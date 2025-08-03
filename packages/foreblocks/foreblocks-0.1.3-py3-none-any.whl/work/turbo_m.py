import logging
import math
import sys
from collections import deque

import gpytorch
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from gpytorch.constraints import Interval
from gpytorch.kernels import MaternKernel, RBFKernel, ScaleKernel, SpectralMixtureKernel
from gpytorch.likelihoods import GaussianLikelihood
from gpytorch.means import ConstantMean
from gpytorch.mlls import ExactMarginalLogLikelihood
from gpytorch.models import ExactGP
from numba import njit


# ============================================================
# Enhanced Feature Extractor for Deep Kernel GP
# ============================================================
class DeepFeatureExtractor(nn.Module):
    def __init__(
        self,
        dim_in,
        hidden_layers=(64, 64),
        dim_out=32,
        activation=nn.ReLU,
        dropout=0.1,
    ):
        super().__init__()
        layers = []
        prev_dim = dim_in
        for h in hidden_layers:
            layers.append(nn.Linear(prev_dim, h))
            layers.append(nn.LayerNorm(h))  # More stable than BatchNorm for GP
            layers.append(activation())
            if dropout > 0:
                layers.append(nn.Dropout(dropout))
            prev_dim = h
        layers.append(nn.Linear(prev_dim, dim_out))
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        x = x.to(dtype=self.net[0].weight.dtype)
        return self.net(x)


# ============================================================
# Standard GP (Matern ν=2.5)
# ============================================================
class GP(ExactGP):
    def __init__(
        self,
        train_x,
        train_y,
        likelihood,
        kernel_type="matern",
        ard_dims=None,
        lengthscale_constraint=None,
        outputscale_constraint=None,
    ):
        super().__init__(train_x, train_y, likelihood)

        # Mean: optionally linear
        self.mean_module = ConstantMean()

        # Base kernel
        if kernel_type == "matern":
            base_kernel = MaternKernel(
                nu=2.5,
                ard_num_dims=ard_dims,
                lengthscale_constraint=lengthscale_constraint,
            )
        elif kernel_type == "rbf":
            base_kernel = RBFKernel(
                ard_num_dims=ard_dims, lengthscale_constraint=lengthscale_constraint
            )
        elif kernel_type == "spectral":
            # Spectral mixture for more flexible priors
            base_kernel = SpectralMixtureKernel(num_mixtures=4, ard_num_dims=ard_dims)
        else:
            raise ValueError(f"Unknown kernel type: {kernel_type}")

        self.covar_module = ScaleKernel(
            base_kernel, outputscale_constraint=outputscale_constraint
        )

    def forward(self, x):
        mean_x = self.mean_module(x)
        covar_x = self.covar_module(x)
        return gpytorch.distributions.MultivariateNormal(mean_x, covar_x)


# ============================================================
# Deep Kernel GP (NN -> Kernel)
# ============================================================
class DeepKernelGP(ExactGP):
    def __init__(
        self,
        train_x,
        train_y,
        likelihood,
        input_dim,
        feature_dim=32,
        kernel_type="matern",
        hidden_layers=(64, 64),
        dropout=0.1,
        lengthscale_constraint=None,
        outputscale_constraint=None,
    ):
        super().__init__(train_x, train_y, likelihood)

        # learnable embedding before kernel
        self.feature_extractor = DeepFeatureExtractor(
            dim_in=input_dim,
            hidden_layers=hidden_layers,
            dim_out=feature_dim,
            activation=nn.ReLU,
            dropout=dropout,
        )

        self.mean_module = ConstantMean()

        # Flexible kernel type
        if kernel_type == "matern":
            base_kernel = MaternKernel(
                nu=2.5,
                ard_num_dims=feature_dim,
                lengthscale_constraint=lengthscale_constraint,
            )
        elif kernel_type == "rbf":
            base_kernel = RBFKernel(
                ard_num_dims=feature_dim, lengthscale_constraint=lengthscale_constraint
            )
        elif kernel_type == "spectral":
            base_kernel = SpectralMixtureKernel(
                num_mixtures=4, ard_num_dims=feature_dim
            )
        else:
            raise ValueError(f"Unknown kernel type: {kernel_type}")

        self.covar_module = ScaleKernel(
            base_kernel, outputscale_constraint=outputscale_constraint
        )

    def forward(self, x):
        z = self.feature_extractor(x)
        mean_z = self.mean_module(z)
        covar_z = self.covar_module(z)
        return gpytorch.distributions.MultivariateNormal(mean_z, covar_z)


# ============================================================
# Smarter Hyperparameter Initialization
# ============================================================
def smart_init_hypers(train_x, train_y, feature_dim=None, is_dkl=False, use_ard=True):
    """
    Robust hyperparameter initialization:
    - Median pairwise distance as lengthscale
    - MAD-based outputscale and noise
    - Matches shape for ARD vs isotropic kernels
    """
    with torch.no_grad():
        dists = torch.cdist(train_x, train_x)
        nonzero = dists[dists > 0]
        median_dist = (
            torch.median(nonzero)
            if nonzero.numel() > 0
            else torch.tensor(0.5, device=train_x.device)
        )
        if not torch.isfinite(median_dist) or median_dist <= 0:
            median_dist = torch.tensor(0.5, device=train_x.device)

    init_lengthscale = torch.clamp(median_dist, 0.01, 5.0).item()

    # Robust noise scale from MAD
    y_mad = torch.median(torch.abs(train_y - torch.median(train_y))) * 1.4826
    init_outputscale = float(torch.clamp(y_mad, 0.05, 20.0))
    init_noise = max(5e-4, min(0.2, 0.01 * init_outputscale))

    # ✅ Shape-aware lengthscale initialization
    if is_dkl and feature_dim is not None:
        # DKL always ARD in feature space
        lengthscale_value = (
            torch.ones(feature_dim, device=train_x.device) * init_lengthscale
        )
    else:
        n_dims = train_x.shape[-1]
        if use_ard:
            # ARD → one lengthscale per dimension
            lengthscale_value = (
                torch.ones(n_dims, device=train_x.device) * init_lengthscale
            )
        else:
            # isotropic → single scalar
            lengthscale_value = torch.tensor([init_lengthscale], device=train_x.device)

    return {
        "covar_module.outputscale": init_outputscale,
        "covar_module.base_kernel.lengthscale": lengthscale_value,
        "likelihood.noise": init_noise,
    }


# ============================================================
# Posterior prediction with gradients
# ============================================================
def gp_predict_with_grad(model, X_test):
    """
    Compute GP posterior mean, variance, and gradients wrt X safely.
    Always returns (mean, var, mean_grad, var_grad).
    """
    X_test = X_test.clone().detach().requires_grad_(True)
    with torch.enable_grad():
        post = model(X_test)
        mean = post.mean
        var = post.variance.clamp_min(1e-12)

        # Try joint gradient computation
        grads = torch.autograd.grad(
            outputs=[mean.sum(), var.sum()],
            inputs=X_test,
            retain_graph=False,
            allow_unused=True,
        )

        # Some outputs may be None → replace with zeros
        mean_grad = grads[0] if grads[0] is not None else torch.zeros_like(X_test)
        var_grad = (
            grads[1]
            if len(grads) > 1 and grads[1] is not None
            else torch.zeros_like(X_test)
        )

    return mean.detach(), var.detach(), mean_grad.detach(), var_grad.detach()


# ============================================================
# Training function (Plain GP or DKL)
# ============================================================
def train_gp(
    train_x,
    train_y,
    use_dkl=True,
    feature_dim=32,
    kernel_type="matern",
    num_steps=100,
    lr=0.05,
    clip_grad=5.0,
    patience=5,
    verbose=False,
    use_ard=True,
    hypers=None,
):
    """
    Train GP or Deep Kernel GP with better stability and dtype consistency.
    """
    if hypers is None:
        hypers = {}

    # Ensure tensors and force consistent dtype/device
    if not torch.is_tensor(train_x):
        train_x = torch.tensor(train_x)
    if not torch.is_tensor(train_y):
        train_y = torch.tensor(train_y)

    # Force float32 unless explicitly handled otherwise
    train_x = train_x.to(dtype=torch.float32)
    train_y = train_y.to(dtype=torch.float32)

    device = train_x.device
    n, d = train_x.shape

    # Constraints
    noise_constraint = Interval(5e-4, 0.2)
    lengthscale_constraint = Interval(0.01, 5.0)
    outputscale_constraint = Interval(0.05, 20.0)

    likelihood = GaussianLikelihood(noise_constraint=noise_constraint).to(device)

    # ARD setup
    ard_dims = d if use_ard else None

    # Model selection
    if use_dkl:
        model = DeepKernelGP(
            train_x,
            train_y,
            likelihood,
            input_dim=d,
            feature_dim=feature_dim,
            kernel_type=kernel_type,
            hidden_layers=(64, 64),
            dropout=0.1,
            lengthscale_constraint=lengthscale_constraint,
            outputscale_constraint=outputscale_constraint,
        )
    else:
        model = GP(
            train_x,
            train_y,
            likelihood,
            kernel_type=kernel_type,
            ard_dims=ard_dims,
            lengthscale_constraint=lengthscale_constraint,
            outputscale_constraint=outputscale_constraint,
        )

    model = model.to(device)

    # Smart hyperparameter initialization
    init_h = smart_init_hypers(
        train_x,
        train_y,
        feature_dim=(feature_dim if use_dkl else None),
        is_dkl=use_dkl,
        use_ard=use_ard,
    )
    model.initialize(**init_h)

    # Load user-defined hypers
    if hypers:
        try:
            model.load_state_dict(hypers, strict=False)
        except RuntimeError:
            pass

    mll = ExactMarginalLogLikelihood(likelihood, model)

    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingWarmRestarts(optimizer, T_0=20)

    model.train()
    likelihood.train()
    best_loss = float("inf")
    no_improve = 0

    for step in range(num_steps):
        optimizer.zero_grad()
        output = model(train_x)
        loss = -mll(output, train_y)

        if not torch.isfinite(loss):
            print(f"❌ Non-finite loss at step {step}")
            break

        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), clip_grad)
        optimizer.step()
        scheduler.step()

        if verbose and step % 10 == 0:
            print(f"[Step {step}/{num_steps}] Loss={loss.item():.4f}")

        if loss.item() + 1e-5 < best_loss:
            best_loss = loss.item()
            no_improve = 0
        else:
            no_improve += 1
            if no_improve >= patience:
                if verbose:
                    print(
                        f"✅ Early stopping after {step+1} steps (patience={patience})"
                    )
                break

    model.eval()
    likelihood.eval()
    return model


##########################################
# Fast vectorized cube projections
##########################################


@njit(fastmath=True, cache=True)
def to_unit_cube(x, lb, ub):
    """Project to [0, 1]^d using vectorized linear scaling."""
    return (x - lb) / (ub - lb)


@njit(fastmath=True, cache=True)
def from_unit_cube(x, lb, ub):
    """Project from [0, 1]^d to original bounds."""
    return x * (ub - lb) + lb


##########################################
# Basic LHS
##########################################


