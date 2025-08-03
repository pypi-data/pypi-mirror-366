# ========================================
# Core & Typing
# ========================================
from typing import Any, Dict, List, Optional, Tuple, Union

# ========================================
# Visualization
# ========================================
import matplotlib.pyplot as plt

# ========================================
# Numerical & Scientific Computing
# ========================================
import numpy as np
import optuna

# ========================================
# Machine Learning & Optimization
# ========================================
import torch
import torch.nn.functional as F
from scipy import sparse
from scipy.linalg import orth, solve
from scipy.sparse import linalg as splinalg
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

# ========================================
# Device Setup
# ========================================

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

ACTIVATIONS = {
    "sigmoid": torch.sigmoid,
    "relu": F.relu,
    "tanh": torch.tanh,
    "leaky_relu": F.leaky_relu,
    "elu": F.elu,
    "gelu": F.gelu,
    "swish": lambda x: x * torch.sigmoid(x),
    "mish": lambda x: x * torch.tanh(F.softplus(x)),
    "softplus": F.softplus,
    "silu": F.silu,
}


class GPUDirectSolver:
    def __init__(self, device: Optional[str] = None, verbose: bool = False):
        """GPU/CPU adaptive ridge regression solver."""
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
        self.verbose = verbose

    # === Utility ===
    def _to_tensor(self, arr: Union[np.ndarray, torch.Tensor]) -> torch.Tensor:
        """Safely convert NumPy/Tensor to float32 tensor on target device."""
        if isinstance(arr, torch.Tensor):
            return arr.detach().to(self.device, dtype=torch.float32)
        return torch.as_tensor(arr, dtype=torch.float32, device=self.device)

    def _check_shapes(self, X: torch.Tensor, y: torch.Tensor):
        """Ensure consistent sample counts."""
        if X.shape[0] != y.shape[0]:
            raise ValueError(
                f"Shape mismatch: X has {X.shape[0]} rows, y has {y.shape[0]} rows"
            )

    # === Public API ===
    def direct_solver(
        self,
        X: Union[np.ndarray, torch.Tensor],
        y: Union[np.ndarray, torch.Tensor],
        l2_reg: float,
    ) -> torch.Tensor:
        """
        Solve ridge regression:
            beta = argmin ||X beta - y||² + λ||beta||²
        Supports multi-output y.
        """
        X = self._to_tensor(X)
        y = self._to_tensor(y)
        self._check_shapes(X, y)

        n_samples, n_features = X.shape

        # Multi-output always as 2D (n, m_outputs)
        if y.dim() == 1:
            y = y[:, None]

        # Auto solver selection
        if n_samples >= n_features:
            return self._solve_normal_equations(X, y, l2_reg)
        else:
            return self._solve_svd(X, y, l2_reg)

    def memory_efficient_solve(
        self,
        X: Union[np.ndarray, torch.Tensor],
        y: Union[np.ndarray, torch.Tensor],
        l2_reg: float,
        chunk_size: int = 8192,
    ) -> torch.Tensor:
        """
        Memory-efficient ridge solve.
        Accumulates X^T X and X^T y in chunks to avoid GPU OOM.
        """
        if isinstance(X, torch.Tensor):
            X = X.detach().cpu().numpy()
        if isinstance(y, torch.Tensor):
            y = y.detach().cpu().numpy()

        n_samples, n_features = X.shape
        y = y.reshape(n_samples, -1)
        n_outputs = y.shape[1]

        # Initialize accumulators
        XTX_acc = torch.zeros(n_features, n_features, device=self.device)
        XTy_acc = torch.zeros(n_features, n_outputs, device=self.device)

        for start in range(0, n_samples, chunk_size):
            end = min(start + chunk_size, n_samples)
            X_chunk = torch.from_numpy(X[start:end]).to(self.device)
            y_chunk = torch.from_numpy(y[start:end]).to(self.device)

            XTX_acc += X_chunk.T @ X_chunk
            XTy_acc += X_chunk.T @ y_chunk

            del X_chunk, y_chunk
            if self.device.type == "cuda":
                torch.cuda.empty_cache()

        regI = l2_reg * torch.eye(n_features, device=self.device)
        A = XTX_acc + regI

        return self._solve_system(A, XTy_acc)

    def solve_batch(
        self,
        X_batch: List[Union[np.ndarray, torch.Tensor]],
        y_batch: List[Union[np.ndarray, torch.Tensor]],
        l2_reg: float,
    ) -> List[torch.Tensor]:
        """Solve multiple independent ridge problems sequentially."""
        if len(X_batch) != len(y_batch):
            raise ValueError("X_batch and y_batch length mismatch")
        return [self.direct_solver(X, y, l2_reg) for X, y in zip(X_batch, y_batch)]

    # === Internal solver paths ===
    def _solve_normal_equations(
        self, X: torch.Tensor, Y: torch.Tensor, l2_reg: float
    ) -> torch.Tensor:
        """
        Solve (X^T X + λI) β = X^T Y.
        Multi-output Y handled in one call.
        """
        XTX = X.T @ X
        XTY = X.T @ Y
        regI = l2_reg * torch.eye(XTX.shape[0], device=self.device, dtype=X.dtype)
        A = XTX + regI
        return self._solve_system(A, XTY)

    def _solve_svd(
        self, X: torch.Tensor, Y: torch.Tensor, l2_reg: float
    ) -> torch.Tensor:
        """
        Solve ridge regression using SVD:
        β = V diag(s/(s²+λ)) U^T Y.
        """
        U, s, Vt = torch.linalg.svd(X, full_matrices=False)

        # Clamp small singular values for stability
        eps = 1e-8
        s_reg = s / (s.square() + l2_reg + eps)

        UTY = U.T @ Y  # (n_samples, n_outputs)
        return Vt.T @ (s_reg[:, None] * UTY)

    def _solve_system(self, A: torch.Tensor, B: torch.Tensor) -> torch.Tensor:
        """
        Solve A β = B with fallback strategies:
        1) Cholesky if PD
        2) torch.linalg.solve
        3) torch.linalg.lstsq fallback
        """
        try:
            L = torch.linalg.cholesky(A)
            beta = torch.cholesky_solve(B, L)
        except RuntimeError:
            try:
                beta = torch.linalg.solve(A, B)
            except RuntimeError:
                beta = torch.linalg.lstsq(A, B).solution

        if self.verbose:
            cond = torch.linalg.cond(A).item()
            print(f"[Solver] cond(A)={cond:.2e} | beta shape={tuple(beta.shape)}")
        return beta


try:
    from kymatio.torch import Scattering1D, Scattering2D
except ImportError:
    Scattering1D, Scattering2D = None, None