def latin_hypercube_basic(n_pts, dim):
    """Basic Latin hypercube with center perturbation."""
    X = np.zeros((n_pts, dim))
    centers = (1.0 + 2.0 * np.arange(0.0, n_pts)) / (2 * n_pts)
    for i in range(dim):
        X[:, i] = centers[np.random.permutation(n_pts)]
    X += np.random.uniform(-1.0, 1.0, (n_pts, dim)) / (2 * n_pts)
    return X


##########################################
# Maximin LHS
##########################################


def maximin_lhs(n_pts, dim, n_candidates=10):
    """Maximin LHS: pick best LHS among multiple candidates by maximizing min distance."""
    best_X, best_min_dist = None, -np.inf
    for _ in range(n_candidates):
        X = latin_hypercube_basic(n_pts, dim)
        # Pairwise distances
        dists = np.sqrt(((X[:, None, :] - X[None, :, :]) ** 2).sum(axis=2))
        np.fill_diagonal(dists, np.inf)
        min_dist = np.min(dists)
        if min_dist > best_min_dist:
            best_X, best_min_dist = X, min_dist
    return best_X


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===============================================
# Enhanced Numerical Utilities
# ===============================================


class TuRBO:
    """Unified TuRBO algorithm supporting both single (TuRBO-1) and multiple (TuRBO-m) trust regions.

    Parameters
    ----------
    f : function handle
    lb : Lower variable bounds, numpy.array, shape (d,).
    ub : Upper variable bounds, numpy.array, shape (d,).
    n_init : Number of initial points (2*dim is recommended), int.
        For multiple trust regions, this is the number of initial points PER trust region.
    max_evals : Total evaluation budget, int.
    n_trust_regions : Number of trust regions, int. If 1, behaves like TuRBO-1.
    batch_size : Number of points in each batch, int.
    verbose : If you want to print information about the optimization progress, bool.
    use_ard : If you want to use ARD for the GP kernel.
    max_cholesky_size : Largest number of training points where we use Cholesky, int
    n_training_steps : Number of training steps for learning the GP hypers, int
    min_cuda : We use float64 on the CPU if we have this or fewer datapoints
    device : Device to use for GP fitting ("cpu" or "cuda")
    dtype : Dtype to use for GP fitting ("float32" or "float64")

    Example usage:
        # Single trust region (TuRBO-1)
        turbo1 = TuRBO(f=f, lb=lb, ub=ub, n_init=n_init, max_evals=max_evals, n_trust_regions=1)

        # Multiple trust regions (TuRBO-m)
        turbo5 = TuRBO(f=f, lb=lb, ub=ub, n_init=n_init, max_evals=max_evals, n_trust_regions=5)

        turbo1.optimize()  # Run optimization
        X, fX = turbo1.X, turbo1.fX  # Evaluated points
    """

    def __init__(
        self,
        f,
        lb,
        ub,
        n_init,
        max_evals,
        n_trust_regions=1,
        batch_size=1,
        verbose=True,
        use_ard=True,
        max_cholesky_size=2000,
        n_training_steps=50,
        min_cuda=1024,
        device="cpu",
        dtype="float64",
    ):

        # Very basic input checks
        assert lb.ndim == 1 and ub.ndim == 1
        assert len(lb) == len(ub)
        assert np.all(ub > lb)
        assert max_evals > 0 and isinstance(max_evals, int)
        assert n_init > 0 and isinstance(n_init, int)
        assert batch_size > 0 and isinstance(batch_size, int)
        assert n_trust_regions > 0 and isinstance(n_trust_regions, int)
        assert isinstance(verbose, bool) and isinstance(use_ard, bool)
        assert max_cholesky_size >= 0 and isinstance(max_cholesky_size, int)
        assert n_training_steps >= 30 and isinstance(n_training_steps, int)
        assert max_evals > n_init and max_evals > batch_size
        assert device == "cpu" or device == "cuda"
        assert dtype == "float32" or dtype == "float64"
        if device == "cuda":
            assert torch.cuda.is_available(), "can't use cuda if it's not available"

        # Additional checks for multiple trust regions
        if n_trust_regions > 1:
            assert (
                max_evals > n_trust_regions * n_init
            ), "Not enough evaluations for initial points in all trust regions"

        # Save function information
        self.f = f
        self.dim = len(lb)
        self.lb = lb
        self.ub = ub

        # Settings
        self.n_init = n_init
        self.max_evals = max_evals
        self.batch_size = batch_size
        self.n_trust_regions = n_trust_regions
        self.verbose = verbose
        self.use_ard = use_ard
        self.max_cholesky_size = max_cholesky_size
        self.n_training_steps = n_training_steps

        # Hyperparameters
        self.mean = np.zeros((0, 1))
        self.signal_var = np.zeros((0, 1))
        self.noise_var = np.zeros((0, 1))
        self.lengthscales = (
            np.zeros((0, self.dim)) if self.use_ard else np.zeros((0, 1))
        )

        # Tolerances and counters
        self.n_cand = min(100 * self.dim, 5000)
        if n_trust_regions == 1:
            # TuRBO-1 parameters
            self.failtol = np.ceil(np.max([4.0 / batch_size, self.dim / batch_size]))
            self.succtol = 3
        else:
            # TuRBO-m parameters
            self.failtol = max(5, self.dim)
            self.succtol = 3

        self.n_evals = 0

        # Trust region sizes
        self.length_min = 0.5**7
        self.length_max = 1.6
        self.length_init = 0.8

        # Save the full history
        self.X = np.zeros((0, self.dim))
        self.fX = np.zeros((0, 1))

        # Device and dtype for GPyTorch
        self.min_cuda = min_cuda
        self.dtype = torch.float32 if dtype == "float32" else torch.float64
        self.device = torch.device("cuda") if device == "cuda" else torch.device("cpu")
        if self.verbose:
            print("Using dtype = %s \nUsing device = %s" % (self.dtype, self.device))
            sys.stdout.flush()

        # Initialize trust region tracking
        self._idx = np.zeros(
            (0, 1), dtype=int
        )  # Track which trust region proposed each point
        self.hypers = [
            {} for _ in range(self.n_trust_regions)
        ]  # GP hyperparameters for each TR

        # Initialize parameters
        self._restart()

    def _restart(self):
        """Reset trust region parameters."""
        self.failcount = np.zeros(self.n_trust_regions, dtype=int)
        self.succcount = np.zeros(self.n_trust_regions, dtype=int)
        self.length = self.length_init * np.ones(self.n_trust_regions)

    def _adjust_length(self, fX_next, i):
        """Adjust trust region length based on success/failure."""
        assert i >= 0 and i < self.n_trust_regions

        # Get minimum function value for this trust region
        tr_indices = np.where(self._idx[:, 0] == i)[0]
        if len(tr_indices) > 0:
            fX_min = self.fX[tr_indices, 0].min()
        else:
            fX_min = np.inf

        # Check for improvement
        if fX_next.min() < fX_min - 1e-3 * math.fabs(fX_min):
            self.succcount[i] += 1
            self.failcount[i] = 0
        else:
            self.succcount[i] = 0
            if self.n_trust_regions == 1:
                # For single TR, increment by 1 (original TuRBO-1 behavior)
                self.failcount[i] += 1
            else:
                # For multiple TRs, increment by batch size (original TuRBO-m behavior)
                self.failcount[i] += len(fX_next)

        # Adjust trust region size
        if self.succcount[i] == self.succtol:  # Expand trust region
            self.length[i] = min([2.0 * self.length[i], self.length_max])
            self.succcount[i] = 0
        elif self.failcount[i] >= self.failtol:  # Shrink trust region
            self.length[i] /= 2.0
            self.failcount[i] = 0

    def _create_candidates(self, X, fX, length, n_training_steps, hypers):
        """Generate candidates assuming X has been scaled to [0,1]^d."""
        assert X.min() >= 0.0 and X.max() <= 1.0

        # Standardize function values (avoid deepcopy)
        mu, sigma = np.median(fX), fX.std()
        sigma = 1.0 if sigma < 1e-6 else sigma
        fX_norm = (fX - mu) / sigma

        # Determine device once
        device = torch.device("cpu") if len(X) < self.min_cuda else self.device
        dtype = torch.float64 if len(X) < self.min_cuda else self.dtype

        # Pre-allocate tensors to avoid repeated conversions
        X_torch = torch.from_numpy(X).to(device=device, dtype=dtype)
        y_torch = torch.from_numpy(fX_norm).to(device=device, dtype=dtype)

        # Train GP
        with gpytorch.settings.max_cholesky_size(self.max_cholesky_size):
            gp = train_gp(
                train_x=X_torch,
                train_y=y_torch,
                use_ard=self.use_ard,
                num_steps=n_training_steps,
                hypers=hypers,
            )
            hypers = gp.state_dict()

        # Create trust region boundaries (vectorized)
        best_idx = fX_norm.argmin()
        x_center = X[best_idx : best_idx + 1, :]  # Keep as 2D without copy
        weights = gp.covar_module.base_kernel.lengthscale.cpu().detach().numpy().ravel()
        weights = weights / weights.mean()
        weights = weights / np.prod(np.power(weights, 1.0 / len(weights)))

        # Vectorized clipping
        half_width = weights * length * 0.5
        lb = np.clip(x_center - half_width, 0.0, 1.0)
        ub = np.clip(x_center + half_width, 0.0, 1.0)

        # Generate candidate points (reuse sobol if possible)
        # if not hasattr(self, '_sobol_engine'):
        #     self._sobol_engine = SobolEngine(self.dim, scramble=True)

        pert = self._sobol_engine.draw(self.n_cand).to(dtype=dtype, device=device)
        # Direct scaling on GPU/device
        pert = lb + (ub - lb) * pert.cpu().numpy()

        # Vectorized perturbation mask
        prob_perturb = min(20.0 / self.dim, 1.0)
        mask = np.random.rand(self.n_cand, self.dim) <= prob_perturb
        no_perturb = mask.sum(axis=1) == 0
        if no_perturb.any():
            mask[no_perturb, np.random.randint(0, self.dim, size=no_perturb.sum())] = (
                True
            )

        # Create candidates efficiently
        X_cand = np.broadcast_to(x_center, (self.n_cand, self.dim)).copy()
        X_cand[mask] = pert[mask]

        # Single tensor conversion for prediction
        X_cand_torch = torch.from_numpy(X_cand).to(device=device, dtype=dtype)

        # Sample from GP posterior
        with torch.no_grad(), gpytorch.settings.max_cholesky_size(
            self.max_cholesky_size
        ):
            y_cand = (
                gp.likelihood(gp(X_cand_torch))
                .sample(torch.Size([self.batch_size]))
                .t()
                .cpu()
                .numpy()
            )

        # Clean up (let garbage collector handle the rest)
        del X_torch, y_torch, X_cand_torch, gp

        # De-standardize sampled values
        y_cand = mu + sigma * y_cand

        return X_cand, y_cand, hypers

    def _select_candidates(self, X_cand, y_cand):
        """Select the best batch_size candidates across all TRs."""
        assert X_cand.shape == (self.n_trust_regions, self.n_cand, self.dim)
        assert y_cand.shape == (self.n_trust_regions, self.n_cand, self.batch_size)
        assert X_cand.min() >= 0.0 and X_cand.max() <= 1.0
        assert np.all(np.isfinite(y_cand))

        X_next = np.empty((self.batch_size, self.dim))
        idx_next = np.empty((self.batch_size, 1), dtype=int)

        for k in range(self.batch_size):
            # Find best fantasized value for this batch index
            flat_idx = np.argmin(y_cand[:, :, k])
            i, j = divmod(flat_idx, self.n_cand)

            X_next[k] = X_cand[i, j]  # no deepcopy needed
            idx_next[k, 0] = i

            # Mask out so it won't be reused
            y_cand[i, j, :] = np.inf

        return X_next, idx_next

    def optimize(self):
        """Run the full optimization process."""
        # Create initial points for each trust region
        for i in range(self.n_trust_regions):
            X_init = maximin_lhs(self.n_init, self.dim)
            X_init = from_unit_cube(X_init, self.lb, self.ub)
            fX_init = np.array([[self.f(x)] for x in X_init])

            # Update data
            self.X = np.vstack((self.X, X_init))
            self.fX = np.vstack((self.fX, fX_init))
            self._idx = np.vstack((self._idx, i * np.ones((self.n_init, 1), dtype=int)))
            self.n_evals += self.n_init

            if self.verbose:
                fbest = fX_init.min()
                if self.n_trust_regions == 1:
                    print(f"Starting from fbest = {fbest:.4}")
                else:
                    print(f"TR-{i} starting from: {fbest:.4}")
                sys.stdout.flush()

        # Pre-allocate arrays for candidate generation
        X_cand = np.zeros((self.n_trust_regions, self.n_cand, self.dim))
        y_cand = np.full((self.n_trust_regions, self.n_cand, self.batch_size), np.inf)

        # Main optimization loop
        while self.n_evals < self.max_evals:
            # Reset candidate arrays (faster than recreating)
            y_cand.fill(np.inf)

            # Generate candidates from each trust region
            for i in range(self.n_trust_regions):
                # Get data for this trust region (avoid deepcopy)
                tr_mask = self._idx[:, 0] == i
                if not tr_mask.any():
                    continue

                X_tr = self.X[tr_mask, :]
                X_tr = to_unit_cube(X_tr, self.lb, self.ub)
                fX_tr = self.fX[tr_mask, 0]

                # Skip retraining if hyperparameters exist and data hasn't changed
                n_training_steps = 0 if self.hypers[i] else self.n_training_steps

                # Generate candidates
                X_cand[i, :, :], y_cand[i, :, :], self.hypers[i] = (
                    self._create_candidates(
                        X_tr,
                        fX_tr,
                        length=self.length[i],
                        n_training_steps=n_training_steps,
                        hypers=self.hypers[i],
                    )
                )

            # Select best candidates
            X_next, idx_next = self._select_candidates(X_cand, y_cand)

            # Convert back to original space
            X_next = from_unit_cube(X_next, self.lb, self.ub)

            # Evaluate candidates
            fX_next = np.array([[self.f(x)] for x in X_next])

            # Update trust regions
            for i in range(self.n_trust_regions):
                idx_i = idx_next[:, 0] == i
                if idx_i.any():
                    self.hypers[i] = {}  # Clear hyperparameters to force retraining
                    fX_i = fX_next[idx_i]

                    # Print progress for improvements
                    if self.verbose and fX_i.min() < self.fX.min() - 1e-3 * math.fabs(
                        self.fX.min()
                    ):
                        if self.n_trust_regions == 1:
                            print(
                                f"{self.n_evals + len(fX_next)}) New best: {fX_i.min():.4}"
                            )
                        else:
                            print(
                                f"{self.n_evals + len(fX_next)}) New best @ TR-{i}: {fX_i.min():.4}"
                            )
                        sys.stdout.flush()

                    self._adjust_length(fX_i, i)

            # Update global data
            self.n_evals += len(fX_next)
            self.X = np.vstack((self.X, X_next))
            self.fX = np.vstack((self.fX, fX_next))
            self._idx = np.vstack((self._idx, idx_next))

            # Handle trust region restarts
            for i in range(self.n_trust_regions):
                if self.length[i] < self.length_min:
                    # Mark old points as inactive
                    tr_indices = self._idx[:, 0] == i

                    if self.verbose:
                        old_best = self.fX[tr_indices, 0].min()
                        if self.n_trust_regions == 1:
                            print(
                                f"{self.n_evals}) Restarting with fbest = {old_best:.4}"
                            )
                        else:
                            print(f"{self.n_evals}) TR-{i} converged to: {old_best:.4}")
                        sys.stdout.flush()

                    # Reset trust region
                    self.length[i] = self.length_init
                    self.succcount[i] = 0
                    self.failcount[i] = 0
                    self._idx[tr_indices, 0] = -1  # Mark as inactive
                    self.hypers[i] = {}

                    # Create new initial design
                    X_init = maximin_lhs(self.n_init, self.dim)
                    X_init = from_unit_cube(X_init, self.lb, self.ub)
                    fX_init = np.array([[self.f(x)] for x in X_init])

                    if self.verbose:
                        new_best = fX_init.min()
                        if self.n_trust_regions == 1:
                            print(f"Starting from fbest = {new_best:.4}")
                        else:
                            print(
                                f"{self.n_evals + self.n_init}) TR-{i} restarting from: {new_best:.4}"
                            )
                        sys.stdout.flush()

                    # Add new data
                    self.X = np.vstack((self.X, X_init))
                    self.fX = np.vstack((self.fX, fX_init))
                    self._idx = np.vstack(
                        (self._idx, i * np.ones((self.n_init, 1), dtype=int))
                    )
                    self.n_evals += self.n_init


# Backwards compatibility aliases
class Turbo1(TuRBO):
    """Backwards compatibility alias for TuRBO with single trust region."""

    def __init__(self, *args, **kwargs):
        # Force single trust region
        kwargs["n_trust_regions"] = 1
        super().__init__(*args, **kwargs)


class TurboM(TuRBO):
    """Backwards compatibility alias for TuRBO with multiple trust regions."""

    def __init__(self, f, lb, ub, n_init, max_evals, n_trust_regions, *args, **kwargs):
        super().__init__(f, lb, ub, n_init, max_evals, n_trust_regions, *args, **kwargs)


class MetaAcquisitionMLP(nn.Module):
    """
    Improved MLP for learning acquisition function combinations with context-awareness.
    Includes residuals, normalization, temperature scaling, and better initialization.
    """

    def __init__(
        self,
        n_components=6,
        context_dim=4,
        hidden_dim=64,
        activation="silu",
        dropout=0.1,
        temperature=1.0,
    ):
        super().__init__()
        self.n_components = n_components
        self.temperature = temperature

        act_fn = {"relu": nn.ReLU(), "silu": nn.SiLU(), "gelu": nn.GELU()}[activation]

        self.context_net = nn.Sequential(
            nn.Linear(context_dim, hidden_dim),
            act_fn,
            nn.LayerNorm(hidden_dim),
            nn.Dropout(dropout),
        )

        self.component_net = nn.Sequential(
            nn.Linear(n_components, hidden_dim),
            act_fn,
            nn.LayerNorm(hidden_dim),
            nn.Dropout(dropout),
        )

        self.fusion = nn.Sequential(
            nn.Linear(2 * hidden_dim, hidden_dim),
            act_fn,
            nn.LayerNorm(hidden_dim),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, n_components),
        )

        self._init_weights()

    def _init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                nn.init.constant_(m.bias, 0.0)

    def forward(self, components, context):
        """
        Args:
            components: [B, n_components] acquisition values
            context:    [B, context_dim]   optimization metadata
        Returns:
            weights:    [B, n_components] softmaxed combination weights
        """
        h_comp = self.component_net(components)
        h_ctx = self.context_net(context)
        fused = torch.cat([h_comp, h_ctx], dim=-1)
        logits = self.fusion(fused) / self.temperature
        return F.softmax(logits, dim=-1)


class AcquisitionBandit:
    def __init__(self, n_components=6, context_dim=4, memory_size=500):
        self.n_components = n_components
        self.context_dim = context_dim
        self.memory = deque(maxlen=memory_size)

        self.component_counts = np.ones(n_components)
        self.component_rewards = np.zeros(n_components)
        self.exploration_bonus = 0.1

        # Rolling improvement stats
        self.improvements = deque(maxlen=memory_size)

    def _normalize_improvement(self, improvement):
        if len(self.improvements) > 10:
            mean = np.mean(self.improvements)
            std = np.std(self.improvements) + 1e-8
            return np.clip((improvement - mean) / std, -2, 2)
        return improvement

    def get_ucb_weights(self, total_pulls):
        if total_pulls < 10:
            return np.ones(self.n_components) / self.n_components

        avg_rewards = self.component_rewards / (self.component_counts + 1e-8)
        confidence = np.sqrt(2 * np.log(total_pulls) / (self.component_counts + 1e-8))
        ucb_values = avg_rewards + self.exploration_bonus * confidence

        # Softmax for smooth component selection
        exp_vals = np.exp(ucb_values - ucb_values.max())
        return exp_vals / exp_vals.sum()

    def update_rewards(self, selected_components, improvements):
        for comp_idx, improvement in zip(selected_components, improvements):
            if comp_idx < self.n_components:
                norm_impr = self._normalize_improvement(improvement)
                reward = np.tanh(norm_impr)

                self.component_counts[comp_idx] += 1
                self.component_rewards[comp_idx] += reward
                self.improvements.append(improvement)
                self.memory.append((comp_idx, reward))


class MetaTrustRegionMLP(nn.Module):
    """
    Learns a low-rank ellipsoidal trust region shape matrix from context.
    Outputs a positive semi-definite metric: L @ L^T.
    """

    def __init__(self, context_dim, dim, rank=4, hidden_dim=32):
        super().__init__()
        self.context_dim = context_dim
        self.dim = dim
        self.rank = rank

        self.encoder = nn.Sequential(
            nn.Linear(context_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, dim * rank),  # Outputs L ∈ R^{dim × rank}
        )

    def forward(self, context):
        """
        Args:
            context: [batch_size, context_dim]
        Returns:
            metric: [batch_size, dim, dim] positive semi-definite matrices
        """
        B = context.shape[0]
        L = self.encoder(context).view(B, self.dim, self.rank)
        M = torch.bmm(L, L.transpose(1, 2))  # PSD matrix: L @ L^T
        trace = M.diagonal(dim1=1, dim2=2).sum(-1, keepdim=True).clamp(min=1e-6)
        M = M / trace.view(-1, 1, 1) * self.dim  # Normalize trace
        return M


# trust_region_rl_controller.py
import numpy as np
import torch
import torch.nn as nn