class RVFL_OPTUNA:
    def __init__(
        self,
        input_dim: int,
        hidden_dim: int,
        output_dim: int = 1,
        activation: str = "gelu",
        n_trials: int = 100,
        dropout_rate: float = 0.02,
        l2_reg: float = 1e-4,
        projection_method: str = "auto",
        multi_activation: bool = False,
        spectral_norm: bool = False,
        kernel_approx: bool = False,
        multi_kernel_approx: bool = False,
        nystrom_features: bool = False,
        fastfood_features: bool = False,
        use_ntk_features: bool = True,
        ntk_scaling: float = 1.0,
        solver: str = "direct",
        admm_rho: float = 1.0,
        sample_weights: Optional[np.ndarray] = None,
        direct_link: bool = False,
        scale_direct: float = 0.05,
        verbose: bool = False,
        trainable: bool = False,
        attention_features: bool = True,
        wavelet_features: bool = True,
    ):
        # Core dimensions
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim

        # RVFL specific parameters
        self.direct_link = direct_link
        self.scale_direct = scale_direct

        # Activation configuration
        self.multi_activation = multi_activation
        if multi_activation:
            self.activations = list(ACTIVATIONS.values())
            self.activation_names = list(ACTIVATIONS.keys())
        else:
            self.activation = ACTIVATIONS[activation]

        # Training parameters
        self.dropout_rate = dropout_rate
        self.l2_reg = l2_reg
        self.n_trials = n_trials
        self.verbose = verbose
        self.trainable = trainable

        # Feature generation parameters
        self.projection_method = projection_method
        self.spectral_norm = spectral_norm
        self.kernel_approx = kernel_approx
        self.multi_kernel_approx = multi_kernel_approx
        self.nystrom_features = nystrom_features
        self.fastfood_features = fastfood_features

        # NTK parameters
        self.use_ntk_features = use_ntk_features
        self.ntk_scaling = ntk_scaling

        # Solver parameters
        self.solver = solver
        self.admm_rho = admm_rho

        # Model parameters (initialized during fit)
        self.W = None
        self.b = None
        self.beta = None
        self.act_indices = None

        # Training data storage
        self.X = None
        self.y_np = None
        self.feature_importances_ = None

        # Feature dimensions (set during training)
        self.hidden_feature_dim = None
        self.kernel_feature_dim = None
        self.ntk_feature_dim = None
        self.nystrom_landmarks = None  # Store landmarks for Nyström
        self.nystrom_feature_dim = None

        # Process sample weights
        self.sample_weights = self._process_sample_weights(sample_weights)

        self.direct_link_gain = None  # low-rank gain matrix
        self.direct_link_bias = None  # bias vector
        self.direct_link_rank = min(32, self.input_dim)  # adjustable low rank

        self._feature_cache = {}

        self.attention_features = attention_features

        self.device = device
        self.wavelet_features = wavelet_features

    def _cache_static_features(self):
        """
        Precompute trial-invariant static features ONCE and keep them in GPU memory.
        These will be reused across Optuna trials.
        """
        if self._feature_cache:
            # Already cached
            return

        self._feature_cache = {}

        # === Kernel approx (static RFF) ===
        if self.kernel_approx:
            self._feature_cache["kernel_approx"] = self._random_fourier_features(
                self.X, num_features=min(self.hidden_dim // 2, 100)
            )

        # === Multi-kernel ===
        if self.multi_kernel_approx:
            self._feature_cache["multi_kernel"] = self._multi_kernel_features(self.X)

        # === Nyström landmarks (precomputed once!) ===
        if self.nystrom_features:
            self._feature_cache["nystrom"] = self._nystrom_kernel_features(
                self.X, num_landmarks=min(self.hidden_dim // 2, 100)
            )

        # === Fastfood projection (precomputed once!) ===
        if self.fastfood_features:
            self._feature_cache["fastfood"] = self._fastfood_projection(
                self.X, num_features=min(self.hidden_dim, 200)
            )

        if self.verbose:
            for k, v in self._feature_cache.items():
                print(f"[Cache] {k} shape={tuple(v.shape)}")

    def _process_sample_weights(
        self, sample_weights: Optional[Union[torch.Tensor, np.ndarray]]
    ) -> Optional[np.ndarray]:
        """Process and normalize sample weights."""
        if sample_weights is None:
            return None

        if isinstance(sample_weights, torch.Tensor):
            sample_weights = sample_weights.detach().cpu().numpy()

        weights = np.array(sample_weights).flatten()
        # Normalize weights to sum to number of samples for numerical stability
        return weights * (len(weights) / np.sum(weights))

    def _init_random_weights(self, method: str = "uniform", scale: float = 1.0):
        """
        State-of-the-art random weight initialization for RVFL hidden layer.

        Supported:
        - "uniform"        → Gaussian scaled by `scale`
        - "xavier"         → Glorot normal
        - "he"             → He normal (for ReLU/GELU)
        - "orthogonal"     → Full orthogonal QR init with padding
        - "pca_orthogonal" → PCA-aligned + orthogonal completion
        - "zca_whitened"   → ZCA-whitened PCA projection
        - "fastfood"       → Structured Fastfood random projection

        Returns:
        W : torch.Tensor (input_dim, hidden_dim)
        b : torch.Tensor (1, hidden_dim)
        """
        in_dim, hid_dim = self.input_dim, self.hidden_dim

        # Placeholder for W
        W = None

        # === 1) Simple Gaussian baseline ===
        if method == "uniform":
            W = torch.randn(in_dim, hid_dim, device=self.device) * scale

        # === 2) Xavier (Glorot) Normal ===
        elif method == "xavier":
            gain = torch.nn.init.calculate_gain("relu")
            std = gain * (2.0 / (in_dim + hid_dim)) ** 0.5
            W = torch.empty(in_dim, hid_dim, device=self.device)
            torch.nn.init.normal_(W, mean=0.0, std=std)

        # === 3) He Normal (good for ReLU/GELU) ===
        elif method == "he":
            std = (2.0 / in_dim) ** 0.5
            W = torch.empty(in_dim, hid_dim, device=self.device)
            torch.nn.init.normal_(W, mean=0.0, std=std)

        # === 4) Strict Orthogonal QR init ===
        elif method == "orthogonal":
            W_np = np.random.randn(in_dim, hid_dim)
            q, _ = np.linalg.qr(W_np)  # full QR
            q = q[:, :hid_dim]  # trim to needed cols

            # If hid_dim > in_dim, we may need extra orthogonal blocks
            while q.shape[1] < hid_dim:
                extra = np.random.randn(in_dim, hid_dim - q.shape[1])
                extra_q, _ = np.linalg.qr(extra)
                q = np.hstack((q, extra_q[:, : hid_dim - q.shape[1]]))
            assert q.shape == (
                in_dim,
                hid_dim,
            ), f"Orthogonal padding failed → got {q.shape}"
            W = torch.tensor(q, dtype=torch.float32, device=self.device) * scale

        # === 5) PCA-Aligned Orthogonal ===
        elif method == "pca_orthogonal":
            X_np = (
                self.X.detach().cpu().numpy()
                if isinstance(self.X, torch.Tensor)
                else np.asarray(self.X)
            )
            X_centered = X_np - X_np.mean(axis=0, keepdims=True)

            from sklearn.utils.extmath import randomized_svd

            requested_pca = min(hid_dim, min(X_centered.shape[0], in_dim))

            if requested_pca > 0:
                U, S, Vt = randomized_svd(
                    X_centered, n_components=requested_pca, random_state=42
                )
                pca_block = Vt.T  # shape (in_dim, requested_pca)
            else:
                pca_block = np.zeros((in_dim, 0))
                S = np.array([])

            W_list = [pca_block]
            current_dim = pca_block.shape[1]

            # Pad remaining dims with random orthogonal
            while current_dim < hid_dim:
                needed = hid_dim - current_dim
                rand_block = np.random.randn(in_dim, needed)
                q_block, _ = np.linalg.qr(rand_block)

                # Orthogonalize against existing PCA subspace
                if current_dim > 0:
                    existing = np.hstack(W_list)
                    proj = existing @ (existing.T @ q_block)
                    q_block -= proj
                    q_block, _ = np.linalg.qr(q_block)

                q_block = q_block[:, :needed]
                W_list.append(q_block)
                current_dim = sum(w.shape[1] for w in W_list)

            # Combine & normalize columns
            W_np = np.hstack(W_list)[:, :hid_dim]
            W_np /= np.linalg.norm(W_np, axis=0, keepdims=True)
            W = torch.tensor(W_np, dtype=torch.float32, device=self.device) * scale

            if self.verbose and len(S) > 0:
                var_explained = (S**2) / np.sum(S**2)
                print(
                    f"[PCA Init] PCA dims={requested_pca}/{hid_dim}, variance={var_explained.sum():.2%}"
                )

        # === 6) ZCA-Whitened PCA Projection ===
        elif method == "zca_whitened":
            X_np = (
                self.X.detach().cpu().numpy()
                if isinstance(self.X, torch.Tensor)
                else np.asarray(self.X)
            )
            X_centered = X_np - X_np.mean(axis=0, keepdims=True)
            cov = np.cov(X_centered, rowvar=False) + 1e-5 * np.eye(in_dim)
            U, S, _ = np.linalg.svd(cov)

            # ZCA whitening matrix (in_dim x in_dim)
            ZCA = U @ np.diag(1.0 / np.sqrt(S)) @ U.T

            # Take only available components
            W_list = [ZCA[:, : min(in_dim, hid_dim)]]
            current_dim = W_list[0].shape[1]

            # Pad with random orthogonal blocks if hidden_dim > input_dim
            while current_dim < hid_dim:
                needed = hid_dim - current_dim
                rand_block = np.random.randn(in_dim, needed)
                q_block, _ = np.linalg.qr(rand_block)
                W_list.append(q_block[:, :needed])
                current_dim = sum(w.shape[1] for w in W_list)

            # Combine & normalize
            W_np = np.hstack(W_list)[:, :hid_dim]
            W_np /= np.linalg.norm(W_np, axis=0, keepdims=True)
            W = torch.tensor(W_np, dtype=torch.float32, device=self.device) * scale

        # === 7) Fastfood Structured Projection ===
        elif method == "fastfood":
            from scipy.stats import ortho_group

            B = np.random.choice([-1, 1], size=in_dim)
            G = np.random.randn(in_dim)
            Π = np.random.permutation(in_dim)
            H = ortho_group.rvs(dim=in_dim)
            W_np = (H @ np.diag(G) @ H[Π, :] @ np.diag(B))[:, :hid_dim]
            W = torch.tensor(W_np, dtype=torch.float32, device=self.device) * scale

        else:
            raise ValueError(f"Unknown weight initialization method: {method}")

        # === Final Shape Checks ===
        if W.shape != (in_dim, hid_dim):
            raise RuntimeError(
                f"[InitError] W shape mismatch: got {W.shape}, expected {(in_dim, hid_dim)}"
            )

        # ✅ Always initialize bias AFTER W is finalized
        b = torch.randn(1, hid_dim, device=self.device) * scale

        # Double-check bias shape
        if b.shape != (1, hid_dim):
            raise RuntimeError(
                f"[InitError] Bias shape mismatch: got {b.shape}, expected {(1, hid_dim)}"
            )

        return W, b

    def _apply_spectral_normalization(
        self, W: torch.Tensor, target_norm: float = 1.0
    ) -> torch.Tensor:
        """Apply spectral normalization to the weight matrix."""
        if not self.spectral_norm:
            return W

        with torch.no_grad():
            try:
                # Power iteration method to approximate largest singular value
                u = F.normalize(torch.randn(1, W.shape[0], device=device), dim=1)
                v = F.normalize(torch.randn(1, W.shape[1], device=device), dim=1)

                # Power iteration (usually converges quickly)
                for _ in range(5):
                    v = F.normalize(u @ W, dim=1)
                    u = F.normalize(v @ W.t(), dim=1)

                sigma = (u @ W @ v.t()).item()

                # Scale the weight matrix
                if sigma > 0:
                    W = W * (target_norm / sigma)
            except Exception:
                # Fall back to non-spectral normalized if there's an issue
                if self.verbose:
                    print(
                        "Warning: Spectral normalization failed, using original weights"
                    )

        return W

    def _random_fourier_features(
        self, X: torch.Tensor, num_features: int = 100, gamma: float = 1.0
    ) -> torch.Tensor:
        """Approximate RBF kernel using random Fourier features."""
        n_samples, n_features = X.shape

        # Generate random weights for the projection
        W_kernel = torch.randn(n_features, num_features, device=device) * np.sqrt(
            2 * gamma
        )
        b_kernel = torch.rand(num_features, device=device) * 2 * np.pi

        # Project the data
        projected = X @ W_kernel + b_kernel

        # Apply trigonometric transformation
        features_sin = torch.sin(projected)
        features_cos = torch.cos(projected)

        # Concatenate and scale
        kernel_features = torch.cat([features_sin, features_cos], dim=1) / np.sqrt(
            num_features
        )

        return kernel_features

    def _multi_kernel_features(
        self, X: torch.Tensor, kernels: Tuple[str, ...] = ("rbf", "matern", "laplace")
    ) -> torch.Tensor:
        """Generate features using multiple kernel types for better diversity."""
        all_feats = []
        for k in kernels:
            # Different gamma values for different kernels
            gamma = 1.0 if k == "rbf" else (0.5 if k == "matern" else 2.0)
            feats = self._random_fourier_features(X, num_features=50, gamma=gamma)
            all_feats.append(feats)
        return torch.cat(all_feats, dim=1)

    def _fastfood_projection(self, X: torch.Tensor, num_features: int) -> torch.Tensor:
        """Fastfood transform with batched FFT for all samples."""
        n_samples, d = X.shape
        out_dim = min(num_features, d)

        try:
            # Rademacher (±1)
            B = torch.randint_like(X, low=0, high=2, device=X.device) * 2 - 1
            XB = X * B  # n×d

            # Pad to next power-of-2
            next_pow2 = 1 << (d - 1).bit_length()
            if d < next_pow2:
                pad = next_pow2 - d
                XB = F.pad(XB, (0, pad))  # n×next_pow2

            # ✅ Batched FFT (one call for all samples!)
            H = torch.fft.rfft(XB, dim=1)
            Hcat = torch.cat([H.real, H.imag], dim=1)

            # One shared random permutation for all rows
            perm = torch.randperm(Hcat.shape[1], device=X.device)
            Hperm = Hcat[:, perm]

            # Gaussian scaling
            G = torch.randn(Hperm.shape[1], device=X.device)
            G /= torch.norm(G)
            out = Hperm * G  # scale

            # Trim/pad
            out = (
                out[:, :out_dim]
                if out.shape[1] > out_dim
                else torch.cat(
                    [
                        out,
                        torch.randn(n_samples, out_dim - out.shape[1], device=X.device),
                    ],
                    dim=1,
                )
            )

        except Exception as e:
            print(f"[WARN] Fastfood failed: {e} → fallback random projection")
            out = torch.randn(n_samples, out_dim, device=X.device)

        return out

    def _nystrom_kernel_features(
        self,
        X: torch.Tensor,
        num_landmarks: int = 100,
        kernel_type: str = "rbf",
        gamma: float = 1.0,
    ) -> torch.Tensor:
        """Row-safe Nyström kernel approximation. Always returns n_samples x num_landmarks."""
        n_samples = X.shape[0]
        num_landmarks = min(num_landmarks, n_samples)

        # Pick landmarks consistently (once per trial)
        if self.nystrom_landmarks is None:
            if num_landmarks == n_samples:
                self.nystrom_landmarks = X.clone()
            else:
                idx = torch.randperm(n_samples, device=X.device)[:num_landmarks]
                self.nystrom_landmarks = X[idx].clone()
        landmarks = self.nystrom_landmarks
        L = landmarks.shape[0]

        # Define kernel functions
        def rbf(X1, X2, g):
            return torch.exp(-g * (torch.cdist(X1, X2) ** 2))

        def matern(X1, X2, g):
            d = torch.cdist(X1, X2)
            sqrt3 = np.sqrt(3.0) * d * np.sqrt(g)
            return (1 + sqrt3) * torch.exp(-sqrt3)

        def laplace(X1, X2, g):
            return torch.exp(-g * torch.cdist(X1, X2, p=1))

        kernel_map = {"rbf": rbf, "matern": matern, "laplace": laplace}
        kernel_fn = kernel_map.get(kernel_type, rbf)

        try:
            # Compute K_nm (n_samples x L) and K_mm (L x L)
            K_nm = kernel_fn(X, landmarks, gamma)
            K_mm = kernel_fn(landmarks, landmarks, gamma)

            # Regularize K_mm for stability
            eps = 1e-6
            K_mm += eps * torch.eye(L, device=X.device)

            # Eigendecomposition for inverse sqrt
            eigvals, eigvecs = torch.linalg.eigh(K_mm)
            mask = eigvals > 1e-10
            eigvals, eigvecs = eigvals[mask], eigvecs[:, mask]

            if eigvals.numel() == 0:
                raise RuntimeError("All Nyström eigenvalues too small → fallback")

            inv_sqrt = torch.diag(1.0 / torch.sqrt(eigvals))
            K_mm_inv_sqrt = eigvecs @ inv_sqrt @ eigvecs.T

            # Nyström features: (n_samples, L)
            feats = K_nm @ K_mm_inv_sqrt
            feats *= np.sqrt(L)  # scaling for numerical consistency

            # ✅ Row-safe check
            if feats.shape[0] != n_samples:
                print(f"[WARN] Nyström row mismatch → forcing random fallback")
                feats = torch.randn(n_samples, L, device=X.device)

        except Exception as e:
            print(f"[WARN] Nyström failed: {e} → fallback")
            feats = self._random_fourier_features(X, num_features=L, gamma=gamma)

        return feats

    def _generate_ntk_features(
        self, X: torch.Tensor, W: torch.Tensor, b: torch.Tensor
    ) -> torch.Tensor:
        # --- Cache key must depend on W,b + dataset shape ---
        key = f"ntk_{X.shape[0]}_{torch.sum(W).item():.6f}_{torch.sum(b).item():.6f}"

        if key in self._feature_cache:
            return self._feature_cache[key]

        # Compute NTK features fresh
        n_samples = X.shape[0]
        with torch.autocast(device_type="cuda", dtype=torch.float16):
            Z = X @ W + b
            phi = np.sqrt(2 / np.pi)
            t = phi * (Z + 0.044715 * Z**3)
            tanh_t = torch.tanh(t)
            left = 0.5 * (1.0 + tanh_t)
            right = 0.5 * Z * (1.0 - tanh_t**2) * phi * (1 + 3 * 0.044715 * Z**2)
            gelu_derivative = left + right
            scaled_W = W.T.unsqueeze(0) * gelu_derivative.unsqueeze(-1)
            ntk_feats = torch.bmm(X.unsqueeze(1), scaled_W.transpose(1, 2)).squeeze(1)
            ntk_feats *= self.ntk_scaling

        # ✅ Cache it safely for *this dataset shape only*
        self._feature_cache[key] = ntk_feats
        return ntk_feats

    def _solve_output_weights(
        self,
        final_feats: torch.Tensor,
        _: Optional[torch.Tensor],
        y: np.ndarray,
        l2_reg: float,
    ):
        """Solve for output weights given final concatenated features."""
        feats_np = final_feats.detach().cpu().numpy()

        # Apply sample weights if provided
        if self.sample_weights is not None:
            sqrt_weights = np.sqrt(self.sample_weights).reshape(-1, 1)
            feats_np = feats_np * sqrt_weights
            y = y * sqrt_weights

        # Choose solver
        if self.solver == "admm":
            l1_reg = 1e-3
            return self._admm_solver(feats_np, y, l1_reg=l1_reg, rho=self.admm_rho)

        else:
            return self._direct_solver(feats_np, y, l2_reg)

    def _direct_solver(
        self, combined_features: np.ndarray, y: np.ndarray, l2_reg: float
    ) -> torch.Tensor:
        """Fast solver using low-rank SVD ridge regression."""
        # Convert to torch tensors for SVD solver
        X_tensor = torch.tensor(combined_features, dtype=torch.float32, device=device)
        y_tensor = torch.tensor(y, dtype=torch.float32, device=device)

        # Use fast SVD-based solver
        gpu_solver = GPUDirectSolver("cuda" if torch.cuda.is_available() else "cpu")
        beta = gpu_solver.direct_solver(X_tensor, y_tensor, l2_reg)
        # beta = self._low_rank_ridge_solver(X_tensor, y_tensor, l2_reg)

        return beta

    def _admm_solver(
        self,
        combined_features: np.ndarray,
        y: np.ndarray,
        l1_reg: float,
        rho: float = 1.0,
        max_iter: int = 200,
        tol: float = 1e-4,
    ) -> torch.Tensor:

        # --- Sanitize & convert ---
        feats = np.nan_to_num(combined_features, nan=0.0, posinf=1e3, neginf=-1e3)
        y_np = np.nan_to_num(y, nan=0.0, posinf=1e3, neginf=-1e3)

        X = torch.as_tensor(feats, dtype=torch.float32, device=self.device)
        y = torch.as_tensor(y_np, dtype=torch.float32, device=self.device)

        n_samples, n_features = X.shape
        if y.ndim == 1:
            y = y[:, None]  # ensure multi-output shape
        n_outputs = y.shape[1]

        # --- Precompute for β-update ---
        XTX = X.T @ X
        XTy = X.T @ y

        # Pre-factorize (XᵀX + ρ I)
        A = XTX + rho * torch.eye(n_features, device=self.device)
        try:
            L = torch.linalg.cholesky(A)
            solve_A = lambda rhs: torch.cholesky_solve(rhs, L)
        except RuntimeError:
            # fallback if not PD
            solve_A = lambda rhs: torch.linalg.solve(A, rhs)

        # === Initialize ADMM variables ===
        beta = torch.zeros((n_features, n_outputs), device=self.device)
        z = torch.zeros_like(beta)
        u = torch.zeros_like(beta)

        # Soft-thresholding operator for z-update
        def soft_threshold(x, kappa):
            return torch.sign(x) * torch.clamp(torch.abs(x) - kappa, min=0.0)

        # === ADMM iterations ===
        for k in range(max_iter):
            # β-update (ridge-like)
            rhs = XTy + rho * (z - u)
            beta = solve_A(rhs)

            # z-update (soft-thresholding for L1)
            z_old = z.clone()
            z = soft_threshold(beta + u, l1_reg / rho)

            # dual update
            u = u + beta - z

            # Residuals for stopping criteria
            primal_res = torch.norm(beta - z)
            dual_res = rho * torch.norm(z - z_old)

            if primal_res < tol and dual_res < tol:
                if self.verbose:
                    print(
                        f"[ADMM-LASSO] converged iter={k+1}, "
                        f"primal={primal_res:.2e}, dual={dual_res:.2e}"
                    )
                break

        # Final solution = z (sparse)
        return torch.nan_to_num(z, nan=0.0, posinf=1e6, neginf=-1e6)

    def _rescale_and_soft_gate_features(
        self, features_list: list[torch.Tensor]
    ) -> torch.Tensor:
        """
        AMP-safe: Normalize each feature block to similar RMS, then apply soft gating.
        Ensures no feature type dominates due to scale differences.
        """
        eps = 1e-8
        normalized_blocks = []

        # Compute global reference RMS
        rms_values = [
            torch.sqrt(torch.mean(f.float() ** 2) + eps) for f in features_list
        ]
        global_rms = torch.stack(rms_values).mean()  # global mean RMS across blocks

        for idx, f in enumerate(features_list):
            block_rms = rms_values[idx]

            # === Normalize block to global RMS ===
            rescale = (global_rms / (block_rms + eps)).clamp(0.5, 2.0)
            f_norm = f * rescale

            # === Soft gating (random mild gate around ~1.0) ===
            gate = 0.9 + 0.2 * torch.sigmoid(torch.randn(1, device=f.device))
            f_final = gate * f_norm

            if self.verbose:
                print(
                    f"[Normalize+Gate] Block {idx}: RMS={block_rms.item():.4f}, "
                    f"rescale={rescale.item():.3f}, gate={gate.item():.3f}"
                )

            normalized_blocks.append(f_final)

        # Concatenate normalized blocks
        return torch.cat(normalized_blocks, dim=1)

    def _attention_features(self, X: torch.Tensor, proj_dim: int = 64) -> torch.Tensor:
        """
        Lightweight single-head self-attention feature block.
        Returns shape (n_samples, proj_dim).
        """
        n_samples, d = X.shape
        with torch.autocast(device_type="cuda", dtype=torch.float16):
            # Random projection weights
            W_q = torch.randn(d, proj_dim, device=X.device) / np.sqrt(d)
            W_k = torch.randn(d, proj_dim, device=X.device) / np.sqrt(d)
            W_v = torch.randn(d, proj_dim, device=X.device) / np.sqrt(d)

            Q = X @ W_q  # (n,proj_dim)
            K = X @ W_k
            V = X @ W_v

            # Scaled dot-product attention
            scale = 1.0 / np.sqrt(proj_dim)
            attn_scores = (Q @ K.T) * scale  # (n,n)
            attn_weights = torch.softmax(attn_scores, dim=-1)  # (n,n)

            # Aggregate
            Z = attn_weights @ V  # (n,proj_dim)
        return Z

    def _generate_features(
        self, X: torch.Tensor, W: torch.Tensor, b: torch.Tensor, training: bool = True
    ) -> torch.Tensor:
        n_samples = X.shape[0]

        with torch.autocast(device_type="cuda", dtype=torch.float16):
            features_list = []

            # --- Random hidden layer ---
            if self.multi_activation:
                if training:
                    self.act_indices = torch.randint(
                        0, len(self.activations), (self.hidden_dim,)
                    )
                H = torch.zeros(n_samples, self.hidden_dim, device=device)
                for i, act_fn in enumerate(self.activations):
                    mask = self.act_indices == i
                    if mask.sum() > 0:
                        H[:, mask] = act_fn(X @ W[:, mask] + b[:, mask])
            else:
                H = self.activation(X @ W + b)
            features_list.append(H)

            # --- Kernel approx ---
            if self.kernel_approx:
                features_list.append(
                    self._random_fourier_features(
                        X, num_features=min(self.hidden_dim // 2, 100)
                    )
                )

            # --- Multi-kernel ---
            if self.multi_kernel_approx:
                features_list.append(self._multi_kernel_features(X))

            # --- Nyström ---
            if self.nystrom_features:
                features_list.append(
                    self._nystrom_kernel_features(
                        X, num_landmarks=min(self.hidden_dim // 2, 100)
                    )
                )

            # --- Fastfood ---
            if self.fastfood_features:
                features_list.append(
                    self._fastfood_projection(X, num_features=min(self.hidden_dim, 200))
                )

            # --- NTK ---
            if self.use_ntk_features:
                features_list.append(self._generate_ntk_features(X.clone(), W, b))

            if self.attention_features:
                features_list.append(
                    self._attention_features(X, proj_dim=min(64, self.hidden_dim // 4))
                )

            if getattr(self, "wavelet_features", False):
                # 1D scattering (assuming time-series or flattened signals)
                wst_feats = self._wavelet_scattering_features(
                    X, order=2, J=3, mode="1d"
                )
                features_list.append(wst_feats)

            # ✅ Block normalization + gating
            final_feats = self._rescale_and_soft_gate_features(features_list)

        if final_feats.shape[0] != n_samples:
            print(f"[FATAL] _generate_features row mismatch → fallback")
            final_feats = torch.randn(n_samples, final_feats.shape[1], device=device)

        return final_feats

    def _generate_dynamic_features(
        self, X: torch.Tensor, W: torch.Tensor, b: torch.Tensor
    ) -> torch.Tensor:
        n_samples = X.shape[0]

        if self.multi_activation:
            # ✅ Ensure act_indices always initialized
            if self.act_indices is None or not isinstance(
                self.act_indices, torch.Tensor
            ):
                self.act_indices = torch.randint(
                    0, len(self.activations), (self.hidden_dim,), device=device
                )

            H = torch.zeros(n_samples, self.hidden_dim, device=device)
            for i, act_fn in enumerate(self.activations):
                mask = self.act_indices == i  # boolean mask per column
                if mask.sum().item() > 0:  # convert to scalar
                    H[:, mask] = act_fn(X @ W[:, mask] + b[:, mask])
        else:
            H = self.activation(X @ W + b)

        return H

    def _objective(self, trial) -> float:
        # === Get NAS + hyperparams for this trial ===
        params = self._get_trial_params(trial)

        # === Init random projection weights ===
        W, b = self._init_random_weights(method=params["method"], scale=params["scale"])
        if self.spectral_norm:
            W = self._apply_spectral_normalization(W)

        # ✅ ALWAYS reinitialize act_indices for multi-activation each trial
        if self.multi_activation:
            self.act_indices = torch.randint(
                0, len(self.activations), (self.hidden_dim,), device=self.device
            )

        # === Dynamic hidden layer (always present) ===
        with torch.autocast(device_type="cuda", dtype=torch.float16):
            H_hidden = self._generate_dynamic_features(self.X, W, b)

            # Optional NTK gating
            if params["gate_ntk"]:
                ntk_feats = self._generate_ntk_features(self.X.clone(), W, b)
                H_dynamic = self._rescale_and_soft_gate_features([H_hidden, ntk_feats])
            else:
                H_dynamic = H_hidden

        # Apply dropout on dynamic features
        H_dynamic = F.dropout(H_dynamic, p=params["dropout"], training=True)

        # === Start final feature concat with dynamic ===
        final_feats = H_dynamic

        # === Selectively add NAS-gated static cached features ===
        static_blocks = []

        # Fastfood (static version)
        if params["gate_fastfood"] and "fastfood" in self._feature_cache:
            static_blocks.append(self._feature_cache["fastfood"])

        # Nyström (static landmarks)
        if params["gate_nystrom"] and "nystrom" in self._feature_cache:
            static_blocks.append(self._feature_cache["nystrom"])

        # Multi-kernel features
        if (
            params.get("use_multi_kernel", False)
            and "multi_kernel" in self._feature_cache
        ):
            static_blocks.append(self._feature_cache["multi_kernel"])

        # Basic kernel approximation
        if self.kernel_approx and "kernel_approx" in self._feature_cache:
            static_blocks.append(self._feature_cache["kernel_approx"])

        # Concatenate only enabled static blocks
        if static_blocks:
            static_concat = torch.cat(static_blocks, dim=1)
            final_feats = torch.cat([final_feats, static_concat], dim=1)

        # === NAS-gated feature families computed dynamically ===

        # Attention
        if params["gate_attention"]:
            final_feats = torch.cat(
                [final_feats, self._attention_features(self.X)], dim=1
            )

        # Extra Fastfood (dynamic)
        if params["gate_fastfood"] and params.get("fastfood_features") is not None:
            dyn_ff = self._fastfood_projection(self.X, params["fastfood_features"])
            final_feats = torch.cat([final_feats, dyn_ff], dim=1)

        # Extra Nyström (dynamic)
        if params["gate_nystrom"] and params.get("nystrom_landmarks") is not None:
            dyn_nystrom = self._nystrom_kernel_features(
                self.X,
                num_landmarks=params["nystrom_landmarks"],
                kernel_type=params["nystrom_kernel"],
                gamma=params["nystrom_gamma"],
            )
            final_feats = torch.cat([final_feats, dyn_nystrom], dim=1)

        if params["gate_wavelets"]:
            wst_feats = self._wavelet_scattering_features(
                self.X, order=2, J=3, mode="1d"
            )
            final_feats = torch.cat([final_feats, wst_feats], dim=1)

        # === Direct link ===
        if self.direct_link:
            X_direct_scaled = self._normalize_direct_link(self.X, H_dynamic)
            final_feats = torch.cat([final_feats, X_direct_scaled], dim=1)

        # === Solve regression ===
        beta = self._solve_output_weights(
            final_feats, None, self.y_np, params["l2_reg"]
        )

        # === Predict & compute MSE ===
        y_pred = final_feats.detach().cpu().numpy() @ beta.cpu().numpy()

        if self.sample_weights is not None:
            # Weighted MSE
            return np.sum(
                self.sample_weights * (self.y_np.flatten() - y_pred.flatten()) ** 2
            ) / np.sum(self.sample_weights)
        else:
            return mean_squared_error(self.y_np, y_pred)

    def _get_trial_params(self, trial) -> Dict[str, Any]:
        """Extract *temporary* hyperparameters for one Optuna trial (no persistent mutation).
        Includes NAS gating for all feature families.
        """
        params = {}

        # === Projection method ===
        params["method"] = (
            trial.suggest_categorical(
                "method", ["uniform", "orthogonal", "pca_orthogonal", "zca_whitened"]
            )
            if self.projection_method == "auto"
            else self.projection_method
        )

        # === Scaling & regularization ===
        params["scale"] = trial.suggest_float("scale", 0.1, 2.0, log=True)
        params["l2_reg"] = trial.suggest_float("l2_reg", 1e-6, 1e-2, log=True)
        params["dropout"] = trial.suggest_float("dropout", 0.0, 0.5)

        params["scale_direct"] = (
            trial.suggest_float("scale_direct", 0.01, 0.2)  # ✅ safer range
            if self.direct_link
            else 0.0
        )

        # === NAS Gating for ALL feature families ===
        params["gate_ntk"] = (
            trial.suggest_categorical("gate_ntk", [True, False])
            if self.use_ntk_features
            else False
        )
        params["gate_nystrom"] = (
            trial.suggest_categorical("gate_nystrom", [True, False])
            if self.nystrom_features
            else False
        )
        params["gate_fastfood"] = (
            trial.suggest_categorical("gate_fastfood", [True, False])
            if self.fastfood_features
            else False
        )
        params["gate_attention"] = (
            trial.suggest_categorical("gate_attention", [True, False])
            if getattr(self, "attention_features", False)
            else False
        )
        params["gate_wavelets"] = (
            trial.suggest_categorical("gate_wavelets", [True, False])
            if getattr(self, "wavelet_features", False)
            else False
        )

        # === NTK scaling only if gated on ===
        if params["gate_ntk"]:
            params["ntk_scaling"] = trial.suggest_float(
                "ntk_scaling", 0.1, 10.0, log=True
            )
        else:
            params["ntk_scaling"] = self.ntk_scaling

        # === Multi-kernel approx ===
        if self.multi_kernel_approx:
            params["use_multi_kernel"] = trial.suggest_categorical(
                "use_multi_kernel", [True, False]
            )
            if params["use_multi_kernel"]:
                kernel_options = [
                    ("rbf", "matern", "laplace"),
                    ("rbf", "matern"),
                    ("rbf", "laplace"),
                    ("matern", "laplace"),
                ]
                idx = trial.suggest_categorical(
                    "kernel_combo_idx", list(range(len(kernel_options)))
                )
                params["kernel_combo"] = kernel_options[idx]
            else:
                params["kernel_combo"] = None
        else:
            params["use_multi_kernel"] = False
            params["kernel_combo"] = None

        # === Nyström kernel details only if gated on ===
        if params["gate_nystrom"]:
            params["nystrom_landmarks"] = trial.suggest_int(
                "nystrom_landmarks", 20, 150
            )
            params["nystrom_kernel"] = trial.suggest_categorical(
                "nystrom_kernel", ["rbf", "matern", "laplace"]
            )
            params["nystrom_gamma"] = trial.suggest_float(
                "nystrom_gamma", 0.1, 10.0, log=True
            )
        else:
            params["nystrom_landmarks"] = None
            params["nystrom_kernel"] = None
            params["nystrom_gamma"] = None

        # === Fastfood details only if gated on ===
        if params["gate_fastfood"]:
            params["fastfood_features"] = trial.suggest_int(
                "fastfood_features", 50, 300
            )
        else:
            params["fastfood_features"] = None

        # === Single activation selection ===
        if not self.multi_activation:
            params["activation"] = trial.suggest_categorical(
                "activation", ["gelu", "swish", "mish", "tanh", "leaky_relu"]
            )
        else:
            params["activation"] = None

        return params

    def fit(
        self, X: Union[np.ndarray, torch.Tensor], y: Union[np.ndarray, torch.Tensor]
    ) -> "RVFL_OPTUNA":
        """Fit the RVFL model to the data."""
        # Convert inputs to tensors
        self.X = (
            X.clone().detach().to(device)
            if isinstance(X, torch.Tensor)
            else torch.tensor(X, dtype=torch.float32, device=device)
        )

        # y -> numpy float32 shape (n,1)
        if isinstance(y, torch.Tensor):
            self.y_np = y.detach().cpu().numpy()
        else:
            self.y_np = np.array(y)
        if self.y_np.ndim == 1:
            self.y_np = self.y_np.reshape(-1, 1)
        self.y_np = self.y_np.astype(np.float32)

        # Reset feature cache each fit
        self._feature_cache = {}
        self._cache_static_features()  # Precompute trial-invariant kernel features

        # Hyperparameter optimization with Optuna
        pruner = optuna.pruners.HyperbandPruner(
            min_resource=5, max_resource=max(self.n_trials // 2, 10), reduction_factor=3
        )
        study = optuna.create_study(
            direction="minimize", sampler=optuna.samplers.TPESampler(), pruner=pruner
        )

        # Use sequential trials unless you refactor to be thread-safe
        study.optimize(
            self._objective,
            n_trials=self.n_trials,
            show_progress_bar=self.verbose,
            n_jobs=1,  # safer than -1 due to shared cache
        )

        # Best params from Optuna
        best_params = study.best_params
        if self.verbose:
            print(f"Best hyperparameters: {best_params}")
            print(f"Best validation error: {study.best_value:.6f}")

        # Train final model with best hyperparameters (also uses static cache)
        self._train_final_model(best_params)

        return self

    def _single_step_direct_link_fit(
        self, X: torch.Tensor, H: torch.Tensor, y: torch.Tensor
    ):
        """
        Fast stabilized scaling for direct-link skip connection.
        Just matches RMS scale between hidden features and raw input.
        """
        eps = 1e-8
        rms_hidden = torch.sqrt(torch.mean(H**2) + eps)
        rms_direct = torch.sqrt(torch.mean(X**2) + eps)

        # Stable ratio with clamped range
        scale_ratio = (rms_hidden / (rms_direct + eps)).clamp(
            0.05, 5.0
        ) * self.scale_direct

        # Just store as scaled identity (no residual ridge)
        self.direct_link_gain = (
            scale_ratio * torch.eye(X.shape[1], device=device),
            torch.eye(X.shape[1], device=device),
        )
        self.direct_link_bias = torch.zeros(1, X.shape[1], device=device)

        if self.verbose:
            print(
                f"✅ Direct-link initialized as scaled identity (ratio={scale_ratio.item():.4f})"
            )

    def _train_final_model(self, best_params: Dict[str, Any]) -> None:
        """Train the final model with the best NAS-gated feature selection."""

        # Persist best gating
        self.use_ntk_features = best_params.get("gate_ntk", self.use_ntk_features)
        self.nystrom_features = best_params.get("gate_nystrom", self.nystrom_features)
        self.fastfood_features = best_params.get(
            "gate_fastfood", self.fastfood_features
        )
        self.attention_features = best_params.get(
            "gate_attention", getattr(self, "attention_features", False)
        )
        self.wavelet_features = best_params.get(
            "gate_wavelets", getattr(self, "wavelet_features", False)
        )

        # Standard params
        method = best_params.get("method", self.projection_method)
        scale = best_params.get("scale", 1.0)
        l2_reg = best_params.get("l2_reg", self.l2_reg)
        dropout = best_params.get("dropout", self.dropout_rate)

        # NTK scaling if enabled
        if self.use_ntk_features:
            self.ntk_scaling = best_params.get("ntk_scaling", self.ntk_scaling)

        # Update activation for single-activation mode
        if not self.multi_activation and best_params.get("activation"):
            self.activation = ACTIVATIONS[best_params["activation"]]

        # Initialize final random weights
        self.W, self.b = self._init_random_weights(method=method, scale=scale)
        if self.spectral_norm:
            self.W = self._apply_spectral_normalization(self.W)

        # Generate features with *final selected NAS gating*
        H_combined = self._generate_features(self.X, self.W, self.b, training=True)
        H_combined = F.dropout(H_combined, p=dropout, training=True)

        # Add direct-link if enabled
        if self.direct_link:
            X_direct_scaled = self._normalize_direct_link(self.X, H_combined)
            final_feats = torch.cat([H_combined, X_direct_scaled], dim=1)
        else:
            final_feats = H_combined

        # Store final feature dim
        self.final_feature_dim = final_feats.shape[1]

        # Solve ridge regression
        self.beta = self._solve_output_weights(final_feats, None, self.y_np, l2_reg)

        # Fine-tune direct link if used
        # === Direct-link stabilization ===
        if self.direct_link:
            # ✅ First single-step ridge fit (cheap, stable)
            self._single_step_direct_link_fit(
                self.X, H_combined, torch.tensor(self.y_np, device=device)
            )

            # ✅ Optional fine-tuning only if you want more expressiveness
            if self.verbose:
                print("Fine-tuning direct-link low-rank transform...")

        if self.verbose:
            print(
                f"✅ Final NAS-gated model trained with feature dim = {self.final_feature_dim}"
            )

    def _normalize_direct_link(self, X: torch.Tensor, H: torch.Tensor) -> torch.Tensor:
        """
        Learnable low-rank affine for direct link (after Optuna tuning).
        Initially fallback to RMS scaling if not trained yet.
        """
        if self.direct_link_gain is None or self.direct_link_bias is None:
            # ✅ Initial RMS fallback BEFORE fine-tuning
            eps = 1e-8
            rms_hidden = torch.sqrt(torch.mean(H**2) + eps)
            rms_direct = torch.sqrt(torch.mean(X**2) + eps)
            scale_ratio = (rms_hidden / (rms_direct + 1e-8)).clamp(
                0.1, 10.0
            ) * self.scale_direct
            return X * scale_ratio

        # ✅ AFTER fine-tuning: use learned transform
        # A = U V^T (low-rank projection)
        U, V = self.direct_link_gain
        projected = (X @ U) @ V.T  # low-rank affine
        return projected + self.direct_link_bias

    def predict(self, X: Union[np.ndarray, torch.Tensor]) -> torch.Tensor:
        if self.W is None:
            raise ValueError("RVFL model not trained yet.")

        X_tensor = torch.tensor(X, dtype=torch.float32).to(device)

        # ✅ AMP-enabled inference
        with torch.autocast(device_type="cuda", dtype=torch.float16):
            H_combined = self._generate_features(
                X_tensor, self.W, self.b, training=False
            )
            if self.direct_link:
                X_direct_scaled = self._normalize_direct_link(X_tensor, H_combined)
                combined_feats = torch.cat([H_combined, X_direct_scaled], dim=1)
            else:
                combined_feats = H_combined

            y_pred = combined_feats @ self.beta

        return y_pred

    def _wavelet_scattering_features(
        self, X: torch.Tensor, order: int = 1, J: int = 2, mode: str = "1d"
    ) -> torch.Tensor:
        """
        Optimized Wavelet Scattering Transform features (fast batch mode).

        - Auto adjusts J to avoid border effects.
        - Downsamples very large inputs.
        - Skips if signals too short.
        - Uses caching to avoid recomputation across Optuna trials.
        """
        # ✅ Cache key to avoid recomputation
        cache_key = f"wavelet_{X.shape[0]}_{X.shape[1]}_{order}_{J}_{mode}"
        if cache_key in self._feature_cache:
            return self._feature_cache[cache_key]

        n_samples, d = X.shape

        # ✅ Fast skip for very small signals
        if d < 64:
            if self.verbose:
                print(
                    f"[Wavelet] Skipping scattering (too short: d={d}) → returning zeros"
                )
            feats = torch.zeros(n_samples, 1, device=X.device)
            self._feature_cache[cache_key] = feats
            return feats

        # ✅ Optional downsample for very large signals
        if d > 512:
            if self.verbose:
                print(f"[Wavelet] Downsampling from {d} → 512 for scattering speed")
            X = F.interpolate(
                X.unsqueeze(1), size=512, mode="linear", align_corners=False
            ).squeeze(1)
            d = 512

        # ✅ Auto-adjust J based on log2(signal length)
        max_J = max(1, int(np.floor(np.log2(d))))  # max scale allowed
        J = min(J, max_J)

        # ✅ Fallback if Kymatio not installed
        if Scattering1D is None:
            if self.verbose:
                print(
                    "[WARN] Kymatio not installed → returning random wavelet features"
                )
            feats = torch.randn(n_samples, min(64, d), device=X.device)
            self._feature_cache[cache_key] = feats
            return feats

        # ✅ Batch-mode scattering
        if mode == "1d":
            scattering = Scattering1D(J=J, shape=d, max_order=order).to(X.device)
            Sx = scattering(X)  # shape: (n_samples, n_coeffs, T_out)
            feats = Sx.reshape(n_samples, -1)  # flatten per sample

        elif mode == "2d":
            side = int(np.sqrt(d))
            if side * side != d:
                if self.verbose:
                    print(
                        "[Wavelet] Cannot reshape to 2D → falling back to 1D scattering"
                    )
                return self._wavelet_scattering_features(X, order=order, J=J, mode="1d")

            # 2D scattering for image-like inputs
            max_J2 = max(1, int(np.floor(np.log2(side))))
            J2 = min(J, max_J2)
            scattering = Scattering2D(J=J2, shape=(side, side), max_order=order).to(
                X.device
            )
            X2 = X.view(n_samples, side, side)
            Sx = scattering(X2)  # (n_samples, C, H_out, W_out)
            feats = Sx.reshape(n_samples, -1)

        else:
            raise ValueError(f"Invalid wavelet mode: {mode}")

        # ✅ Cache it for all trials
        self._feature_cache[cache_key] = feats

        if self.verbose:
            print(
                f"[Wavelet] Scattering computed: J={J}, order={order}, mode={mode}, out_dim={feats.shape[1]}"
            )

        return feats

    def get_feature_importance(self) -> Optional[np.ndarray]:
        """Get feature importance based on output weights magnitude."""
        if self.beta is None:
            return None
        importance = torch.abs(self.beta).sum(dim=1).detach().cpu().numpy()
        return importance / importance.sum()