class TrustRegionRLController(nn.Module):
    def __init__(self, obs_dim, action_dim, hidden_dim=64):
        super().__init__()
        self.policy = nn.Sequential(
            nn.Linear(obs_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, action_dim)  # Output: merge_thresh, spawn_count
        )
        self.softmax = nn.Softmax(dim=-1)

    def forward(self, obs):
        logits = self.policy(obs)
        return logits

    def select_action(self, obs: np.ndarray, epsilon=0.0):
        obs_tensor = torch.from_numpy(obs).float().unsqueeze(0)  # [1, obs_dim]
        with torch.no_grad():
            logits = self(obs_tensor)[0]
        if np.random.rand() < epsilon:
            return {
                "merge_eps": np.random.uniform(0.05, 0.4),
                "n_spawn": np.random.randint(0, 5)
            }
        merge_eps = float(torch.sigmoid(logits[0]) * 0.4)  # Map [0, 1] → [0, 0.4]
        n_spawn = int(torch.clamp(torch.round(torch.sigmoid(logits[1]) * 4), 0, 4))
        return {
            "merge_eps": merge_eps,
            "n_spawn": n_spawn
        }
import torch
import torch.nn as nn
from torch.distributions import Normal


class TRPolicy(nn.Module):
    def __init__(self, obs_dim, action_std=0.2):
        super().__init__()
        self.actor = nn.Sequential(
            nn.Linear(obs_dim, 64),
            nn.Tanh(),
            nn.Linear(64, 64),
            nn.Tanh()
        )
        self.mu_head = nn.Linear(64, 2)  # merge_eps, n_spawn
        self.log_std = nn.Parameter(torch.ones(2) * torch.log(torch.tensor(action_std)))

        self.critic = nn.Sequential(
            nn.Linear(obs_dim, 64),
            nn.Tanh(),
            nn.Linear(64, 64),
            nn.Tanh(),
            nn.Linear(64, 1)
        )

    def forward(self, obs):
        features = self.actor(obs)
        mu = self.mu_head(features)
        std = self.log_std.exp().expand_as(mu)
        dist = Normal(mu, std)
        value = self.critic(obs)
        return dist, value.squeeze(-1)

class RolloutBuffer:
    def __init__(self):
        self.obs = []
        self.actions = []
        self.logprobs = []
        self.rewards = []
        self.values = []
        self.dones = []

    def clear(self):
        self.__init__()

class PPOTrainer:
    def __init__(self, policy, lr=3e-4, gamma=0.99, lam=0.95, clip_eps=0.2):
        self.policy = policy
        self.optimizer = torch.optim.Adam(policy.parameters(), lr=lr)
        self.gamma = gamma
        self.lam = lam
        self.clip_eps = clip_eps

    def train(self, buffer, batch_size=32, epochs=10):
        obs = torch.tensor(buffer.obs, dtype=torch.float32)
        actions = torch.tensor(buffer.actions, dtype=torch.float32)
        logprobs_old = torch.tensor(buffer.logprobs, dtype=torch.float32)
        rewards = buffer.rewards
        values = torch.tensor(buffer.values, dtype=torch.float32)
        dones = buffer.dones

        # Compute GAE
        returns, advantages = [], []
        gae = 0
        next_value = 0
        for t in reversed(range(len(rewards))):
            delta = rewards[t] + self.gamma * next_value * (1 - dones[t]) - values[t]
            gae = delta + self.gamma * self.lam * (1 - dones[t]) * gae
            advantages.insert(0, gae)
            next_value = values[t]
        advantages = torch.tensor(advantages, dtype=torch.float32)
        returns = advantages + values

        for _ in range(epochs):
            for i in range(0, len(obs), batch_size):
                batch_idx = slice(i, i + batch_size)
                dist, value = self.policy(obs[batch_idx])
                new_logprob = dist.log_prob(actions[batch_idx]).sum(-1)
                ratio = (new_logprob - logprobs_old[batch_idx]).exp()
                surr1 = ratio * advantages[batch_idx]
                surr2 = torch.clamp(ratio, 1 - self.clip_eps, 1 + self.clip_eps) * advantages[batch_idx]
                actor_loss = -torch.min(surr1, surr2).mean()
                critic_loss = nn.functional.mse_loss(value, returns[batch_idx])
                loss = actor_loss + 0.5 * critic_loss

                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()


class TuRBOMPP(TuRBO):
    def __init__(
        self,
        *args,
        spawn_entropy_threshold=0.6,
        merge_dist_threshold=0.15,
        max_regions=16,
        min_eval_between_spawns=50,
        max_global_gp_points=2000,
        adaptive_thresholds=True,
        # SOTA features
        use_lipschitz_adaptation=True,
        use_pareto_spawning=True,
        use_gradient_information=True,
        uncertainty_decay_rate=0.95,
        diversity_bonus_weight=0.1,
        multi_fidelity_ratio=0.3,
        # Meta-acquisition learning
        use_meta_acquisition=True,
        meta_acquisition_warmup=50,
        meta_learning_rate=0.001,
        use_meta_trust_region=True,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        # Core parameters
        self.spawn_entropy_threshold = spawn_entropy_threshold
        self.merge_dist_threshold = merge_dist_threshold
        self.max_regions = max_regions
        self.min_eval_between_spawns = min_eval_between_spawns
        self.max_global_gp_points = max_global_gp_points
        self.adaptive_thresholds = adaptive_thresholds

        # SOTA features
        self.use_lipschitz_adaptation = use_lipschitz_adaptation
        self.use_pareto_spawning = use_pareto_spawning
        self.use_gradient_information = use_gradient_information
        self.uncertainty_decay_rate = uncertainty_decay_rate
        self.diversity_bonus_weight = diversity_bonus_weight
        self.multi_fidelity_ratio = multi_fidelity_ratio

        # Meta-acquisition learning
        self.use_meta_acquisition = use_meta_acquisition
        self.meta_acquisition_warmup = meta_acquisition_warmup
        self.meta_learning_rate = meta_learning_rate

        self.use_meta_trust_region = use_meta_trust_region

        # Enhanced state tracking
        self._init_state()

        # Performance caches
        self._init_caches()

        # Meta-acquisition components
        if self.use_meta_acquisition:
            self._init_meta_acquisition()

        if self.use_meta_trust_region:
            self.meta_trust_region_mlp = MetaTrustRegionMLP(
                context_dim=4,  # same as your optimization context
                dim=self.dim,
                rank=4,
                hidden_dim=32,
            ).to(self.device)

        obs_dim = 7  # [n_regions, dynamic_cap, q_mean, q_std, l_mean, l_std, entropy]
        action_dim = 2  # merge_eps (continuous), n_spawn (discrete)

        self.rl_obs_dim = 8  # or however many in _compute_rl_observation
        self._ppo_buffer = RolloutBuffer()
        self.rl_agent = TRPolicy(obs_dim=self.rl_obs_dim)
        self.ppo_trainer = PPOTrainer(self.rl_agent)

        self.best_global_value = np.inf
        self.prev_best_global = np.inf
        self.global_step = 0
        self.train_interval = 5

    def _init_state(self):
        """Initialize enhanced state tracking."""
        self.last_spawn_eval = 0
        self.spawn_history = []
        self.tr_centers = np.zeros((self.max_regions, self.dim))
        self.tr_quality_scores = np.ones(self.max_regions)
        self.tr_lipschitz_constants = np.ones(self.max_regions)
        self.tr_uncertainty_history = [[] for _ in range(self.max_regions)]

        # Adaptive thresholds
        self.base_entropy_threshold = self.spawn_entropy_threshold
        self.base_merge_threshold = self.merge_dist_threshold

    def _init_caches(self):
        """Initialize performance caches."""
        self._gp_cache = {}
        self._acquisition_cache = {}
        self._cached_global_gp = None
        self._cache_valid_until = 0
        self._sobol_engine = torch.quasirandom.SobolEngine(self.dim, scramble=True)

    def _init_meta_acquisition(self):
        """Initialize meta-acquisition learning components."""
        self.n_acq_components = 6  # EI, UCB, PI, Entropy, Gradient, Thompson
        self.context_dim = 4  # progress, region_quality, lipschitz, diversity

        # Meta-acquisition MLP
        self.meta_acq_mlp = MetaAcquisitionMLP(
            n_components=self.n_acq_components,
            context_dim=self.context_dim,
            hidden_dim=32,
        ).to(device=self.device, dtype=self.dtype)

        # Optimizer for online learning
        self.meta_optimizer = optim.Adam(
            self.meta_acq_mlp.parameters(), lr=self.meta_learning_rate
        )

        # Contextual bandit for tracking performance
        self.acq_bandit = AcquisitionBandit(
            n_components=self.n_acq_components, context_dim=self.context_dim
        )

        # Training data collection
        self.meta_training_data = []
        self.last_selected_components = []
        self.last_improvements = []

    # ===============================================
    # Enhanced GP Management with Intelligent Caching
    # ===============================================

    def _get_cached_gp(self, X, y, cache_key_suffix=""):
        """Get or train GP with intelligent caching."""
        # Create stable cache key
        X_hash = (
            hash(X.detach().cpu().numpy().tobytes())
            if torch.is_tensor(X)
            else hash(X.tobytes())
        )
        y_hash = (
            hash(y.detach().cpu().numpy().tobytes())
            if torch.is_tensor(y)
            else hash(y.tobytes())
        )
        cache_key = f"{X_hash}_{y_hash}_{cache_key_suffix}"

        if cache_key in self._gp_cache:
            return self._gp_cache[cache_key]

        # Train new GP
        gp_model = train_gp(
            train_x=(
                X
                if torch.is_tensor(X)
                else torch.tensor(X, dtype=self.dtype, device=self.device)
            ),
            train_y=(
                y
                if torch.is_tensor(y)
                else torch.tensor(y, dtype=self.dtype, device=self.device)
            ),
            use_ard=self.use_ard,
            num_steps=min(100, max(10, len(X) // 5)),
        )

        # Cache management (keep only 10 most recent)
        if len(self._gp_cache) >= 10:
            oldest_key = next(iter(self._gp_cache))
            del self._gp_cache[oldest_key]

        self._gp_cache[cache_key] = gp_model
        return gp_model

    # ===============================================
    # Enhanced Multi-Acquisition with Caching
    # ===============================================

    def _compute_acquisition_components(
        self, mean, var, progress, gp_model=None, candidates=None
    ):
        """Compute individual acquisition function components."""
        std = np.sqrt(var + 1e-12)
        f_min = mean.min()
        z = (f_min - mean) / (std + 1e-9)

        components = np.zeros((len(mean), self.n_acq_components))

        # 1. Expected Improvement (normalized)
        ei = (f_min - mean) * 0.5 * (1 + np.tanh(z / np.sqrt(2))) + std * np.exp(
            -0.5 * z**2
        ) / np.sqrt(2 * np.pi)
        components[:, 0] = ei / (ei.max() + 1e-9)

        # 2. Upper Confidence Bound (adaptive β)
        beta = 2.0 * np.log(
            2 * self.n_evals * np.pi**2 / (6 * 0.05)
        )  # High-confidence UCB
        ucb = mean + np.sqrt(beta) * std
        components[:, 1] = (ucb - ucb.min()) / (ucb.ptp() + 1e-9)

        # 3. Probability of Improvement
        pi = 0.5 * (1 + np.tanh(z / np.sqrt(2)))
        components[:, 2] = pi

        # 4. Entropy (exploration)
        entropy = 0.5 * np.log(2 * np.pi * np.e * var)
        components[:, 3] = (entropy - entropy.min()) / (entropy.ptp() + 1e-9)

        # 5. Gradient-based (if available)
        if (
            self.use_gradient_information
            and gp_model is not None
            and candidates is not None
        ):
            try:
                X_torch = torch.tensor(
                    candidates, dtype=self.dtype, device=self.device, requires_grad=True
                )
                _, _, mean_grad, _ = gp_predict_with_grad(gp_model, X_torch)
                grad_norm = torch.norm(mean_grad, dim=-1).cpu().numpy()
                components[:, 4] = grad_norm / (grad_norm.max() + 1e-9)
            except:
                components[:, 4] = 0.5  # Neutral value if gradient fails
        else:
            components[:, 4] = 0.5

        # 6. Thompson Sampling
        ts_sample = mean + std * np.random.randn(*mean.shape)
        components[:, 5] = (ts_sample - ts_sample.min()) / (ts_sample.ptp() + 1e-9)

        return components

    def _get_optimization_context(self, region_id=None):
        """Get current optimization context for meta-learning."""
        progress = min(1.0, self.n_evals / self.max_evals)

        if region_id is not None and region_id < len(self.tr_quality_scores):
            region_quality = self.tr_quality_scores[region_id]
            lipschitz = self.tr_lipschitz_constants[region_id]
        else:
            region_quality = (
                np.mean(self.tr_quality_scores[: self.n_trust_regions])
                if self.n_trust_regions > 0
                else 1.0
            )
            lipschitz = (
                np.mean(self.tr_lipschitz_constants[: self.n_trust_regions])
                if self.n_trust_regions > 0
                else 1.0
            )

        # Diversity measure based on trust region spread
        if self.n_trust_regions > 1:
            centers = to_unit_cube(
                self.tr_centers[: self.n_trust_regions], self.lb, self.ub
            )
            distances = np.linalg.norm(centers[:, None] - centers[None], axis=2)
            diversity = np.mean(distances[np.triu_indices(len(centers), k=1)])
        else:
            diversity = 0.5

        return np.array([progress, region_quality, lipschitz, diversity])

    def _compute_meta_acquisition(
        self, mean, var, progress, gp_model=None, candidates=None, region_id=None
    ):
        """Compute meta-learned acquisition function."""
        # Get acquisition components
        components = self._compute_acquisition_components(
            mean, var, progress, gp_model, candidates
        )
        context = self._get_optimization_context(region_id)

        # Use bandit or MLP depending on warmup phase
        if self.n_evals < self.meta_acquisition_warmup or not self.use_meta_acquisition:
            # Fallback to UCB-based component selection during warmup
            weights = self.acq_bandit.get_ucb_weights(self.n_evals)
            if self.verbose and self.n_evals % 100 == 0:
                print(f"[META-ACQ] Warmup phase, using bandit weights: {weights}")
        else:
            # Use learned MLP
            try:
                with torch.no_grad():
                    components_torch = torch.tensor(
                        components, dtype=self.dtype, device=self.device
                    )
                    context_torch = torch.tensor(
                        context, dtype=self.dtype, device=self.device
                    ).expand(len(components), -1)

                    weights_torch = self.meta_acq_mlp(components_torch, context_torch)
                    weights = (
                        weights_torch.mean(dim=0).cpu().numpy()
                    )  # Average across candidates

                    if self.verbose and self.n_evals % 200 == 0:
                        print(f"[META-ACQ] MLP weights: {weights}")

            except Exception as e:
                if self.verbose:
                    print(f"[META-ACQ] MLP failed, using bandit: {e}")
                weights = self.acq_bandit.get_ucb_weights(self.n_evals)

        # Compute weighted acquisition
        weighted_acq = np.sum(components * weights[None, :], axis=1)

        # Store for learning
        if len(self.last_selected_components) > 0:
            # Update bandit with previous performance
            self.acq_bandit.update_rewards(
                self.last_selected_components, self.last_improvements
            )

        # Track current selection for next update
        best_component = np.argmax(weights)
        self.last_selected_components = [best_component] * len(components)

        return weighted_acq, components, weights

    def _update_meta_acquisition(self, improvements):
        """Update meta-acquisition learning based on observed improvements."""
        if not self.use_meta_acquisition or self.n_evals < self.meta_acquisition_warmup:
            return

        self.last_improvements = improvements

        # Update training data with actual improvements
        if len(self.meta_training_data) > 0:
            # Add improvements to the most recent training data
            recent_data = self.meta_training_data[-1]
            recent_data["improvements"] = np.array(
                improvements
            )  # Store as 'improvements'

            # Train MLP on collected data
            self._train_meta_mlp()

        # Update bandit
        if len(self.last_selected_components) > 0:
            self.acq_bandit.update_rewards(self.last_selected_components, improvements)

    def _train_meta_mlp(self):
        """Train meta-acquisition MLP on collected data."""
        if len(self.meta_training_data) < 10:
            return

        try:
            # Sample recent training data that has improvements
            valid_data = [
                d for d in self.meta_training_data[-50:] if "improvements" in d
            ]

            if len(valid_data) < 5:
                return

            components_list = []
            contexts_list = []
            targets_list = []

            for data in valid_data:
                components_list.append(data["components"])
                contexts_list.append(data["context"])
                # Use the stored improvements
                improvements = data["improvements"]
                # Convert to per-candidate targets
                n_candidates = len(data["components"])
                target_per_candidate = np.full(n_candidates, np.mean(improvements))
                targets_list.append(target_per_candidate)

            if len(components_list) == 0:
                return

            # Prepare tensors
            components_tensor = torch.tensor(
                np.vstack(components_list), dtype=self.dtype, device=self.device
            )
            contexts_tensor = torch.tensor(
                np.vstack(contexts_list), dtype=self.dtype, device=self.device
            )
            targets_tensor = torch.tensor(
                np.concatenate(targets_list), dtype=self.dtype, device=self.device
            )

            # Normalize targets to [-1, 1] range
            if targets_tensor.std() > 1e-8:
                targets_tensor = torch.tanh(targets_tensor * 10)

            # Training step
            self.meta_optimizer.zero_grad()

            # Forward pass
            weights = self.meta_acq_mlp(components_tensor, contexts_tensor)
            predicted_acq = torch.sum(components_tensor * weights, dim=1)

            # Loss: encourage weights that led to better improvements
            loss = -torch.mean(predicted_acq * targets_tensor)  # Maximize correlation
            entropy = -torch.sum(weights * torch.log(weights + 1e-9), dim=1).mean()
            loss = loss - 0.01 * entropy

            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.meta_acq_mlp.parameters(), 1.0)
            self.meta_optimizer.step()

            if self.verbose and self.n_evals % 200 == 0:
                print(
                    f"[META-ACQ] MLP trained, loss: {loss.item():.4f}, "
                    f"samples: {len(valid_data)}"
                )

        except Exception as e:
            if self.verbose:
                print(f"[META-ACQ] Training failed: {str(e)[:50]}...")

    def _create_candidates(
        self, X_unit, fX, length, n_training_steps, hypers, region_id=None
    ):
        """Streamlined candidate generation with SOTA features."""
        N, dim = X_unit.shape

        # Normalize targets
        f_std = (fX - fX.mean()) / (fX.std() + 1e-8)

        # Train/get cached GP
        cache_suffix = f"reg_{region_id}_{n_training_steps}"
        gp_model = self._get_cached_gp(X_unit, f_std, cache_suffix)

        # Trust region center
        center = X_unit[fX.argmin()][None]
        if len(self.X) > 0:
            global_best_unit = to_unit_cube(
                self.X[self.fX.argmin()][None], self.lb, self.ub
            )
            center = 0.8 * center + 0.2 * global_best_unit

        # Enhanced ellipsoid shaping
        # hessian_metric = self._estimate_hessian_metric(X_unit - center, f_std)

        # GP lengthscale metric
        try:
            if hasattr(gp_model.covar_module.base_kernel, "lengthscale"):
                ls = (
                    gp_model.covar_module.base_kernel.lengthscale.detach()
                    .cpu()
                    .numpy()
                    .flatten()
                )
                ls = np.pad(ls, (0, max(0, dim - len(ls))), constant_values=ls.mean())[
                    :dim
                ]
                gp_metric = np.diag(1.0 / (ls + 1e-6))
                gp_metric /= np.trace(gp_metric) / dim  # normalize
            else:
                gp_metric = np.eye(dim)
        except:
            gp_metric = np.eye(dim)

        # Adaptive blending
        # maturity = min(1.0, N / max(15, dim + 5))
        # alpha = 0.3 * (1 - maturity) + 0.8 * maturity
        # ellipsoid_metric = (1 - alpha) * hessian_metric + alpha * gp_metric
        context = (
            torch.tensor(self._get_optimization_context(region_id), device=self.device)
            .unsqueeze(0)
            .to(dtype=self.meta_trust_region_mlp.encoder[0].weight.dtype)
        )

        M = self.meta_trust_region_mlp(context)[0].detach().cpu().numpy()  # [dim, dim]
        ellipsoid_metric = M  # learned PSD matrix
        # Efficient candidate sampling
        n_candidates = self.n_cand * 3
        raw_samples = self._sobol_engine.draw(n_candidates).cpu().numpy() - 0.5

        # Normalize to unit sphere
        norms = np.linalg.norm(raw_samples, axis=1, keepdims=True)
        norms[norms < 1e-12] = 1.0
        unit_samples = raw_samples / norms

        # Transform and clip
        candidates = center + length * 0.5 * unit_samples @ ellipsoid_metric.T
        candidates = np.clip(candidates, 0.0, 1.0)

        # GP evaluation
        with torch.no_grad():
            gp_model.eval()
            X_torch = torch.tensor(candidates, dtype=self.dtype, device=self.device)
            posterior = gp_model(X_torch)
            mean = posterior.mean.cpu().numpy()
            var = posterior.variance.cpu().numpy()

        # Enhanced acquisition function with meta-learning
        progress = min(1.0, self.n_evals / self.max_evals)

        if self.use_meta_acquisition:
            acq_scores, components, weights = self._compute_meta_acquisition(
                mean,
                var,
                progress,
                gp_model=gp_model if self.use_gradient_information else None,
                candidates=candidates if self.use_gradient_information else None,
                region_id=region_id,
            )

            # Store training data for meta-learning
            context = self._get_optimization_context(region_id)
            self.meta_training_data.append(
                {
                    "components": components,
                    "context": context[None, :].repeat(len(components), axis=0),
                    "weights": weights,
                    "n_evals": self.n_evals,
                    # Note: 'improvements' will be added later in _update_meta_acquisition
                }
            )

            # Keep only recent data
            if len(self.meta_training_data) > 100:
                self.meta_training_data = self.meta_training_data[-100:]

        else:
            # Fallback to traditional blended acquisition
            acq_scores = self._compute_traditional_acquisition(
                mean, var, progress, gp_model, candidates
            )

        # Diversity-aware selection
        diversity_scores = self._compute_diversity_scores(candidates, var)
        final_scores = acq_scores + self.diversity_bonus_weight * diversity_scores

        # Select top candidates
        top_indices = np.argsort(-final_scores)[: self.n_cand]
        selected_candidates = candidates[top_indices]

        # Generate fantasies
        with torch.no_grad():
            X_selected = torch.tensor(
                selected_candidates, dtype=self.dtype, device=self.device
            )
            posterior_selected = gp_model(X_selected)
            fantasies = (
                posterior_selected.sample(torch.Size([self.batch_size]))
                .t()
                .cpu()
                .numpy()
            )

            # Denormalize
            fantasies = fX.mean() + (fX.std() + 1e-8) * fantasies

        return selected_candidates, fantasies, gp_model.state_dict()

    def _compute_traditional_acquisition(
        self, mean, var, progress, gp_model=None, candidates=None
    ):
        """Traditional blended acquisition as fallback."""
        std = np.sqrt(var + 1e-12)

        # Dynamic weights based on optimization progress
        if progress < 0.3:
            w_explore, w_exploit = 0.7, 0.3
        elif progress < 0.7:
            w_explore, w_exploit = 0.5, 0.5
        else:
            w_explore, w_exploit = 0.3, 0.7

        # Efficient acquisition computation
        std_norm = std / (std.max() + 1e-9)

        # Expected improvement
        f_min = mean.min()
        z = (f_min - mean) / (std + 1e-9)
        ei = (f_min - mean) * 0.5 * (1 + np.tanh(z / np.sqrt(2))) + std * np.exp(
            -0.5 * z**2
        ) / np.sqrt(2 * np.pi)
        ei_norm = ei / (ei.max() + 1e-9)

        # Base blended acquisition
        acq = w_explore * std_norm + w_exploit * ei_norm

        # Gradient enhancement if available
        if (
            self.use_gradient_information
            and gp_model is not None
            and candidates is not None
        ):
            try:
                X_torch = torch.tensor(
                    candidates, dtype=self.dtype, device=self.device, requires_grad=True
                )
                _, _, mean_grad, var_grad = gp_predict_with_grad(gp_model, X_torch)

                grad_norm = torch.norm(mean_grad, dim=-1).cpu().numpy()
                grad_norm_scaled = grad_norm / (grad_norm.max() + 1e-9)
                gradient_bonus = 0.1 * grad_norm_scaled * std_norm * (1 - progress)
                acq += gradient_bonus
            except:
                pass

        return acq

    def _compute_diversity_scores(self, candidates, var):
        """Efficient diversity scoring."""
        n_candidates = len(candidates)
        if n_candidates < 10:
            return np.ones(n_candidates) * 0.5

        # Select high-variance subset for diversity computation
        k_diverse = min(n_candidates, 100)
        high_var_idx = np.argsort(-var)[:k_diverse]
        diverse_candidates = candidates[high_var_idx]

        # Compute pairwise distances efficiently
        dist_matrix = np.linalg.norm(
            diverse_candidates[:, None] - diverse_candidates[None], axis=2
        )

        # Diversity score as mean distance to others
        diversity_subset = dist_matrix.mean(axis=1)

        # Map back to all candidates
        diversity_scores = np.ones(n_candidates) * diversity_subset.mean()
        diversity_scores[high_var_idx] = diversity_subset

        return diversity_scores / (diversity_scores.max() + 1e-9)

    # ===============================================
    # Enhanced Lipschitz Adaptation
    # ===============================================

    def _update_lipschitz_constants(self):
        """Update Lipschitz constants for adaptive trust region scaling."""
        if not self.use_lipschitz_adaptation:
            return

        for i in range(self.n_trust_regions):
            tr_mask = self._idx[:, 0] == i
            if not tr_mask.any() or tr_mask.sum() < 3:
                continue

            X_tr = self.X[tr_mask]
            fX_tr = self.fX[tr_mask, 0]

            # Efficient Lipschitz estimation via GP gradients
            try:
                X_unit = to_unit_cube(X_tr, self.lb, self.ub)
                f_std = (fX_tr - fX_tr.mean()) / (fX_tr.std() + 1e-8)

                gp_local = self._get_cached_gp(X_unit, f_std, f"lipschitz_{i}")

                # Sample points for gradient estimation
                n_probe = min(20, len(X_tr))
                probe_points = torch.tensor(
                    X_unit[:n_probe],
                    dtype=self.dtype,
                    device=self.device,
                    requires_grad=True,
                )

                mean_pred = gp_local(probe_points).mean.sum()
                grad = torch.autograd.grad(mean_pred, probe_points, create_graph=False)[
                    0
                ]
                grad_norms = torch.norm(grad, dim=1)

                lipschitz_estimate = grad_norms.max().item()
                self.tr_lipschitz_constants[i] = np.clip(lipschitz_estimate, 0.1, 10.0)

            except:
                self.tr_lipschitz_constants[i] = 1.0

    def _get_adapted_length(self, region_id, base_length):
        """Get Lipschitz-adapted trust region length."""
        if not self.use_lipschitz_adaptation or region_id >= len(
            self.tr_lipschitz_constants
        ):
            return base_length

        lipschitz = self.tr_lipschitz_constants[region_id]
        adaptation = min(2.0, max(0.5, 1.0 / (1.0 + lipschitz)))
        return base_length * adaptation

    # ===============================================
    # Enhanced Entropy and Trust Region Control
    # ===============================================

    def _compute_exploration_entropy(self, gp_model, n_samples=256):
        """Compute exploration entropy efficiently with gradient enhancement."""
        # Use cached Sobol points
        gap_points = self._sobol_engine.draw(n_samples).to(
            device=self.device, dtype=self.dtype
        )

        with torch.no_grad():
            posterior = gp_model(gap_points)
            var = posterior.variance.clamp_min(1e-9)
            entropy = 0.5 * torch.log(2 * math.pi * math.e * var).mean().item()

        # Enhanced entropy with gradient information when enabled
        if self.use_gradient_information:
            try:
                # Sample fewer points for gradient computation (expensive)
                n_grad_samples = min(64, n_samples // 4)
                grad_points = gap_points[:n_grad_samples]

                mean_pred, var_pred, mean_grad, var_grad = gp_predict_with_grad(
                    gp_model, grad_points
                )

                # Gradient-enhanced entropy
                grad_norm = torch.norm(mean_grad, dim=-1)
                gradient_entropy_bonus = 0.1 * torch.log(1 + grad_norm).mean().item()
                entropy += gradient_entropy_bonus

                if self.verbose and self.n_evals % 200 == 0:
                    print(
                        f"[GRADIENT] Entropy enhanced: base={entropy-gradient_entropy_bonus:.3f} → "
                        f"enhanced={entropy:.3f} (grad_bonus={gradient_entropy_bonus:.3f})"
                    )

            except Exception as e:
                if self.verbose:
                    print(f"[GRADIENT] Entropy gradient computation failed: {e}")

        return entropy, gap_points.cpu().numpy(), var.cpu().numpy()

    def adaptive_capacity_based_on_entropy_and_gradient(self, gp_global, max_cap=None):
        """Adapt trust region capacity based on entropy, gradient norm, and progress."""
        if max_cap is None:
            max_cap = self.max_regions

        n_samples = 128
        with torch.no_grad():
            # Draw Sobol samples in unit cube
            X_unit = self._sobol_engine.draw(n_samples).to(
                device=self.device, dtype=self.dtype
            )
            posterior = gp_global(X_unit)
            var = posterior.variance.clamp_min(1e-9)
            entropy = 0.5 * torch.log(2 * math.pi * math.e * var).cpu().numpy()

        # Optional: gradient-aware entropy bonus
        if self.use_gradient_information:
            try:
                X_unit.requires_grad_(True)
                mean, var, grad_mean, _ = gp_predict_with_grad(gp_global, X_unit)
                grad_norm = torch.norm(grad_mean, dim=1).detach().cpu().numpy()
                entropy += 0.1 * np.log1p(grad_norm)
            except:
                pass

        # Normalize entropy to [0, 1]
        entropy_score = (entropy - entropy.min()) / (entropy.ptp() + 1e-9)
        avg_entropy = np.mean(entropy_score)

        # Normalize Lipschitz constants (lower = better)
        if self.n_trust_regions > 0:
            lipschitz_vals = self.tr_lipschitz_constants[: self.n_trust_regions]
            lipschitz_score = 1.0 / (1.0 + lipschitz_vals)
            avg_lipschitz_score = np.mean(lipschitz_score)
        else:
            avg_lipschitz_score = 1.0

        # Optimization progress
        progress = min(1.0, self.n_evals / self.max_evals)

        # Final capacity score (weight can be tuned)
        score = 0.5 * avg_entropy + 0.3 * avg_lipschitz_score + 0.2 * (1 - progress)

        # Scale to [min_cap, max_cap]
        min_cap = 2
        capacity = int(min_cap + (max_cap - min_cap) * score)
        capacity = np.clip(capacity, min_cap, max_cap)

        if self.verbose and self.n_evals % 50 == 0:
            print(
                f"[ADAPTIVE CAPACITY] score={score:.3f}, avg_entropy={avg_entropy:.3f}, "
                f"avg_lipschitz={avg_lipschitz_score:.3f}, progress={progress:.2f} → capacity={capacity}"
            )

        return capacity


    def _trust_region_controller(self, gp_global):
        """Trust region controller using DBSCAN for region merging."""
        if self.n_trust_regions == 0:
            return

        dynamic_capacity = self.adaptive_capacity_based_on_entropy_and_gradient(
            gp_global
        )

        centers_unit = to_unit_cube(
            self.tr_centers[: self.n_trust_regions], self.lb, self.ub
        )
        qualities = self.tr_quality_scores[: self.n_trust_regions]
        lipschitz_vals = self.tr_lipschitz_constants[: self.n_trust_regions]

        # Merge redundant regions using DBSCAN
        if self.n_trust_regions > dynamic_capacity:
            from sklearn.cluster import DBSCAN

            if self.verbose:
                print(
                    f"[PURGE] Over capacity: {self.n_trust_regions} > {dynamic_capacity}"
                )

            # DBSCAN does not require n_clusters
            clustering = DBSCAN(eps=0.2, min_samples=1).fit(centers_unit)
            cluster_labels = clustering.labels_

            keep_indices = []
            merge_info = []

            for c in set(cluster_labels):
                cluster_indices = np.where(cluster_labels == c)[0]
                if len(cluster_indices) > 0:
                    # Multi-objective region score
                    scores = 0.5 * qualities[cluster_indices] / (
                        qualities[cluster_indices].max() + 1e-9
                    ) + 0.5 * (1 / (1 + lipschitz_vals[cluster_indices]))
                    best_idx = cluster_indices[np.argmax(scores)]
                    keep_indices.append(best_idx)

                    if len(cluster_indices) > 1:
                        merge_candidates = [i for i in cluster_indices if i != best_idx]
                        merge_info.append((best_idx, merge_candidates))

            # Log merges
            for best_idx, mergees in merge_info:
                if self.verbose:
                    print(
                        f"[MERGE] TR-{best_idx} absorbs {mergees} "
                        f"(quality={qualities[best_idx]:.3f})"
                    )

            # Remove non-selected
            to_remove = [
                i for i in range(self.n_trust_regions) if i not in keep_indices
            ]
            for idx in sorted(to_remove, reverse=True):
                if self.verbose:
                    print(
                        f"[PURGE] Removing TR-{idx} "
                        f"(quality={qualities[idx]:.3f}, lipschitz={lipschitz_vals[idx]:.3f})"
                    )
                self._remove_trust_region(idx)

        # Spawn new regions if capacity allows
        if self.n_trust_regions < dynamic_capacity:
            entropy, gap_points, gap_var = self._compute_exploration_entropy(gp_global)

            if self.n_trust_regions > 0:
                centers_unit = to_unit_cube(
                    self.tr_centers[: self.n_trust_regions], self.lb, self.ub
                )
                distances = np.linalg.norm(
                    gap_points[:, None] - centers_unit[None], axis=2
                )
                distance_penalty = distances.min(axis=1)
            else:
                distance_penalty = np.ones(len(gap_points))

            spawn_scores = gap_var * distance_penalty / (distance_penalty.max() + 1e-9)
            spawn_scores_norm = (spawn_scores - spawn_scores.min()) / (
                spawn_scores.ptp() + 1e-9
            )
            entropy_score = spawn_scores_norm.mean()

            n_spawn = int(
                np.clip(entropy_score * (dynamic_capacity - self.n_trust_regions), 1, 4)
            )
            spawn_indices = np.argsort(-spawn_scores)[:n_spawn]

            if self.verbose and len(spawn_indices) > 0:
                print(
                    f"[SPAWN] Creating {len(spawn_indices)} new regions "
                    f"(entropy={entropy:.3f}, capacity={dynamic_capacity})"
                )

            for idx in spawn_indices:
                spawn_center = from_unit_cube(
                    gap_points[idx : idx + 1], self.lb, self.ub
                )[0]
                self._spawn_new_region(spawn_center, entropy)
                
    # def _trust_region_controller(self, gp_global):
    #     """Trust region controller using PPO for adaptive region merging/spawning."""
    #     if self.n_trust_regions == 0:
    #         return

    #     obs = self._compute_rl_observation(gp_global)
    #     obs_tensor = torch.tensor(obs, dtype=torch.float32).unsqueeze(0)

    #     with torch.no_grad():
    #         # print(f"[PPO OBSERVATION] {obs_tensor.squeeze().cpu().numpy()}")
    #         dist, value = self.rl_agent(obs_tensor)
    #         action = dist.sample().squeeze(0)  # shape: [2]
    #         merge_eps = float(torch.sigmoid(action[0]) * 0.4 + 0.05)
    #         n_spawn = int(torch.clamp(torch.round(torch.relu(action[1]) * 4), 0, 4))
    #         logprob = dist.log_prob(action).sum().item()


    #     merge_eps = float(torch.sigmoid(action[0]) * 0.4 + 0.05)  # [0.05, 0.45]
    #     n_spawn = int(torch.clamp(torch.round(torch.relu(action[1]) * 4), 0, 4))

    #     if self.verbose:
    #         print(f"[PPO ACTION] merge_eps={merge_eps:.3f}, n_spawn={n_spawn}")

    #     # Save transition
    #     self._ppo_buffer.obs.append(obs)
    #     self._ppo_buffer.actions.append([action[0].item(), action[1].item()])
    #     self._ppo_buffer.logprobs.append(logprob)
    #     self._ppo_buffer.values.append(value)

    #     # Perform DBSCAN merging
    #     if self.n_trust_regions > self.adaptive_capacity_based_on_entropy_and_gradient(gp_global):
    #         from sklearn.cluster import DBSCAN

    #         centers_unit = to_unit_cube(self.tr_centers[: self.n_trust_regions], self.lb, self.ub)
    #         clustering = DBSCAN(eps=merge_eps, min_samples=1).fit(centers_unit)
    #         cluster_labels = clustering.labels_
    #         keep_indices = []
    #         for c in set(cluster_labels):
    #             indices = np.where(cluster_labels == c)[0]
    #             if len(indices) > 0:
    #                 best = indices[np.argmax(self.tr_quality_scores[indices])]
    #                 keep_indices.append(best)
    #         to_remove = [i for i in range(self.n_trust_regions) if i not in keep_indices]
    #         for i in sorted(to_remove, reverse=True):
    #             self._remove_trust_region(i)

    #     # Spawn new regions
    #     entropy, gap_points, gap_var = self._compute_exploration_entropy(gp_global)
    #     if self.n_trust_regions < self.max_regions and n_spawn > 0:
    #         centers_unit = to_unit_cube(self.tr_centers[:self.n_trust_regions], self.lb, self.ub)
    #         distances = np.linalg.norm(gap_points[:, None] - centers_unit[None], axis=2)
    #         distance_penalty = distances.min(axis=1)
    #         scores = gap_var * distance_penalty
    #         top_idx = np.argsort(-scores)[:n_spawn]
    #         for idx in top_idx:
    #             new_center = from_unit_cube(gap_points[idx:idx+1], self.lb, self.ub)[0]
    #             self._spawn_new_region(new_center, entropy)

    #     # Train PPO every K steps
    #     if self.global_step % self.train_interval == 0 and len(self._ppo_buffer.rewards) >= self.batch_size:
    #         # print(f"[PPO TRAIN] Training step {self.global_step}, batch size: {len(self._ppo_buffer.rewards)}")
    #         self.ppo_trainer.train(self._ppo_buffer)
    #         # print(f"[PPO TRAIN] Completed step {self.global_step}")
    #         self._ppo_buffer.clear()

    def _compute_rl_observation(self, gp_global=None):
        """
        Compute the RL observation vector as a flat numerical summary of:
        - Trust region statistics
        - GP model uncertainty
        - Global state

        Returns:
            obs: np.ndarray of shape (obs_dim,)
        """
        if self.n_trust_regions == 0:
            # Zero state: no trust regions yet
            return np.zeros(self.rl_obs_dim, dtype=np.float32)

        # Get core stats
        n_tr = self.n_trust_regions
        cap = self.adaptive_capacity_based_on_entropy_and_gradient(gp_global)
        entropy, gap_points, gap_var = self._compute_exploration_entropy(gp_global)

        q = self.tr_quality_scores[:n_tr]
        l = self.tr_lipschitz_constants[:n_tr]

        # Normalize stats
        q_mean, q_std = np.mean(q), np.std(q)
        l_mean, l_std = np.mean(l), np.std(l)

        # Optional: mean distance between trust regions
        centers_unit = to_unit_cube(self.tr_centers[:n_tr], self.lb, self.ub)
        dists = np.linalg.norm(centers_unit[:, None] - centers_unit[None], axis=-1)
        avg_dist = np.mean(dists[np.triu_indices(n_tr, k=1)]) if n_tr > 1 else 0.0

        obs = np.array([
            n_tr / self.max_regions,                    # normalized region count
            cap / self.max_regions,                     # normalized capacity
            q_mean, q_std,                              # trust region quality
            l_mean, l_std,                              # local Lipschitz estimates
            entropy,                                    # exploration entropy
            avg_dist                                    # average spacing
        ], dtype=np.float32)

        return obs


    def _compute_rl_reward(self):
        new_best = self.fX.min()

        if not hasattr(self, "prev_best_global") or math.isinf(self.prev_best_global):
            # First call: initialize without reward
            self.prev_best_global = new_best
            print(f"[PPO REWARD] Initialized best to {new_best:.4f}")
            return 0.0

        reward = self.prev_best_global - new_best
        self.prev_best_global = min(self.prev_best_global, new_best)
        return reward


    def _spawn_new_region(self, spawn_center, entropy_value):
        """Spawn new trust region with multi-fidelity initialization."""
        # Add new region
        region_id = self.n_trust_regions
        self.n_trust_regions += 1
        self.failcount = np.append(self.failcount, 0)
        self.succcount = np.append(self.succcount, 0)
        self.length = np.append(self.length, self.length_init)
        self.hypers.append({})

        # Update region tracking
        self.tr_centers = np.vstack([self.tr_centers, spawn_center])
        self.tr_quality_scores = np.append(self.tr_quality_scores, entropy_value)
        self.tr_lipschitz_constants = np.append(self.tr_lipschitz_constants, 1.0)
        self.tr_uncertainty_history.append([])

        # Multi-fidelity initialization
        n_init = max(self.n_init // 2, 3)
        init_radius = min(0.2, self.length_init)

        # Generate initial points
        sobol_points = self._sobol_engine.draw(n_init).numpy()
        X_init_unit = np.clip(
            to_unit_cube(spawn_center[None], self.lb, self.ub)
            + init_radius * (sobol_points - 0.5),
            0,
            1,
        )
        X_init = from_unit_cube(X_init_unit, self.lb, self.ub)

        # Evaluate with multi-fidelity
        if hasattr(self, "evaluate_fidelity"):
            # Low fidelity first
            f_low = np.array([[self.evaluate_fidelity(x, "low")] for x in X_init])
            # Promote top candidates
            n_promote = max(1, int(self.multi_fidelity_ratio * n_init))
            promote_idx = np.argsort(f_low.ravel())[:n_promote]
            X_eval = X_init[promote_idx]
            f_eval = np.array([[self.f(x)] for x in X_eval])

            if self.verbose:
                print(
                    f"[SPAWN] TR-{region_id}: Multi-fidelity init "
                    f"{n_init} → {len(X_eval)} promoted, "
                    f"best={f_eval.min():.4f}, entropy={entropy_value:.3f}"
                )
        else:
            X_eval = X_init
            f_eval = np.array([[self.f(x)] for x in X_eval])

            if self.verbose:
                print(
                    f"[SPAWN] TR-{region_id}: Standard init "
                    f"{len(X_eval)} points, "
                    f"best={f_eval.min():.4f}, entropy={entropy_value:.3f}"
                )

        # Update global state
        self.X = np.vstack([self.X, X_eval])
        self.fX = np.vstack([self.fX, f_eval])
        tr_idx = self.n_trust_regions - 1
        self._idx = np.vstack(
            [self._idx, tr_idx * np.ones((len(X_eval), 1), dtype=int)]
        )
        self.n_evals += len(X_eval)

        # Update region center
        best_idx = np.argmin(f_eval)
        self.tr_centers[tr_idx] = X_eval[best_idx]

        self.spawn_history.append(self.n_evals)

    def _remove_trust_region(self, tr_idx):
        """Remove trust region efficiently."""
        if tr_idx >= self.n_trust_regions:
            return

        if self.verbose:
            tr_mask = self._idx[:, 0] == tr_idx
            n_points = tr_mask.sum() if tr_mask.any() else 0
            best_val = self.fX[tr_mask, 0].min() if n_points > 0 else float("inf")
            print(
                f"[REMOVE] TR-{tr_idx} deleted "
                f"({n_points} points, best={best_val:.4f})"
            )

        # Mark points as inactive
        self._idx[self._idx == tr_idx] = -1
        self._idx[self._idx > tr_idx] -= 1

        # Remove region state
        self.tr_centers = np.delete(self.tr_centers, tr_idx, axis=0)
        self.tr_quality_scores = np.delete(self.tr_quality_scores, tr_idx)
        self.tr_lipschitz_constants = np.delete(self.tr_lipschitz_constants, tr_idx)
        self.tr_uncertainty_history.pop(tr_idx)

        # Remove TuRBO state
        self.failcount = np.delete(self.failcount, tr_idx)
        self.succcount = np.delete(self.succcount, tr_idx)
        self.length = np.delete(self.length, tr_idx)
        self.hypers.pop(tr_idx)

        self.n_trust_regions -= 1

    def _handle_restarts(self):
        """Handle restart of stagnated trust regions."""
        for i in range(self.n_trust_regions):
            if self.length[i] < self.length_min:
                tr_mask = self._idx[:, 0] == i
                n_points = tr_mask.sum() if tr_mask.any() else 0
                old_best = self.fX[tr_mask, 0].min() if n_points > 0 else float("inf")

                if self.verbose:
                    print(
                        f"[RESTART] TR-{i} stagnated "
                        f"(length={self.length[i]:.2e} < {self.length_min:.2e}, "
                        f"best={old_best:.4f})"
                    )

                # Reset region
                self.length[i] = self.length_init
                self.succcount[i] = 0
                self.failcount[i] = 0
                self.hypers[i] = {}
                self.tr_quality_scores[i] = 1.0
                self.tr_lipschitz_constants[i] = 1.0

                # Reinitialize around best point
                if len(self.X) > 0:
                    best_point = self.X[self.fX.argmin()]
                    restart_center = np.clip(
                        best_point
                        + 0.1 * (np.random.rand(self.dim) - 0.5) * (self.ub - self.lb),
                        self.lb,
                        self.ub,
                    )
                    self.tr_centers[i] = restart_center

                    if self.verbose:
                        print(f"[RESTART] TR-{i} relocated to vicinity of global best")

    # ===============================================
    # Enhanced Length Adjustment
    # ===============================================

    def _adjust_length(self, fX_next, idx, X_next=None):
        """Enhanced length adjustment with Lipschitz adaptation."""
        old_length = self.length[idx]
        super()._adjust_length(fX_next, idx)
        new_length = self.length[idx]

        # Apply Lipschitz adaptation
        if self.use_lipschitz_adaptation:
            adapted_length = self._get_adapted_length(idx, self.length[idx])
            self.length[idx] = adapted_length

        # Update quality scores and log significant changes
        improvement = fX_next.min() - self.fX.min()
        old_quality = self.tr_quality_scores[idx]

        if improvement < -1e-3 * abs(self.fX.min()):
            self.tr_quality_scores[idx] = min(2.0, self.tr_quality_scores[idx] + 0.1)
            if self.verbose and improvement < -1e-2 * abs(self.fX.min()):
                print(
                    f"[IMPROVE] TR-{idx}: New best {fX_next.min():.4f} "
                    f"(Δ={improvement:.3e}, quality {old_quality:.2f}→{self.tr_quality_scores[idx]:.2f})"
                )
        else:
            self.tr_quality_scores[idx] = max(0.1, self.tr_quality_scores[idx] - 0.05)

        # Log significant length changes
        if self.verbose and abs(new_length - old_length) > 0.1 * old_length:
            status = "EXPAND" if new_length > old_length else "SHRINK"
            print(
                f"[{status}] TR-{idx}: length {old_length:.3f}→{self.length[idx]:.3f} "
                f"(lipschitz={self.tr_lipschitz_constants[idx]:.2f})"
            )

    # ===============================================
    # Enhanced Global GP Training
    # ===============================================

    def _train_global_gp(self):
        """Train global GP with intelligent subsampling and caching."""
        # Check cache validity
        if (
            self._cached_global_gp is not None
            and self.n_evals <= self._cache_valid_until + 50
        ):
            return self._cached_global_gp

        # Intelligent subsampling for large datasets
        if len(self.X) > self.max_global_gp_points:
            # Keep best points + diverse selection
            n_best = self.max_global_gp_points // 2
            n_diverse = self.max_global_gp_points - n_best

            best_idx = np.argsort(self.fX.ravel())[:n_best]
            remaining_idx = np.setdiff1d(np.arange(len(self.X)), best_idx)

            if len(remaining_idx) > n_diverse:
                # Farthest point sampling for diversity
                from sklearn.cluster import KMeans

                kmeans = KMeans(n_clusters=n_diverse, random_state=42, n_init=10)
                diverse_idx = remaining_idx[
                    np.argmin(
                        np.linalg.norm(
                            self.X[remaining_idx][:, None]
                            - kmeans.fit(self.X[remaining_idx]).cluster_centers_[None],
                            axis=2,
                        ),
                        axis=1,
                    )
                ]
            else:
                diverse_idx = remaining_idx

            idx_subset = np.concatenate([best_idx, diverse_idx])
            X_sub, fX_sub = self.X[idx_subset], self.fX[idx_subset]
        else:
            X_sub, fX_sub = self.X, self.fX

        # Train GP
        X_unit = to_unit_cube(X_sub, self.lb, self.ub)
        f_std = (fX_sub[:, 0] - fX_sub[:, 0].mean()) / (fX_sub[:, 0].std() + 1e-8)

        gp_global = self._get_cached_gp(X_unit, f_std, "global")

        # Update cache
        self._cached_global_gp = gp_global
        self._cache_valid_until = self.n_evals

        return gp_global

    # ===============================================
    # Main Optimization Loop
    # ===============================================

    def optimize(self):
        """Enhanced main optimization loop."""
        # Initialize regions
        for i in range(self.n_trust_regions):
            X_init = maximin_lhs(self.n_init, self.dim)
            X_init = from_unit_cube(X_init, self.lb, self.ub)

            # Multi-fidelity initialization if available
            if hasattr(self, "evaluate_fidelity"):
                f_low = np.array([[self.evaluate_fidelity(x, "low")] for x in X_init])
                n_promote = max(1, int(self.multi_fidelity_ratio * self.n_init))
                promote_idx = np.argsort(f_low.ravel())[:n_promote]
                X_eval = X_init[promote_idx]
                f_eval = np.array([[self.f(x)] for x in X_eval])
            else:
                X_eval = X_init
                f_eval = np.array([[self.f(x)] for x in X_eval])

            self.X = np.vstack([self.X, X_eval])
            self.fX = np.vstack([self.fX, f_eval])
            self._idx = np.vstack([self._idx, i * np.ones((len(X_eval), 1), dtype=int)])
            #self.n_evals += 1
            self.tr_centers[i] = X_eval[np.argmin(f_eval)]

        # Main optimization loop
        while self.n_evals < self.max_evals:
            print(f"[OPTIMIZATION] Iteration {self.n_evals}/{self.max_evals}")
            # Periodic updates
            if self.n_evals % 10 == 0:
                self._update_lipschitz_constants()

            # Generate candidates for all regions
            X_cand = np.zeros((self.n_trust_regions, self.n_cand, self.dim))
            y_cand = np.full(
                (self.n_trust_regions, self.n_cand, self.batch_size), np.inf
            )

            for i in range(self.n_trust_regions):
                tr_mask = self._idx[:, 0] == i
                if not tr_mask.any():
                    continue

                X_unit = to_unit_cube(self.X[tr_mask], self.lb, self.ub)
                fX_tr = self.fX[tr_mask, 0]
                n_steps = 0 if self.hypers[i] else self.n_training_steps

                X_cand[i], y_cand[i], self.hypers[i] = self._create_candidates(
                    X_unit, fX_tr, self.length[i], n_steps, self.hypers[i], i
                )

            # Select and evaluate candidates
            X_next_unit, idx_next = self._select_candidates(X_cand, y_cand)
            X_next = from_unit_cube(X_next_unit, self.lb, self.ub)

            # Multi-fidelity evaluation if available
            if hasattr(self, "evaluate_fidelity"):
                f_low = np.array([[self.evaluate_fidelity(x, "low")] for x in X_next])
                n_promote = max(1, int(self.multi_fidelity_ratio * len(X_next)))
                promote_idx = np.argsort(f_low.ravel())[:n_promote]
                X_eval = X_next[promote_idx]
                f_eval = np.array([[self.f(x)] for x in X_eval])
                idx_eval = idx_next[promote_idx]
            else:
                X_eval = X_next
                f_eval = np.array([[self.f(x)] for x in X_eval])
                idx_eval = idx_next

            # Update region parameters and meta-acquisition learning
            improvements = []
            for i in range(self.n_trust_regions):
                region_mask = idx_eval[:, 0] == i
                if region_mask.any():
                    self.hypers[i] = {}  # Reset for retraining
                    old_best = self.fX.min()
                    self._adjust_length(f_eval[region_mask], i, X_eval[region_mask])
                    new_best = np.minimum(old_best, f_eval[region_mask].min())
                    improvement = old_best - new_best
                    improvements.append(improvement)
                else:
                    improvements.append(0.0)

            # print(f"[IMPROVEMENT] Improvements: {improvements}")
            reward = np.array(improvements).mean()
            # print(f"[PPO REWARD] Step {self.global_step}, reward: {reward:.4f}")
            self._ppo_buffer.rewards.append(reward)
            self._ppo_buffer.dones.append(False)  # could use termination condition
            self.global_step += 1

            # Update meta-acquisition learning
            if self.use_meta_acquisition and len(improvements) > 0:
                self._update_meta_acquisition(improvements)

            # Update global state
            self.X = np.vstack([self.X, X_eval])
            self.fX = np.vstack([self.fX, f_eval])
            self._idx = np.vstack([self._idx, idx_eval])
            self.n_evals += 1

            # Periodic trust region controller
            #if self.n_evals % 20 == 0 and len(self.X) > 10:
            gp_global = self._train_global_gp()
            print(f"[GLOBAL GP] Trained with {len(self.X)} points, {self.n_trust_regions} regions")
            self._trust_region_controller(gp_global)

            # Restart stagnated regions
            self._handle_restarts()

            # Progress logging
            if self.verbose and self.n_evals % 100 == 0:
                avg_length = self.length[: self.n_trust_regions].mean()
                avg_quality = self.tr_quality_scores[: self.n_trust_regions].mean()
                avg_lipschitz = self.tr_lipschitz_constants[
                    : self.n_trust_regions
                ].mean()

                print(
                    f"[PROGRESS] Iter {self.n_evals}/{self.max_evals}, "
                    f"Best: {self.fX.min():.4f}, "
                    f"Regions: {self.n_trust_regions}, "
                    f"Avg Length: {avg_length:.3f}, "
                    f"Avg Quality: {avg_quality:.3f}, "
                    f"Avg Lipschitz: {avg_lipschitz:.3f}"
                )

        return self.X, self.fX
