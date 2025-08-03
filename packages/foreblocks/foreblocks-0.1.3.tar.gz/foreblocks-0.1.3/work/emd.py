# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: hydrogen
#       format_version: '1.3'
#       jupytext_version: 1.17.2
#   kernelspec:
#     display_name: .venv
#     language: python
#     name: python3
# ---

# %%
import numpy as np
import matplotlib.pyplot as plt
from PyEMD import EMD

# Test signal
t = np.linspace(0, 5, 2000)
signal = (
        0.3 * t + 
        np.sin(2*np.pi*4*t) + 
        0.6*np.sin(2*np.pi*15*t) + 
        0.4*np.sin(2*np.pi*35*t) +
        0.05*np.random.normal(size=len(t))
    )
# Library EMD
emd = EMD()
imfs_lib = emd(signal)

print(f"Extracted {imfs_lib.shape[0]} IMFs")

plt.figure(figsize=(10, 8))
plt.subplot(imfs_lib.shape[0]+1, 1, 1)
plt.plot(t, signal)
plt.title("Original Signal (PyEMD)")

for i, imf in enumerate(imfs_lib):
    plt.subplot(imfs_lib.shape[0]+1, 1, i+2)
    plt.plot(t, imf)
    plt.title(f"IMF {i+1}")

plt.tight_layout()
plt.show()


# %%
# -*- coding: utf-8 -*-
"""
Fast Optuna-Optimized VMD (Simple but Effective Optimizations)
"""

import numpy as np
import optuna
import pyfftw
import pyfftw.interfaces.numpy_fft as fftw_np
pyfftw.interfaces.cache.enable()  # Enable FFT plan caching

# Use fftw_np.fft like np.fft


# ==============================================
# Boundary Handling Functions
# ==============================================
def apply_window(signal, window_type='tukey', alpha_win=0.1):
    """Apply windowing to reduce boundary artifacts"""
    N = len(signal)
    if window_type == 'tukey':
        from scipy.signal import windows
        window = windows.tukey(N, alpha_win)
    elif window_type == 'hann':
        window = np.hanning(N)
    elif window_type == 'hamming':
        window = np.hamming(N)
    else:
        window = np.ones(N)
    return signal * window, window

def extend_signal(signal, method='mirror', extension_ratio=0.25):
    """Extend signal to reduce boundary effects"""
    N = len(signal)
    ext_len = int(N * extension_ratio)
    
    if method == 'mirror':
        # Better mirroring - symmetric around endpoints
        left_ext = signal[1:ext_len+1][::-1]
        right_ext = signal[-(ext_len+1):-1][::-1]
        extended = np.concatenate([left_ext, signal, right_ext])
    elif method == 'reflect':
        # Reflect around endpoint values
        left_val = signal[0]
        right_val = signal[-1]
        left_ext = 2*left_val - signal[1:ext_len+1][::-1]
        right_ext = 2*right_val - signal[-(ext_len+1):-1][::-1]
        extended = np.concatenate([left_ext, signal, right_ext])
    elif method == 'linear':
        # Linear extrapolation
        left_slope = (signal[1] - signal[0])
        right_slope = (signal[-1] - signal[-2])
        left_ext = signal[0] + left_slope * np.arange(-ext_len, 0)
        right_ext = signal[-1] + right_slope * np.arange(1, ext_len+1)
        extended = np.concatenate([left_ext, signal, right_ext])
    elif method == 'constant':
        # Constant padding
        left_ext = np.full(ext_len, signal[0])
        right_ext = np.full(ext_len, signal[-1])
        extended = np.concatenate([left_ext, signal, right_ext])
    else:
        return signal, 0, 0
        
    return extended, ext_len, ext_len

def taper_boundaries(modes, taper_length=50):
    """Apply boundary tapering to modes"""
    tapered_modes = []
    for mode in modes:
        tapered = mode.copy()
        N = len(mode)
        taper_len = min(taper_length, N//4)
        
        # Create taper window
        taper = np.ones(N)
        # Left taper
        taper[:taper_len] = np.sin(np.linspace(0, np.pi/2, taper_len))**2
        # Right taper
        taper[-taper_len:] = np.cos(np.linspace(0, np.pi/2, taper_len))**2
        
        tapered_modes.append(tapered * taper)
    return tapered_modes


# ==============================================
# Optimized VMD with Boundary Handling
# ==============================================
import numpy as np
from numba import njit, prange

@njit(parallel=True, fastmath=True)
def update_modes_numba(freqs, half_T, f_hat_plus, sum_uk, lambda_hat_n, Alpha, omega_n, u_hat_prev, K, tau):
    """
    Numba-accelerated update for all K modes in one iteration.
    Returns updated u_hat_plus_next, omega_next, sum_uk_next, lambda_next, diff_norm.
    """
    T = len(freqs)
    freq_slice_start = half_T
    
    # Allocate outputs
    u_hat_plus_next = np.zeros((T, K), dtype=np.complex128)
    omega_next = np.zeros(K)
    
    # Mode sum for lambda update
    mode_sum = np.zeros(T, dtype=np.complex128)
    diff_norm = 0.0
    
    for k in range(K):
        # Update sum_uk for this mode
        if k == 0:
            sum_uk += u_hat_prev[:, K - 1] - u_hat_prev[:, 0]
        else:
            sum_uk += u_hat_plus_next[:, k - 1] - u_hat_prev[:, k]
        
        # Compute denominator (vectorized)
        freq_diff = freqs - omega_n[k]
        denom = 1.0 + Alpha[k] * freq_diff * freq_diff
        
        # Update u_hat for this mode
        u_hat_plus_next[:, k] = (f_hat_plus - sum_uk - lambda_hat_n * 0.5) / denom
        
        # Compute omega update (only for non-DC)
        u_slice = u_hat_plus_next[freq_slice_start:T, k]
        weights = np.abs(u_slice) ** 2
        wsum = np.sum(weights)
        if wsum > 1e-12:
            omega_next[k] = np.dot(freqs[freq_slice_start:T], weights) / wsum
        else:
            omega_next[k] = omega_n[k]
        
        # Accumulate for lambda update
        mode_sum += u_hat_plus_next[:, k]
        
        # Convergence diff (skip for very first iterations)
        diff = u_hat_plus_next[:, k] - u_hat_prev[:, k]
        diff_norm += np.real(np.vdot(diff, diff)) / T
    
    # Lambda update
    lambda_next = lambda_hat_n + tau * (mode_sum - f_hat_plus)
    
    return u_hat_plus_next, omega_next, sum_uk, lambda_next, diff_norm


def VMD(f, alpha, tau, K, DC, init, tol, boundary_method='reflect', max_iter=300):
    original_length = len(f)
    if len(f) % 2:  # enforce even length
        f = f[:-1]

    # Boundary handling
    if boundary_method != 'none':
        fMirr, left_ext, right_ext = extend_signal(f, method=boundary_method, extension_ratio=0.3)
    else:
        fMirr = f
        left_ext = right_ext = 0
    
    T = len(fMirr)
    t = np.linspace(0, 1, T)
    freqs = t - 0.5 - 1.0 / T
    
    # FFT of extended signal
    #f_hat = np.fft.fftshift(np.fft.fft(fMirr))
    f_hat = fftw_np.fftshift(fftw_np.fft(fMirr))

    f_hat_plus = f_hat.copy()
    f_hat_plus[:T // 2] = 0
    
    # Allocate small states
    Alpha = alpha * np.ones(K)
    omega_curr = np.zeros(K)
    
    # Init omegas
    if init == 1:
        omega_curr = np.arange(K) * (0.5 / K)
    elif init == 2:
        fs = 1 / T
        omega_curr = np.sort(np.exp(np.log(fs) + (np.log(0.5) - np.log(fs)) * np.random.rand(K)))
    if DC:
        omega_curr[0] = 0.0
    
    lambda_curr = np.zeros(len(freqs), dtype=np.complex128)
    sum_uk = np.zeros(len(freqs), dtype=np.complex128)
    u_hat_prev = np.zeros((len(freqs), K), dtype=np.complex128)
    
    # Iterate with numba core
    half_T = T // 2
    uDiff = tol + 1.0
    iters = 0
    
    for n in range(max_iter):
        u_hat_next, omega_next, sum_uk, lambda_next, diff_norm = update_modes_numba(
            freqs, half_T, f_hat_plus, sum_uk, lambda_curr, Alpha, omega_curr, u_hat_prev, K, tau
        )
        
        # Convergence check
        if n > 5:  # skip first few iterations
            uDiff = diff_norm
        
        # Update for next iteration
        u_hat_prev = u_hat_next
        lambda_curr = lambda_next
        omega_curr = omega_next
        iters = n + 1
        
        if uDiff <= tol:
            break
    
    # Reconstruct u_hat (symmetric)
    u_hat_full = np.zeros((T, K), dtype=np.complex128)
    u_hat_full[half_T:T, :] = u_hat_prev[half_T:T, :]
    idxs = np.arange(1, half_T)
    u_hat_full[idxs, :] = np.conj(u_hat_full[T - idxs, :])
    u_hat_full[0, :] = np.conj(u_hat_full[-1, :])
    
    # IFFT to get modes
    u = np.real(fftw_np.ifft(fftw_np.ifftshift(u_hat_full, axes=0), axis=0)).T
    
    # Remove boundary extension
    if boundary_method != 'none':
        start_idx = left_ext
        end_idx = start_idx + len(f)
        u = u[:, start_idx:end_idx]
    
    # Resize if needed
    if u.shape[1] != original_length:
        from scipy.interpolate import interp1d
        new_u = np.zeros((K, original_length))
        x_old = np.linspace(0, 1, u.shape[1])
        x_new = np.linspace(0, 1, original_length)
        for k in range(K):
            new_u[k, :] = interp1d(x_old, u[k, :], kind='linear', fill_value='extrapolate')(x_new)
        u = new_u
    
    return u, u_hat_full, omega_curr


# ==============================================
# Optimized Helpers
# ==============================================
def get_dominant_frequency(sig, fs):
    N = len(sig)
    if N < 4 or np.allclose(sig, 0, atol=1e-12):
        return 0.0
    freqs = fftw_np.rfftfreq(N, d=1/fs)
    spec = np.abs(fftw_np.rfft(sig))
    if len(spec) == 0:
        return 0.0
    spec[0] = 0  # Remove DC
    return freqs[np.argmax(spec)]

def merge_similar_modes(modes, fs, freq_tol=0.1):
    if len(modes) <= 1:
        return modes
        
    dom_freqs = [get_dominant_frequency(m, fs) for m in modes]
    merged = []
    used = np.zeros(len(modes), dtype=bool)
    
    for i in range(len(modes)):
        if used[i]:
            continue
        group = [modes[i]]
        fi = dom_freqs[i]
        used[i] = True
        
        # Find similar frequencies
        for j in range(i+1, len(modes)):
            if used[j]:
                continue
            fj = dom_freqs[j]
            if abs(fi-fj)/max(fi,1e-6) < freq_tol:
                group.append(modes[j])
                used[j] = True
        
        merged.append(np.sum(group, axis=0))
    return merged

def sort_modes_by_frequency(modes, fs, low_to_high=True):
    dom_freqs = [get_dominant_frequency(m, fs) for m in modes]
    order = np.argsort(dom_freqs)
    if not low_to_high:
        order = order[::-1]
    sorted_modes = [modes[i] for i in order]
    sorted_freqs = [dom_freqs[i] for i in order]
    return sorted_modes, sorted_freqs

def ovmd_cost(modes, signal, fs):
    if len(modes) == 0:
        return 10.0
        
    total_energy = np.sum(signal**2)
    recon = np.sum(modes, axis=0)
    residual_energy = np.sum((signal - recon)**2) / total_energy

    # Optimized overlap penalty
    dom_freqs = [get_dominant_frequency(m, fs) for m in modes]
    if len(dom_freqs) > 1:
        freq_diffs = np.diff(np.sort(dom_freqs))
        overlap_penalty = np.mean(np.exp(-freq_diffs))
    else:
        overlap_penalty = 0.0

    # Optimized entropy calculation
    entropy_vals = []
    for m in modes:
        spec = np.abs(fftw_np.rfft(m)) + 1e-12
        p = spec / np.sum(spec)
        entropy = -np.sum(p * np.log(p)) / np.log(len(spec))
        entropy_vals.append(entropy)
    avg_entropy = np.mean(entropy_vals)

    return 0.7*residual_energy + 0.2*overlap_penalty + 0.1*avg_entropy

# ==============================================
# Optuna-Optimized VMD with Simple Caching
# ==============================================
_cache = {}

def optuna_objective(trial, signal, fs, tau=0.0, DC=0, init=1, tol=1e-6, boundary_method='reflect'):
    K = trial.suggest_int("K", 2, 6)
    alpha = trial.suggest_float("alpha", 500, 5000, log=True)
    
    # Simple cache (only for identical parameters)
    cache_key = (K, round(alpha, -1))  # Round alpha to nearest 10
    if cache_key in _cache:
        modes = _cache[cache_key]
    else:
        try:
            modes, _, _ = VMD(signal, alpha=alpha, tau=tau, K=K, DC=DC, init=init, tol=tol, boundary_method=boundary_method)
            total_energy = np.sum(signal**2)
            modes = [m for m in modes if np.sum(m**2)/total_energy > 0.01]
            if len(_cache) < 50:  # Limit cache size
                _cache[cache_key] = modes
        except:
            return 10.0
    
    if len(modes) == 0:
        return 10.0
    return ovmd_cost(modes, signal, fs)

def optuna_optimized_vmd(signal, fs,
                         n_trials=30,
                         tau=0.0, DC=0, init=1, tol=1e-6,
                         boundary_method='reflect',
                         apply_tapering=True):
    global _cache
    _cache.clear()  # Clear cache for new optimization
    
    def objective_wrapper(trial):
        return optuna_objective(trial, signal, fs, tau, DC, init, tol, boundary_method)

    # Suppress optuna output for speed
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    study = optuna.create_study(direction="minimize")
    study.optimize(objective_wrapper, n_trials=n_trials, show_progress_bar=True, n_jobs=-1)

    best_K = int(study.best_params["K"])
    best_alpha = study.best_params["alpha"]
    best_cost = study.best_value
    print(f"[Fast-VMD] Optimal K={best_K}, alpha={best_alpha:.1f}, cost={best_cost:.4f}")

    # Final decomposition with optimal parameters
    best_modes, _, _ = VMD(signal, alpha=best_alpha, tau=tau, K=best_K, DC=DC, init=init, tol=tol, boundary_method=boundary_method)
    total_energy = np.sum(signal**2)
    best_modes = [m for m in best_modes if np.sum(m**2)/total_energy > 0.01]
    merged_modes = merge_similar_modes(best_modes, fs, freq_tol=0.15)
    sorted_modes, sorted_freqs = sort_modes_by_frequency(merged_modes, fs, low_to_high=True)
    
    # Apply boundary tapering if requested
    if apply_tapering:
        taper_length = min(100, len(signal)//10)  # Adaptive taper length
        sorted_modes = taper_boundaries(sorted_modes, taper_length)
    
    return np.array(sorted_modes), sorted_freqs, (best_K, best_alpha, best_cost)

# ==============================================
# Test Script
# ==============================================
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import time

    # Test signal: trend + 4Hz + 15Hz + 35Hz
    t = np.linspace(0, 8, 1500)
    fs = len(t)/(t[-1]-t[0])
    signal = (0.3*t +
              np.sin(2*np.pi*4*t) +
              0.6*np.sin(2*np.pi*15*t) +
              0.4*np.sin(2*np.pi*35*t) +
              0.05*np.random.normal(size=len(t)))

    print("Running Fast Optuna-VMD with boundary handling...")
    start_time = time.time()
    modes, freqs, params = optuna_optimized_vmd(signal, fs, n_trials=30, 
                                               boundary_method='reflect',
                                               apply_tapering=False)
    elapsed_time = time.time() - start_time
    print(f"Completed in {elapsed_time:.2f} seconds")

    total_energy = np.sum(signal**2)
    fig, axes = plt.subplots(len(modes)+2, 1, figsize=(14, 2.2*(len(modes)+2)))
    axes[0].plot(t, signal, 'b-', alpha=0.8)
    axes[0].set_title("Original Signal")

    for i, (m, f) in enumerate(zip(modes, freqs)):
        e_pct = 100*np.sum(m**2)/total_energy
        axes[i+1].plot(t, m, alpha=0.85)
        axes[i+1].set_title(f"Mode {i+1} | Dom freq ~{f:.2f} Hz | Energy {e_pct:.1f}%")

    recon = np.sum(modes, axis=0)
    axes[-1].plot(t, signal, 'b-', label="Original")
    axes[-1].plot(t, recon, 'r--', label="Reconstructed")
    mse = np.mean((signal - recon)**2)
    axes[-1].legend()
    axes[-1].set_title(f"Reconstruction MSE: {mse:.3e} | Best K={params[0]}, α={params[1]:.1f} | Boundary: reflect+taper")
    plt.tight_layout()
    plt.show()

# %%
# -*- coding: utf-8 -*-
"""
Fast Optuna-Optimized VMD with FFT caching for Optuna trials
"""

import numpy as np
import optuna
import pyfftw
import pyfftw.interfaces.numpy_fft as fftw_np
pyfftw.interfaces.cache.enable()
pyfftw.interfaces.cache.set_keepalive_time(3600)
pyfftw.config.NUM_THREADS = -1  # Use all available cores

from numba import njit, prange

# ==============================================
# Boundary Handling Functions
# ==============================================
def apply_window(signal, window_type='tukey', alpha_win=0.1):
    N = len(signal)
    if window_type == 'tukey':
        from scipy.signal import windows
        window = windows.tukey(N, alpha_win)
    elif window_type == 'hann':
        window = np.hanning(N)
    elif window_type == 'hamming':
        window = np.hamming(N)
    else:
        window = np.ones(N)
    return signal * window, window

def extend_signal(signal, method='mirror', extension_ratio=0.25):
    N = len(signal)
    ext_len = int(N * extension_ratio)
    if method == 'mirror':
        left_ext = signal[1:ext_len+1][::-1]
        right_ext = signal[-(ext_len+1):-1][::-1]
        extended = np.concatenate([left_ext, signal, right_ext])
    elif method == 'reflect':
        left_val = signal[0]
        right_val = signal[-1]
        left_ext = 2*left_val - signal[1:ext_len+1][::-1]
        right_ext = 2*right_val - signal[-(ext_len+1):-1][::-1]
        extended = np.concatenate([left_ext, signal, right_ext])
    elif method == 'linear':
        left_slope = (signal[1] - signal[0])
        right_slope = (signal[-1] - signal[-2])
        left_ext = signal[0] + left_slope * np.arange(-ext_len, 0)
        right_ext = signal[-1] + right_slope * np.arange(1, ext_len+1)
        extended = np.concatenate([left_ext, signal, right_ext])
    elif method == 'constant':
        left_ext = np.full(ext_len, signal[0])
        right_ext = np.full(ext_len, signal[-1])
        extended = np.concatenate([left_ext, signal, right_ext])
    else:
        return signal, 0, 0
    return extended, ext_len, ext_len

def taper_boundaries(modes, taper_length=50):
    tapered_modes = []
    for mode in modes:
        tapered = mode.copy()
        N = len(mode)
        taper_len = min(taper_length, N//4)
        taper = np.ones(N)
        taper[:taper_len] = np.sin(np.linspace(0, np.pi/2, taper_len))**2
        taper[-taper_len:] = np.cos(np.linspace(0, np.pi/2, taper_len))**2
        tapered_modes.append(tapered * taper)
    return tapered_modes

# ==============================================
# Numba Inner Loop
# ==============================================
@njit(parallel=True, fastmath=True)
def update_modes_numba(freqs, half_T, f_hat_plus, sum_uk,
                       lambda_hat_n, Alpha, omega_n, u_hat_prev, K, tau):
    T = len(freqs)
    freq_slice_start = half_T
    u_hat_plus_next = np.zeros((T, K), dtype=np.complex128)
    omega_next = np.zeros(K)
    mode_sum = np.zeros(T, dtype=np.complex128)
    diff_norm = 0.0
    eps = 1e-14  # ✅ stability

    for k in range(K):
        if k == 0:
            sum_uk += u_hat_prev[:, K - 1] - u_hat_prev[:, 0]
        else:
            sum_uk += u_hat_plus_next[:, k - 1] - u_hat_prev[:, k]

        freq_diff = freqs - omega_n[k]
        denom = 1.0 + Alpha[k] * freq_diff * freq_diff + eps  # ✅ stable
        u_hat_plus_next[:, k] = (f_hat_plus - sum_uk - lambda_hat_n * 0.5) / denom

        u_slice = u_hat_plus_next[freq_slice_start:T, k]
        weights = np.abs(u_slice) ** 2
        wsum = np.sum(weights)
        if wsum > eps:
            omega_next[k] = np.dot(freqs[freq_slice_start:T], weights) / wsum
        else:
            omega_next[k] = omega_n[k]

        mode_sum += u_hat_plus_next[:, k]
        diff = u_hat_plus_next[:, k] - u_hat_prev[:, k]
        diff_norm += np.real(np.vdot(diff, diff)) / T

    lambda_next = lambda_hat_n + tau * (mode_sum - f_hat_plus)
    return u_hat_plus_next, omega_next, sum_uk, lambda_next, diff_norm

# ==============================================
# Precompute FFT+Boundary for all trials
# ==============================================

def smooth_edge_junction(extended_signal, original_len, ext_len, smooth_ratio=0.02):
    """
    Smooth the junction between mirrored edges and original signal with a tiny cosine ramp.
    smooth_ratio=0.02 means 2% of signal length at each junction.
    """
    N = len(extended_signal)
    taper_len = max(2, int(original_len * smooth_ratio))

    # Cosine ramps
    ramp_up = 0.5 * (1 - np.cos(np.linspace(0, np.pi, taper_len)))
    ramp_down = ramp_up[::-1]

    # Left junction
    extended_signal[ext_len - taper_len:ext_len] *= ramp_up
    # Right junction
    end_idx = ext_len + original_len
    extended_signal[end_idx:end_idx + taper_len] *= ramp_down
    return extended_signal

def adaptive_extension_ratio(signal):
    N = len(signal)
    # shorter extension for long signals, longer for very short signals
    if N < 500:
        return 0.4
    elif N < 2000:
        return 0.3
    else:
        return 0.2


def auto_window_alpha(signal, min_alpha=0.01, max_alpha=0.1):
    """
    Adaptive Tukey window alpha based on derivative variance.
    
    - Highly oscillatory signals -> smaller alpha (less windowing)
    - Smooth signals -> larger alpha (more windowing)
    """
    deriv = np.diff(signal)
    deriv_var = np.var(deriv)

    # Normalize variance to a reasonable range
    norm_var = deriv_var / (np.mean(np.abs(signal))**2 + 1e-12)

    # Map normalized variance to [min_alpha, max_alpha]
    # More oscillation (large norm_var) => closer to min_alpha
    # Smoother signals (small norm_var) => closer to max_alpha
    smoothness_factor = 1.0 / (1.0 + norm_var)  # ~0 for noisy, ~1 for smooth
    alpha = min_alpha + (max_alpha - min_alpha) * smoothness_factor

    return alpha


def precompute_vmd_fft(signal, boundary_method='reflect', use_soft_junction=False, window_alpha=None):
    orig_len = len(signal)
    if len(signal) % 2:
        signal = signal[:-1]

    # normal extension
    if boundary_method != 'none':
        ratio = adaptive_extension_ratio(signal)
        fMirr, left_ext, right_ext = extend_signal(signal, method=boundary_method, extension_ratio=ratio)
    else:
        fMirr = signal
        left_ext = right_ext = 0

    # ✅ NEW: soft junction smoothing
    if use_soft_junction and boundary_method != 'none':
        fMirr = smooth_edge_junction(fMirr, orig_len, left_ext, smooth_ratio=0.02)

    if window_alpha is None:
        window_alpha = auto_window_alpha(signal)

    # ✅ NEW: apply very light Tukey window before FFT
    if window_alpha > 0:
        from scipy.signal import windows
        win = windows.tukey(len(fMirr), alpha=window_alpha)
        fMirr = fMirr * win

    # ✅ NEW: safer frequency grid
    T = len(fMirr)
    freqs = np.fft.fftshift(np.fft.fftfreq(T))  # more numerically consistent
    f_hat = fftw_np.fftshift(fftw_np.fft(fMirr))
    f_hat_plus = f_hat.copy()
    f_hat_plus[:T // 2] = 0

    return {
        "f_hat_plus": f_hat_plus,
        "freqs": freqs,
        "T": T,
        "half_T": T // 2,
        "orig_len": orig_len,
        "left_ext": left_ext,
        "right_ext": right_ext
    }

def init_from_spectrum(signal, K):
    """
    Initialize omega_curr from the K largest FFT peaks.
    """
    spec = np.abs(fftw_np.rfft(signal))
    freqs = fftw_np.rfftfreq(len(signal))
    peak_idx = np.argsort(spec)[-K:]  # largest K peaks
    return np.sort(freqs[peak_idx])

def smart_init_omega(signal, K, method='spectral'):
    """Fast spectral initialization"""
    if method == 'spectral':
        # Quick FFT-based initialization
        spec = np.abs(fftw_np.rfft(signal))
        freqs = fftw_np.rfftfreq(len(signal))
        
        # Find K largest peaks efficiently
        if K >= len(spec):
            return np.linspace(0, 0.5, K)
        
        peak_idx = np.argpartition(spec, -K)[-K:]
        return np.sort(freqs[peak_idx])
    else:
        return np.linspace(0, 0.5, K)
    
# ==============================================
# VMD Core (can use cached FFT)
# ==============================================
def VMD(f, alpha, tau, K, DC, init, tol,
        boundary_method='reflect', max_iter=300,
        precomputed_fft=None,
        trial=None):  # <-- now accepts trial
    # If we have a precomputed cache, use it
    if precomputed_fft is not None:
        f_hat_plus = precomputed_fft["f_hat_plus"]
        freqs = precomputed_fft["freqs"]
        T = precomputed_fft["T"]
        half_T = precomputed_fft["half_T"]
        orig_len = precomputed_fft["orig_len"]
        left_ext = precomputed_fft["left_ext"]
        right_ext = precomputed_fft["right_ext"]
    else:
        # Normal path: compute FFT and boundaries
        orig_len = len(f)
        if len(f) % 2:
            f = f[:-1]
        if boundary_method != 'none':
            fMirr, left_ext, right_ext = extend_signal(f, method=boundary_method, extension_ratio=0.3)
        else:
            fMirr = f
            left_ext = right_ext = 0
        T = len(fMirr)
        freqs = np.linspace(0, 1, T) - 0.5 - 1.0/T
        f_hat = fftw_np.fftshift(fftw_np.fft(fMirr))
        f_hat_plus = f_hat.copy()
        f_hat_plus[:T // 2] = 0
        half_T = T // 2

    Alpha = alpha * np.ones(K)
    omega_curr = np.zeros(K)
    if init == 1:
        omega_curr = np.arange(K) * (0.5 / K)
    elif init == 2:
        fs = 1 / T
        omega_curr = np.sort(np.exp(np.log(fs) + (np.log(0.5) - np.log(fs)) * np.random.rand(K)))
    elif init == 3:  # new mode: spectral init
        omega_curr = smart_init_omega(f if f is not None else np.random.randn(orig_len), K)
    if DC:
        omega_curr[0] = 0.0
    lambda_curr = np.zeros(len(freqs), dtype=np.complex128)
    sum_uk = np.zeros(len(freqs), dtype=np.complex128)
    u_hat_prev = np.zeros((len(freqs), K), dtype=np.complex128)
    uDiff = tol + 1.0
    for n in range(max_iter):
        u_hat_next, omega_next, sum_uk, lambda_next, diff_norm = update_modes_numba(
            freqs, half_T, f_hat_plus, sum_uk, lambda_curr, Alpha, omega_curr, u_hat_prev, K, tau
        )
        if n > 5:
            uDiff = diff_norm

        # ✅ Report intermediate value to Optuna for pruning
        if trial is not None and n % 10 == 0:
            trial.report(uDiff, step=n)
            if trial.should_prune():
                raise optuna.TrialPruned()
        u_hat_prev = u_hat_next
        lambda_curr = lambda_next
        omega_curr = omega_next
        if uDiff <= tol:
            break

    # symmetric reconstruction
    u_hat_full = np.zeros((T, K), dtype=np.complex128)
    u_hat_full[half_T:T, :] = u_hat_prev[half_T:T, :]
    idxs = np.arange(1, half_T)
    u_hat_full[idxs, :] = np.conj(u_hat_full[T - idxs, :])
    u_hat_full[0, :] = np.conj(u_hat_full[-1, :])
    # Inverse FFT to time domain
    u = np.real(fftw_np.ifft(fftw_np.ifftshift(u_hat_full, axes=0), axis=0)).T

    if precomputed_fft is not None or boundary_method != 'none':
        start_idx = left_ext
        end_idx = start_idx + orig_len
        u = u[:, start_idx:end_idx]

    if u.shape[1] != orig_len:
        # old time grid (normalized 0..1)
        x_old = np.linspace(0, 1, u.shape[1])
        # new time grid (target length)
        x_new = np.linspace(0, 1, orig_len)
        
        # vectorized interpolation: apply np.interp for each mode row
        u = np.vstack([np.interp(x_new, x_old, mode) for mode in u])

    return u, u_hat_full, omega_curr

# ==============================================
# Helpers
# ==============================================
def get_dominant_frequency(sig, fs):
    N = len(sig)
    if N < 4 or np.allclose(sig, 0, atol=1e-12):
        return 0.0
    freqs = fftw_np.rfftfreq(N, d=1/fs)
    spec = np.abs(fftw_np.rfft(sig))
    if len(spec) == 0:
        return 0.0
    spec[0] = 0
    return freqs[np.argmax(spec)]

def merge_similar_modes(modes, fs, freq_tol=0.1):
    if len(modes) <= 1:
        return modes
    dom_freqs = [get_dominant_frequency(m, fs) for m in modes]
    merged = []
    used = np.zeros(len(modes), dtype=bool)
    for i in range(len(modes)):
        if used[i]:
            continue
        group = [modes[i]]
        fi = dom_freqs[i]
        used[i] = True
        for j in range(i+1, len(modes)):
            if used[j]:
                continue
            fj = dom_freqs[j]
            if abs(fi-fj)/max(fi,1e-6) < freq_tol:
                group.append(modes[j])
                used[j] = True
        merged.append(np.sum(group, axis=0))
    return merged

def sort_modes_by_frequency(modes, fs, low_to_high=True):
    dom_freqs = [get_dominant_frequency(m, fs) for m in modes]
    order = np.argsort(dom_freqs)
    if not low_to_high:
        order = order[::-1]
    return [modes[i] for i in order], [dom_freqs[i] for i in order]

def ovmd_cost(modes, signal, fs):
    if len(modes) == 0:
        return 10.0
    total_energy = np.sum(signal**2)
    recon = np.sum(modes, axis=0)
    residual_energy = np.sum((signal - recon)**2) / total_energy
    dom_freqs = [get_dominant_frequency(m, fs) for m in modes]
    overlap_penalty = np.mean(np.exp(-np.diff(np.sort(dom_freqs)))) if len(dom_freqs) > 1 else 0.0
    entropy_vals = []
    for m in modes:
        spec = np.abs(fftw_np.rfft(m)) + 1e-12
        p = spec / np.sum(spec)
        entropy_vals.append(-np.sum(p * np.log(p)) / np.log(len(spec)))
    avg_entropy = np.mean(entropy_vals)
    return 0.7*residual_energy + 0.2*overlap_penalty + 0.1*avg_entropy

# ==============================================
# Optuna with FFT Cache
# ==============================================
_cache = {}
def optuna_objective(trial, signal, fs, precomputed_fft,
                     tau=0.0, DC=0, init=1, tol=1e-6):
    K = trial.suggest_int("K", 2, 6)
    alpha = trial.suggest_float("alpha", 500, 5000, log=True)
    cache_key = (K, round(alpha, -1))
    if cache_key in _cache:
        modes = _cache[cache_key]
    else:
        try:
            modes, _, _ = VMD(None, alpha=alpha, tau=tau, K=K,
                              DC=DC, init=init, tol=tol,
                              precomputed_fft=precomputed_fft,
                              trial=trial)  # <-- pass trial here
            total_energy = np.sum(signal**2)
            modes = [m for m in modes if np.sum(m**2)/total_energy > 0.01]
            if len(_cache) < 50:
                _cache[cache_key] = modes
        except optuna.TrialPruned:
            raise  # propagate pruning
        except:
            return 10.0
    if len(modes) == 0:
        return 10.0
    return ovmd_cost(modes, signal, fs)

def optuna_optimized_vmd(signal, fs,
                         n_trials=30,
                         tau=0.0, DC=0, init=1, tol=1e-6,
                         boundary_method='reflect',
                         apply_tapering=True):
    global _cache
    _cache.clear()
    # Precompute FFT once for all trials
    precomputed_fft = precompute_vmd_fft(signal, boundary_method)
    def objective_wrapper(trial):
        return optuna_objective(trial, signal, fs, precomputed_fft, tau, DC, init, tol)
    # ✅ Enable pruning
    pruner = optuna.pruners.MedianPruner(n_warmup_steps=5)
    study = optuna.create_study(direction="minimize", pruner=pruner)
    study.optimize(objective_wrapper, n_trials=n_trials, show_progress_bar=True, n_jobs=-1)
    best_K = int(study.best_params["K"])
    best_alpha = study.best_params["alpha"]
    best_cost = study.best_value
    print(f"[Fast-VMD] Optimal K={best_K}, alpha={best_alpha:.1f}, cost={best_cost:.4f}")
    best_modes, _, _ = VMD(None, alpha=best_alpha, tau=tau, K=best_K,
                           DC=DC, init=init, tol=tol,
                           precomputed_fft=precomputed_fft)
    total_energy = np.sum(signal**2)
    best_modes = [m for m in best_modes if np.sum(m**2)/total_energy > 0.01]
    merged_modes = merge_similar_modes(best_modes, fs, freq_tol=0.15)
    sorted_modes, sorted_freqs = sort_modes_by_frequency(merged_modes, fs, low_to_high=True)
    if apply_tapering:
        taper_len = min(100, len(signal)//10)
        sorted_modes = taper_boundaries(sorted_modes, taper_len)
    return np.array(sorted_modes), sorted_freqs, (best_K, best_alpha, best_cost)
# ==============================================
# Test Script
# ==============================================
if __name__ == "__main__":
    import matplotlib.pyplot as plt, time
    t = np.linspace(0, 8, 1500)
    fs = len(t)/(t[-1]-t[0])
    signal = (0.3*t +
              np.sin(2*np.pi*4*t) +
              0.6*np.sin(2*np.pi*15*t) +
              0.4*np.sin(2*np.pi*35*t) +
              0.05*np.random.normal(size=len(t)))
    print("Running Fast Optuna-VMD with FFT caching...")
    start_time = time.time()
    modes, freqs, params = optuna_optimized_vmd(signal, fs, n_trials=20,
                                                boundary_method='reflect',
                                                apply_tapering=False)
    elapsed = time.time() - start_time
    print(f"Completed in {elapsed:.2f}s")
    total_energy = np.sum(signal**2)
    fig, axes = plt.subplots(len(modes)+2, 1, figsize=(14, 2.2*(len(modes)+2)))
    axes[0].plot(t, signal, 'b-', alpha=0.8)
    axes[0].set_title("Original Signal")
    for i, (m, f) in enumerate(zip(modes, freqs)):
        e_pct = 100*np.sum(m**2)/total_energy
        axes[i+1].plot(t, m, alpha=0.85)
        axes[i+1].set_title(f"Mode {i+1} | Dom freq ~{f:.2f} Hz | Energy {e_pct:.1f}%")
    recon = np.sum(modes, axis=0)
    axes[-1].plot(t, signal, 'b-', label="Original")
    axes[-1].plot(t, recon, 'r--', label="Reconstructed")
    mse = np.mean((signal - recon)**2)
    axes[-1].legend()
    axes[-1].set_title(f"Reconstruction MSE: {mse:.3e} | Best K={params[0]}, α={params[1]:.1f}")
    plt.tight_layout()
    plt.show()


# %%
# -*- coding: utf-8 -*-
"""
Fast Optuna-Optimized VMD with FFT caching for Optuna trials - Performance Enhanced
"""

import numpy as np
import optuna
import pyfftw
import pyfftw.interfaces.numpy_fft as fftw_np
pyfftw.interfaces.cache.enable()
pyfftw.interfaces.cache.set_keepalive_time(3600)

from numba import njit, prange

# ==============================================
# Boundary Handling Functions (UNCHANGED)
# ==============================================
def apply_window(signal, window_type='tukey', alpha_win=0.1):
    N = len(signal)
    if window_type == 'tukey':
        from scipy.signal import windows
        window = windows.tukey(N, alpha_win)
    elif window_type == 'hann':
        window = np.hanning(N)
    elif window_type == 'hamming':
        window = np.hamming(N)
    else:
        window = np.ones(N)
    return signal * window, window

def extend_signal(signal, method='mirror', extension_ratio=0.25):
    N = len(signal)
    ext_len = int(N * extension_ratio)
    if method == 'mirror':
        left_ext = signal[1:ext_len+1][::-1]
        right_ext = signal[-(ext_len+1):-1][::-1]
        extended = np.concatenate([left_ext, signal, right_ext])
    elif method == 'reflect':
        left_val = signal[0]
        right_val = signal[-1]
        left_ext = 2*left_val - signal[1:ext_len+1][::-1]
        right_ext = 2*right_val - signal[-(ext_len+1):-1][::-1]
        extended = np.concatenate([left_ext, signal, right_ext])
    elif method == 'linear':
        left_slope = (signal[1] - signal[0])
        right_slope = (signal[-1] - signal[-2])
        left_ext = signal[0] + left_slope * np.arange(-ext_len, 0)
        right_ext = signal[-1] + right_slope * np.arange(1, ext_len+1)
        extended = np.concatenate([left_ext, signal, right_ext])
    elif method == 'constant':
        left_ext = np.full(ext_len, signal[0])
        right_ext = np.full(ext_len, signal[-1])
        extended = np.concatenate([left_ext, signal, right_ext])
    else:
        return signal, 0, 0
    return extended, ext_len, ext_len

def taper_boundaries(modes, taper_length=50):
    tapered_modes = []
    for mode in modes:
        tapered = mode.copy()
        N = len(mode)
        taper_len = min(taper_length, N//4)
        taper = np.ones(N)
        taper[:taper_len] = np.sin(np.linspace(0, np.pi/2, taper_len))**2
        taper[-taper_len:] = np.cos(np.linspace(0, np.pi/2, taper_len))**2
        tapered_modes.append(tapered * taper)
    return tapered_modes

# ==============================================
# Enhanced Numba Inner Loop with Optimizations
# ==============================================
@njit(parallel=True, fastmath=True)
def update_modes_numba(freqs, half_T, f_hat_plus, sum_uk,
                       lambda_hat_n, Alpha, omega_n, u_hat_prev, K, tau):
    T = len(freqs)
    freq_slice_start = half_T
    u_hat_plus_next = np.zeros((T, K), dtype=np.complex128)
    omega_next = np.zeros(K)
    mode_sum = np.zeros(T, dtype=np.complex128)
    diff_norm = 0.0
    eps = 1e-14  # ✅ stability

    # 🚀 OPTIMIZATION: Pre-compute squared frequencies for stability
    freq_sq = freqs * freqs
    
    for k in range(K):
        if k == 0:
            sum_uk += u_hat_prev[:, K - 1] - u_hat_prev[:, 0]
        else:
            sum_uk += u_hat_plus_next[:, k - 1] - u_hat_prev[:, k]

        # 🚀 OPTIMIZATION: Vectorized computation with pre-computed squares
        omega_k = omega_n[k]
        alpha_k = Alpha[k]
        
        for i in range(T):
            freq_diff = freqs[i] - omega_k
            denom = 1.0 + alpha_k * freq_diff * freq_diff + eps  # ✅ stable
            u_hat_plus_next[i, k] = (f_hat_plus[i] - sum_uk[i] - lambda_hat_n[i] * 0.5) / denom

        # 🚀 OPTIMIZATION: More efficient frequency update
        numerator = 0.0
        denominator = 0.0
        for i in range(freq_slice_start, T):
            weight = u_hat_plus_next[i, k].real**2 + u_hat_plus_next[i, k].imag**2
            numerator += freqs[i] * weight
            denominator += weight
        
        if denominator > eps:
            omega_next[k] = numerator / denominator
        else:
            omega_next[k] = omega_k

        mode_sum += u_hat_plus_next[:, k]
        diff = u_hat_plus_next[:, k] - u_hat_prev[:, k]
        diff_norm += np.real(np.vdot(diff, diff)) / T

    lambda_next = lambda_hat_n + tau * (mode_sum - f_hat_plus)
    return u_hat_plus_next, omega_next, sum_uk, lambda_next, diff_norm

# ==============================================
# Precompute FFT+Boundary for all trials (ENHANCED)
# ==============================================

def smooth_edge_junction(extended_signal, original_len, ext_len, smooth_ratio=0.02):
    """
    Smooth the junction between mirrored edges and original signal with a tiny cosine ramp.
    smooth_ratio=0.02 means 2% of signal length at each junction.
    """
    N = len(extended_signal)
    taper_len = max(2, int(original_len * smooth_ratio))

    # Cosine ramps
    ramp_up = 0.5 * (1 - np.cos(np.linspace(0, np.pi, taper_len)))
    ramp_down = ramp_up[::-1]

    # Left junction
    extended_signal[ext_len - taper_len:ext_len] *= ramp_up
    # Right junction
    end_idx = ext_len + original_len
    extended_signal[end_idx:end_idx + taper_len] *= ramp_down
    return extended_signal

def adaptive_extension_ratio(signal):
    N = len(signal)
    # 🚀 OPTIMIZATION: More aggressive ratio reduction for speed
    if N < 500:
        return 0.3  # Reduced from 0.4
    elif N < 2000:
        return 0.2  # Reduced from 0.3
    else:
        return 0.15  # Reduced from 0.2

def auto_window_alpha(signal, min_alpha=0.01, max_alpha=0.1):
    """
    Adaptive Tukey window alpha based on derivative variance.
    
    - Highly oscillatory signals -> smaller alpha (less windowing)
    - Smooth signals -> larger alpha (more windowing)
    """
    deriv = np.diff(signal)
    deriv_var = np.var(deriv)

    # Normalize variance to a reasonable range
    norm_var = deriv_var / (np.mean(np.abs(signal))**2 + 1e-12)

    # Map normalized variance to [min_alpha, max_alpha]
    # More oscillation (large norm_var) => closer to min_alpha
    # Smoother signals (small norm_var) => closer to max_alpha
    smoothness_factor = 1.0 / (1.0 + norm_var)  # ~0 for noisy, ~1 for smooth
    alpha = min_alpha + (max_alpha - min_alpha) * smoothness_factor

    return alpha

def precompute_vmd_fft(signal, boundary_method='reflect', use_soft_junction=True, window_alpha=None):
    orig_len = len(signal)
    if len(signal) % 2:
        signal = signal[:-1]

    # normal extension
    if boundary_method != 'none':
        ratio = adaptive_extension_ratio(signal)
        fMirr, left_ext, right_ext = extend_signal(signal, method=boundary_method, extension_ratio=ratio)
    else:
        fMirr = signal
        left_ext = right_ext = 0

    # ✅ NEW: soft junction smoothing
    if use_soft_junction and boundary_method != 'none':
        fMirr = smooth_edge_junction(fMirr, orig_len, left_ext, smooth_ratio=0.02)

    if window_alpha is None:
        window_alpha = auto_window_alpha(signal)

    # ✅ NEW: apply very light Tukey window before FFT
    if window_alpha > 0:
        from scipy.signal import windows
        win = windows.tukey(len(fMirr), alpha=window_alpha)
        fMirr = fMirr * win

    # ✅ NEW: safer frequency grid
    T = len(fMirr)
    freqs = np.fft.fftshift(np.fft.fftfreq(T))  # more numerically consistent
    f_hat = fftw_np.fftshift(fftw_np.fft(fMirr))
    f_hat_plus = f_hat.copy()
    f_hat_plus[:T // 2] = 0

    return {
        "f_hat_plus": f_hat_plus,
        "freqs": freqs,
        "T": T,
        "half_T": T // 2,
        "orig_len": orig_len,
        "left_ext": left_ext,
        "right_ext": right_ext
    }

def init_from_spectrum(signal, K):
    """
    Initialize omega_curr from the K largest FFT peaks.
    """
    spec = np.abs(fftw_np.rfft(signal))
    freqs = fftw_np.rfftfreq(len(signal))
    peak_idx = np.argsort(spec)[-K:]  # largest K peaks
    return np.sort(freqs[peak_idx])

# ==============================================
# VMD Core with Performance Optimizations
# ==============================================
def VMD(f, alpha, tau, K, DC, init, tol,
        boundary_method='reflect', max_iter=300,
        precomputed_fft=None,
        trial=None):  # <-- now accepts trial
    # If we have a precomputed cache, use it
    if precomputed_fft is not None:
        f_hat_plus = precomputed_fft["f_hat_plus"]
        freqs = precomputed_fft["freqs"]
        T = precomputed_fft["T"]
        half_T = precomputed_fft["half_T"]
        orig_len = precomputed_fft["orig_len"]
        left_ext = precomputed_fft["left_ext"]
        right_ext = precomputed_fft["right_ext"]
    else:
        # Normal path: compute FFT and boundaries
        orig_len = len(f)
        if len(f) % 2:
            f = f[:-1]
        if boundary_method != 'none':
            fMirr, left_ext, right_ext = extend_signal(f, method=boundary_method, extension_ratio=0.3)
        else:
            fMirr = f
            left_ext = right_ext = 0
        T = len(fMirr)
        freqs = np.linspace(0, 1, T) - 0.5 - 1.0/T
        f_hat = fftw_np.fftshift(fftw_np.fft(fMirr))
        f_hat_plus = f_hat.copy()
        f_hat_plus[:T // 2] = 0
        half_T = T // 2

    Alpha = alpha * np.ones(K)
    omega_curr = np.zeros(K)
    if init == 1:
        omega_curr = np.arange(K) * (0.5 / K)
    elif init == 2:
        fs = 1 / T
        omega_curr = np.sort(np.exp(np.log(fs) + (np.log(0.5) - np.log(fs)) * np.random.rand(K)))
    elif init == 3:  # new mode: spectral init
        omega_curr = init_from_spectrum(fMirr if 'fMirr' in locals() else f, K)
    if DC:
        omega_curr[0] = 0.0
    lambda_curr = np.zeros(len(freqs), dtype=np.complex128)
    sum_uk = np.zeros(len(freqs), dtype=np.complex128)
    u_hat_prev = np.zeros((len(freqs), K), dtype=np.complex128)
    uDiff = tol + 1.0
    
    # 🚀 OPTIMIZATION: Early stopping variables
    stagnation_count = 0
    prev_diff = float('inf')
    adaptive_tol = max(tol, 1e-7)  # Slightly relaxed for speed
    
    for n in range(max_iter):
        u_hat_next, omega_next, sum_uk, lambda_next, diff_norm = update_modes_numba(
            freqs, half_T, f_hat_plus, sum_uk, lambda_curr, Alpha, omega_curr, u_hat_prev, K, tau
        )
        if n > 5:
            uDiff = diff_norm

        # 🚀 OPTIMIZATION: Smart early stopping
        if n > 10:
            if abs(diff_norm - prev_diff) < adaptive_tol * 0.1:
                stagnation_count += 1
            else:
                stagnation_count = 0
            
            # Early termination if stagnating
            if stagnation_count >= 5:
                break

        # ✅ Report intermediate value to Optuna for pruning (less frequent for speed)
        if trial is not None and n % 15 == 0:  # Reduced from 10 to 15
            trial.report(uDiff, step=n)
            if trial.should_prune():
                raise optuna.TrialPruned()
        
        u_hat_prev = u_hat_next
        lambda_curr = lambda_next
        omega_curr = omega_next
        prev_diff = diff_norm
        
        if uDiff <= tol:
            break

    # symmetric reconstruction
    u_hat_full = np.zeros((T, K), dtype=np.complex128)
    u_hat_full[half_T:T, :] = u_hat_prev[half_T:T, :]
    idxs = np.arange(1, half_T)
    u_hat_full[idxs, :] = np.conj(u_hat_full[T - idxs, :])
    u_hat_full[0, :] = np.conj(u_hat_full[-1, :])
    # Inverse FFT to time domain
    u = np.real(fftw_np.ifft(fftw_np.ifftshift(u_hat_full, axes=0), axis=0)).T

    if precomputed_fft is not None or boundary_method != 'none':
        start_idx = left_ext
        end_idx = start_idx + orig_len
        u = u[:, start_idx:end_idx]

    if u.shape[1] != orig_len:
        # old time grid (normalized 0..1)
        x_old = np.linspace(0, 1, u.shape[1])
        # new time grid (target length)
        x_new = np.linspace(0, 1, orig_len)
        
        # vectorized interpolation: apply np.interp for each mode row
        u = np.vstack([np.interp(x_new, x_old, mode) for mode in u])

    return u, u_hat_full, omega_curr

# ==============================================
# Helpers (UNCHANGED but with minor optimizations)
# ==============================================
def get_dominant_frequency(sig, fs):
    N = len(sig)
    if N < 4 or np.allclose(sig, 0, atol=1e-12):
        return 0.0
    freqs = fftw_np.rfftfreq(N, d=1/fs)
    spec = np.abs(fftw_np.rfft(sig))
    if len(spec) == 0:
        return 0.0
    spec[0] = 0
    return freqs[np.argmax(spec)]

def merge_similar_modes(modes, fs, freq_tol=0.1):
    if len(modes) <= 1:
        return modes
    dom_freqs = [get_dominant_frequency(m, fs) for m in modes]
    merged = []
    used = np.zeros(len(modes), dtype=bool)
    for i in range(len(modes)):
        if used[i]:
            continue
        group = [modes[i]]
        fi = dom_freqs[i]
        used[i] = True
        for j in range(i+1, len(modes)):
            if used[j]:
                continue
            fj = dom_freqs[j]
            if abs(fi-fj)/max(fi,1e-6) < freq_tol:
                group.append(modes[j])
                used[j] = True
        merged.append(np.sum(group, axis=0))
    return merged

def sort_modes_by_frequency(modes, fs, low_to_high=True):
    dom_freqs = [get_dominant_frequency(m, fs) for m in modes]
    order = np.argsort(dom_freqs)
    if not low_to_high:
        order = order[::-1]
    return [modes[i] for i in order], [dom_freqs[i] for i in order]

def ovmd_cost(modes, signal, fs):
    if len(modes) == 0:
        return 10.0
    total_energy = np.sum(signal**2)
    recon = np.sum(modes, axis=0)
    residual_energy = np.sum((signal - recon)**2) / total_energy
    dom_freqs = [get_dominant_frequency(m, fs) for m in modes]
    overlap_penalty = np.mean(np.exp(-np.diff(np.sort(dom_freqs)))) if len(dom_freqs) > 1 else 0.0
    
    # 🚀 OPTIMIZATION: Simplified entropy calculation
    entropy_vals = []
    for m in modes:
        spec = np.abs(fftw_np.rfft(m)) + 1e-12
        p = spec / np.sum(spec)
        # Faster entropy approximation
        entropy_vals.append(-np.mean(p * np.log(p + 1e-12)))
    avg_entropy = np.mean(entropy_vals) / np.log(len(modes) + 1)  # Normalized
    
    return 0.7*residual_energy + 0.2*overlap_penalty + 0.1*avg_entropy

# ==============================================
# Enhanced Optuna with Better Caching
# ==============================================
_cache = {}
def optuna_objective(trial, signal, fs, precomputed_fft,
                     tau=0.0, DC=0, init=1, tol=1e-6):
    K = trial.suggest_int("K", 2, 6)
    alpha = trial.suggest_float("alpha", 500, 5000, log=True)
    
    # 🚀 OPTIMIZATION: Smarter caching with rounded alpha
    cache_key = (K, round(alpha, -1))  # Round to nearest 10
    if cache_key in _cache:
        modes = _cache[cache_key]
    else:
        try:
            modes, _, _ = VMD(None, alpha=alpha, tau=tau, K=K,
                              DC=DC, init=init, tol=tol,
                              precomputed_fft=precomputed_fft,
                              trial=trial)  # <-- pass trial here
            total_energy = np.sum(signal**2)
            modes = [m for m in modes if np.sum(m**2)/total_energy > 0.01]
            
            # 🚀 OPTIMIZATION: Better cache management
            if len(_cache) < 40:  # Slightly larger cache
                _cache[cache_key] = modes
        except optuna.TrialPruned:
            raise  # propagate pruning
        except:
            return 10.0
    if len(modes) == 0:
        return 10.0
    return ovmd_cost(modes, signal, fs)

def optuna_optimized_vmd(signal, fs,
                         n_trials=30,
                         tau=0.0, DC=0, init=1, tol=1e-6,
                         boundary_method='reflect',
                         apply_tapering=True):
    global _cache
    _cache.clear()
    
    # 🚀 OPTIMIZATION: Smart trial reduction for long signals
    if len(signal) > 2000:
        n_trials = max(15, n_trials // 2)  # Reduce trials for long signals
    
    # Precompute FFT once for all trials
    precomputed_fft = precompute_vmd_fft(signal, boundary_method)
    def objective_wrapper(trial):
        return optuna_objective(trial, signal, fs, precomputed_fft, tau, DC, init, tol)
    
    # ✅ Enable pruning with better settings
    pruner = optuna.pruners.MedianPruner(
        n_warmup_steps=3,  # Reduced from 5
        n_startup_trials=5
    )
    study = optuna.create_study(direction="minimize", pruner=pruner)
    study.optimize(objective_wrapper, n_trials=n_trials, show_progress_bar=True, n_jobs=-1)
    
    best_K = int(study.best_params["K"])
    best_alpha = study.best_params["alpha"]
    best_cost = study.best_value
    print(f"[Fast-VMD] Optimal K={best_K}, alpha={best_alpha:.1f}, cost={best_cost:.4f}")
    best_modes, _, _ = VMD(None, alpha=best_alpha, tau=tau, K=best_K,
                           DC=DC, init=init, tol=tol,
                           precomputed_fft=precomputed_fft)
    total_energy = np.sum(signal**2)
    best_modes = [m for m in best_modes if np.sum(m**2)/total_energy > 0.01]
    merged_modes = merge_similar_modes(best_modes, fs, freq_tol=0.15)
    sorted_modes, sorted_freqs = sort_modes_by_frequency(merged_modes, fs, low_to_high=True)
    if apply_tapering:
        taper_len = min(100, len(signal)//10)
        sorted_modes = taper_boundaries(sorted_modes, taper_len)
    return np.array(sorted_modes), sorted_freqs, (best_K, best_alpha, best_cost)

# ==============================================
# Test Script (UNCHANGED)
# ==============================================
if __name__ == "__main__":
    import matplotlib.pyplot as plt, time
    t = np.linspace(0, 8, 1500)
    fs = len(t)/(t[-1]-t[0])
    signal = (0.3*t +
              np.sin(2*np.pi*4*t) +
              0.6*np.sin(2*np.pi*15*t) +
              0.4*np.sin(2*np.pi*35*t) +
              0.05*np.random.normal(size=len(t)))
    print("Running Fast Optuna-VMD with FFT caching...")
    start_time = time.time()
    modes, freqs, params = optuna_optimized_vmd(signal, fs, n_trials=20,
                                                boundary_method='reflect',
                                                apply_tapering=False)
    elapsed = time.time() - start_time
    print(f"Completed in {elapsed:.2f}s")
    total_energy = np.sum(signal**2)
    fig, axes = plt.subplots(len(modes)+2, 1, figsize=(14, 2.2*(len(modes)+2)))
    axes[0].plot(t, signal, 'b-', alpha=0.8)
    axes[0].set_title("Original Signal")
    for i, (m, f) in enumerate(zip(modes, freqs)):
        e_pct = 100*np.sum(m**2)/total_energy
        axes[i+1].plot(t, m, alpha=0.85)
        axes[i+1].set_title(f"Mode {i+1} | Dom freq ~{f:.2f} Hz | Energy {e_pct:.1f}%")
    recon = np.sum(modes, axis=0)
    axes[-1].plot(t, signal, 'b-', label="Original")
    axes[-1].plot(t, recon, 'r--', label="Reconstructed")
    mse = np.mean((signal - recon)**2)
    axes[-1].legend()
    axes[-1].set_title(f"Reconstruction MSE: {mse:.3e} | Best K={params[0]}, α={params[1]:.1f}")
    plt.tight_layout()
    plt.show()

# %%
# -*- coding: utf-8 -*-
"""
Fast Optuna-Optimized VMD with FFT caching for Optuna trials - Performance Enhanced
"""

import numpy as np
import optuna
import pyfftw
import pyfftw.interfaces.numpy_fft as fftw_np
from numba import njit, prange
import os
import pickle
import gc

# ==============================================
# 🚀 PERFORMANCE OPTIMIZATIONS
# ==============================================

# Configure FFTW for maximum performance
pyfftw.interfaces.cache.enable()
pyfftw.interfaces.cache.set_keepalive_time(7200)  # Extended cache time
pyfftw.config.NUM_THREADS = -1  # Use all cores

# FFTW Wisdom for massive speedup on repeated use
wisdom_file = "vmd_fftw_wisdom.dat"

def load_fftw_wisdom():
    """Load FFTW wisdom for faster FFTs"""
    if os.path.exists(wisdom_file):
        try:
            with open(wisdom_file, 'rb') as f:
                pyfftw.import_wisdom(pickle.load(f))
            print("🧠 FFTW wisdom loaded - FFTs will be faster!")
        except:
            print("⚠️ Could not load FFTW wisdom file")

def save_fftw_wisdom():
    """Save FFTW wisdom for future runs"""
    try:
        with open(wisdom_file, 'wb') as f:
            pickle.dump(pyfftw.export_wisdom(), f)
        print("💾 FFTW wisdom saved for future speedup")
    except:
        print("⚠️ Could not save FFTW wisdom")

# Load wisdom at import
load_fftw_wisdom()

# Memory pool to avoid repeated large allocations
_memory_pool = {}

def get_temp_array(shape, dtype=np.complex128, clear=True):
    """Get temporary array from memory pool"""
    key = (shape, dtype.__name__ if hasattr(dtype, '__name__') else str(dtype))
    if key not in _memory_pool:
        _memory_pool[key] = np.zeros(shape, dtype=dtype)
    
    arr = _memory_pool[key]
    if clear:
        arr.fill(0)  # Clear previous data
    return arr

def clear_memory_pool():
    """Clear memory pool to free RAM"""
    global _memory_pool
    _memory_pool.clear()
    gc.collect()

# Signal complexity assessment for smart parameter tuning
def assess_signal_complexity(signal, fs):
    """Determine optimal parameters based on signal characteristics"""
    # Basic signal stats
    signal_len = len(signal)
    
    # Spectral analysis
    spec = np.abs(fftw_np.rfft(signal))
    freqs = fftw_np.rfftfreq(signal_len, 1/fs)
    
    # Spectral entropy (measure of complexity)
    spec_norm = spec / (np.sum(spec) + 1e-12)
    spectral_entropy = -np.sum(spec_norm * np.log(spec_norm + 1e-12))
    
    # Dominant frequency analysis
    spec[0] = 0  # Remove DC
    peak_idx = np.argmax(spec)
    dominant_freq = freqs[peak_idx]
    
    # Energy distribution
    energy_threshold = 0.05 * np.max(spec)
    significant_freqs = freqs[spec > energy_threshold]
    freq_spread = len(significant_freqs) / len(freqs)
    
    # Derivative-based complexity
    signal_diff = np.diff(signal)
    variability = np.std(signal_diff) / (np.std(signal) + 1e-12)
    
    # Determine complexity level
    complexity_score = (
        0.4 * (spectral_entropy / 10.0) +  # Normalized spectral entropy
        0.3 * freq_spread +                # Frequency spread
        0.3 * min(variability, 2.0) / 2.0  # Normalized variability
    )
    
    # Smart parameter recommendations
    if complexity_score < 0.3:  # Simple signal
        params = {
            'n_trials': max(10, min(15, signal_len // 200)),
            'max_K': 4,
            'tol': 1e-5,
            'alpha_min': 1000,
            'alpha_max': 3000,
            'early_stop_patience': 3
        }
    elif complexity_score < 0.6:  # Moderate complexity
        params = {
            'n_trials': max(15, min(25, signal_len // 150)),
            'max_K': 6,
            'tol': 1e-6,
            'alpha_min': 500,
            'alpha_max': 5000,
            'early_stop_patience': 5
        }
    else:  # Complex signal
        params = {
            'n_trials': max(20, min(35, signal_len // 100)),
            'max_K': 8,
            'tol': 1e-7,
            'alpha_min': 200,
            'alpha_max': 8000,
            'early_stop_patience': 7
        }
    
    # Adjust for signal length
    if signal_len > 3000:
        params['n_trials'] = max(10, params['n_trials'] // 2)
        params['tol'] *= 2  # Relax tolerance for long signals
    
    print(f"🧮 Signal complexity: {complexity_score:.3f} | "
          f"Dominant freq: {dominant_freq:.1f} Hz | "
          f"Recommended trials: {params['n_trials']}, max_K: {params['max_K']}")
    
    return params

# ==============================================
# Boundary Handling Functions (UNCHANGED)
# ==============================================
def apply_window(signal, window_type='tukey', alpha_win=0.1):
    N = len(signal)
    if window_type == 'tukey':
        from scipy.signal import windows
        window = windows.tukey(N, alpha_win)
    elif window_type == 'hann':
        window = np.hanning(N)
    elif window_type == 'hamming':
        window = np.hamming(N)
    else:
        window = np.ones(N)
    return signal * window, window

def extend_signal(signal, method='mirror', extension_ratio=0.25):
    N = len(signal)
    ext_len = int(N * extension_ratio)
    if method == 'mirror':
        left_ext = signal[1:ext_len+1][::-1]
        right_ext = signal[-(ext_len+1):-1][::-1]
        extended = np.concatenate([left_ext, signal, right_ext])
    elif method == 'reflect':
        left_val = signal[0]
        right_val = signal[-1]
        left_ext = 2*left_val - signal[1:ext_len+1][::-1]
        right_ext = 2*right_val - signal[-(ext_len+1):-1][::-1]
        extended = np.concatenate([left_ext, signal, right_ext])
    elif method == 'linear':
        left_slope = (signal[1] - signal[0])
        right_slope = (signal[-1] - signal[-2])
        left_ext = signal[0] + left_slope * np.arange(-ext_len, 0)
        right_ext = signal[-1] + right_slope * np.arange(1, ext_len+1)
        extended = np.concatenate([left_ext, signal, right_ext])
    elif method == 'constant':
        left_ext = np.full(ext_len, signal[0])
        right_ext = np.full(ext_len, signal[-1])
        extended = np.concatenate([left_ext, signal, right_ext])
    else:
        return signal, 0, 0
    return extended, ext_len, ext_len

def taper_boundaries(modes, taper_length=50):
    tapered_modes = []
    for mode in modes:
        tapered = mode.copy()
        N = len(mode)
        taper_len = min(taper_length, N//4)
        taper = np.ones(N)
        taper[:taper_len] = np.sin(np.linspace(0, np.pi/2, taper_len))**2
        taper[-taper_len:] = np.cos(np.linspace(0, np.pi/2, taper_len))**2
        tapered_modes.append(tapered * taper)
    return tapered_modes

# ==============================================
# Enhanced Numba Inner Loop with Optimizations
# ==============================================
@njit(parallel=True, fastmath=True)
def update_modes_numba(freqs, half_T, f_hat_plus, sum_uk,
                       lambda_hat_n, Alpha, omega_n, u_hat_prev, K, tau):
    T = len(freqs)
    freq_slice_start = half_T
    u_hat_plus_next = np.zeros((T, K), dtype=np.complex128)
    omega_next = np.zeros(K)
    mode_sum = np.zeros(T, dtype=np.complex128)
    diff_norm = 0.0
    eps = 1e-14  # ✅ stability

    # 🚀 OPTIMIZATION: Pre-compute squared frequencies for stability
    # freq_sq = freqs * freqs  # Removed unused variable
    
    for k in range(K):
        if k == 0:
            sum_uk += u_hat_prev[:, K - 1] - u_hat_prev[:, 0]
        else:
            sum_uk += u_hat_plus_next[:, k - 1] - u_hat_prev[:, k]

        # 🚀 OPTIMIZATION: Vectorized computation with pre-computed squares
        omega_k = omega_n[k]
        alpha_k = Alpha[k]
        
        for i in range(T):
            freq_diff = freqs[i] - omega_k
            denom = 1.0 + alpha_k * freq_diff * freq_diff + eps  # ✅ stable
            u_hat_plus_next[i, k] = (f_hat_plus[i] - sum_uk[i] - lambda_hat_n[i] * 0.5) / denom

        # 🚀 OPTIMIZATION: More efficient frequency update
        numerator = 0.0
        denominator = 0.0
        for i in range(freq_slice_start, T):
            weight = u_hat_plus_next[i, k].real**2 + u_hat_plus_next[i, k].imag**2
            numerator += freqs[i] * weight
            denominator += weight
        
        if denominator > eps:
            omega_next[k] = numerator / denominator
        else:
            omega_next[k] = omega_k

        mode_sum += u_hat_plus_next[:, k]
        diff = u_hat_plus_next[:, k] - u_hat_prev[:, k]
        diff_norm += np.real(np.vdot(diff, diff)) / T

    lambda_next = lambda_hat_n + tau * (mode_sum - f_hat_plus)
    return u_hat_plus_next, omega_next, sum_uk, lambda_next, diff_norm

# ==============================================
# Precompute FFT+Boundary for all trials (ENHANCED)
# ==============================================

def smooth_edge_junction(extended_signal, original_len, ext_len, smooth_ratio=0.02):
    """
    Smooth the junction between mirrored edges and original signal with a tiny cosine ramp.
    smooth_ratio=0.02 means 2% of signal length at each junction.
    """
    N = len(extended_signal)
    taper_len = max(2, int(original_len * smooth_ratio))

    # Cosine ramps
    ramp_up = 0.5 * (1 - np.cos(np.linspace(0, np.pi, taper_len)))
    ramp_down = ramp_up[::-1]

    # Left junction
    extended_signal[ext_len - taper_len:ext_len] *= ramp_up
    # Right junction
    end_idx = ext_len + original_len
    extended_signal[end_idx:end_idx + taper_len] *= ramp_down
    return extended_signal

def adaptive_extension_ratio(signal):
    N = len(signal)
    # 🚀 OPTIMIZATION: More aggressive ratio reduction for speed
    if N < 500:
        return 0.3  # Reduced from 0.4
    elif N < 2000:
        return 0.2  # Reduced from 0.3
    else:
        return 0.15  # Reduced from 0.2

def auto_window_alpha(signal, min_alpha=0.01, max_alpha=0.1):
    """
    Adaptive Tukey window alpha based on derivative variance.
    
    - Highly oscillatory signals -> smaller alpha (less windowing)
    - Smooth signals -> larger alpha (more windowing)
    """
    deriv = np.diff(signal)
    deriv_var = np.var(deriv)

    # Normalize variance to a reasonable range
    norm_var = deriv_var / (np.mean(np.abs(signal))**2 + 1e-12)

    # Map normalized variance to [min_alpha, max_alpha]
    # More oscillation (large norm_var) => closer to min_alpha
    # Smoother signals (small norm_var) => closer to max_alpha
    smoothness_factor = 1.0 / (1.0 + norm_var)  # ~0 for noisy, ~1 for smooth
    alpha = min_alpha + (max_alpha - min_alpha) * smoothness_factor

    return alpha

def precompute_vmd_fft(signal, boundary_method='reflect', use_soft_junction=True, window_alpha=None):
    orig_len = len(signal)
    if len(signal) % 2:
        signal = signal[:-1]

    # normal extension
    if boundary_method != 'none':
        ratio = adaptive_extension_ratio(signal)
        fMirr, left_ext, right_ext = extend_signal(signal, method=boundary_method, extension_ratio=ratio)
    else:
        fMirr = signal
        left_ext = right_ext = 0

    # ✅ NEW: soft junction smoothing
    if use_soft_junction and boundary_method != 'none':
        fMirr = smooth_edge_junction(fMirr, orig_len, left_ext, smooth_ratio=0.02)

    if window_alpha is None:
        window_alpha = auto_window_alpha(signal)

    # ✅ NEW: apply very light Tukey window before FFT
    if window_alpha > 0:
        from scipy.signal import windows
        win = windows.tukey(len(fMirr), alpha=window_alpha)
        fMirr = fMirr * win

    # ✅ NEW: safer frequency grid
    T = len(fMirr)
    freqs = np.fft.fftshift(np.fft.fftfreq(T))  # more numerically consistent
    f_hat = fftw_np.fftshift(fftw_np.fft(fMirr))
    f_hat_plus = f_hat.copy()
    f_hat_plus[:T // 2] = 0

    return {
        "f_hat_plus": f_hat_plus,
        "freqs": freqs,
        "T": T,
        "half_T": T // 2,
        "orig_len": orig_len,
        "left_ext": left_ext,
        "right_ext": right_ext
    }

def init_from_spectrum(signal, K):
    """
    Initialize omega_curr from the K largest FFT peaks.
    """
    spec = np.abs(fftw_np.rfft(signal))
    freqs = fftw_np.rfftfreq(len(signal))
    peak_idx = np.argsort(spec)[-K:]  # largest K peaks
    return np.sort(freqs[peak_idx])

# ==============================================
# VMD Core with Performance Optimizations
# ==============================================
def VMD(f, alpha, tau, K, DC, init, tol,
        boundary_method='reflect', max_iter=300,
        precomputed_fft=None,
        trial=None):  # <-- now accepts trial
    # If we have a precomputed cache, use it
    if precomputed_fft is not None:
        f_hat_plus = precomputed_fft["f_hat_plus"]
        freqs = precomputed_fft["freqs"]
        T = precomputed_fft["T"]
        half_T = precomputed_fft["half_T"]
        orig_len = precomputed_fft["orig_len"]
        left_ext = precomputed_fft["left_ext"]
        right_ext = precomputed_fft["right_ext"]
    else:
        # Normal path: compute FFT and boundaries
        orig_len = len(f)
        if len(f) % 2:
            f = f[:-1]
        if boundary_method != 'none':
            fMirr, left_ext, right_ext = extend_signal(f, method=boundary_method, extension_ratio=0.3)
        else:
            fMirr = f
            left_ext = right_ext = 0
        T = len(fMirr)
        freqs = np.linspace(0, 1, T) - 0.5 - 1.0/T
        f_hat = fftw_np.fftshift(fftw_np.fft(fMirr))
        f_hat_plus = f_hat.copy()
        f_hat_plus[:T // 2] = 0
        half_T = T // 2

    Alpha = alpha * np.ones(K)
    omega_curr = np.zeros(K)
    if init == 1:
        omega_curr = np.arange(K) * (0.5 / K)
    elif init == 2:
        fs = 1 / T
        omega_curr = np.sort(np.exp(np.log(fs) + (np.log(0.5) - np.log(fs)) * np.random.rand(K)))
    elif init == 3:  # new mode: spectral init
        omega_curr = init_from_spectrum(fMirr if 'fMirr' in locals() else f, K)
    if DC:
        omega_curr[0] = 0.0
    lambda_curr = np.zeros(len(freqs), dtype=np.complex128)
    sum_uk = np.zeros(len(freqs), dtype=np.complex128)
    u_hat_prev = np.zeros((len(freqs), K), dtype=np.complex128)
    uDiff = tol + 1.0
    
    # 🚀 OPTIMIZATION: Early stopping variables
    stagnation_count = 0
    prev_diff = float('inf')
    adaptive_tol = max(tol, 1e-7)  # Slightly relaxed for speed
    
    for n in range(max_iter):
        u_hat_next, omega_next, sum_uk, lambda_next, diff_norm = update_modes_numba(
            freqs, half_T, f_hat_plus, sum_uk, lambda_curr, Alpha, omega_curr, u_hat_prev, K, tau
        )
        if n > 5:
            uDiff = diff_norm

        # 🚀 OPTIMIZATION: Smart early stopping
        if n > 10:
            if abs(diff_norm - prev_diff) < adaptive_tol * 0.1:
                stagnation_count += 1
            else:
                stagnation_count = 0
            
            # Early termination if stagnating
            if stagnation_count >= 5:
                break

        # ✅ Report intermediate value to Optuna for pruning (less frequent for speed)
        if trial is not None and n % 15 == 0:  # Reduced from 10 to 15
            trial.report(uDiff, step=n)
            if trial.should_prune():
                raise optuna.TrialPruned()
        
        u_hat_prev = u_hat_next
        lambda_curr = lambda_next
        omega_curr = omega_next
        prev_diff = diff_norm
        
        if uDiff <= tol:
            break

    # symmetric reconstruction
    u_hat_full = np.zeros((T, K), dtype=np.complex128)
    u_hat_full[half_T:T, :] = u_hat_prev[half_T:T, :]
    idxs = np.arange(1, half_T)
    u_hat_full[idxs, :] = np.conj(u_hat_full[T - idxs, :])
    u_hat_full[0, :] = np.conj(u_hat_full[-1, :])
    # Inverse FFT to time domain
    u = np.real(fftw_np.ifft(fftw_np.ifftshift(u_hat_full, axes=0), axis=0)).T

    if precomputed_fft is not None or boundary_method != 'none':
        start_idx = left_ext
        end_idx = start_idx + orig_len
        u = u[:, start_idx:end_idx]

    if u.shape[1] != orig_len:
        # old time grid (normalized 0..1)
        x_old = np.linspace(0, 1, u.shape[1])
        # new time grid (target length)
        x_new = np.linspace(0, 1, orig_len)
        
        # vectorized interpolation: apply np.interp for each mode row
        u = np.vstack([np.interp(x_new, x_old, mode) for mode in u])

    return u, u_hat_full, omega_curr

# ==============================================
# Helpers (UNCHANGED but with minor optimizations)
# ==============================================
def get_dominant_frequency(sig, fs):
    N = len(sig)
    if N < 4 or np.allclose(sig, 0, atol=1e-12):
        return 0.0
    freqs = fftw_np.rfftfreq(N, d=1/fs)
    spec = np.abs(fftw_np.rfft(sig))
    if len(spec) == 0:
        return 0.0
    spec[0] = 0
    return freqs[np.argmax(spec)]

def merge_similar_modes(modes, fs, freq_tol=0.1):
    if len(modes) <= 1:
        return modes
    dom_freqs = [get_dominant_frequency(m, fs) for m in modes]
    merged = []
    used = np.zeros(len(modes), dtype=bool)
    for i in range(len(modes)):
        if used[i]:
            continue
        group = [modes[i]]
        fi = dom_freqs[i]
        used[i] = True
        for j in range(i+1, len(modes)):
            if used[j]:
                continue
            fj = dom_freqs[j]
            if abs(fi-fj)/max(fi,1e-6) < freq_tol:
                group.append(modes[j])
                used[j] = True
        merged.append(np.sum(group, axis=0))
    return merged

def sort_modes_by_frequency(modes, fs, low_to_high=True):
    dom_freqs = [get_dominant_frequency(m, fs) for m in modes]
    order = np.argsort(dom_freqs)
    if not low_to_high:
        order = order[::-1]
    return [modes[i] for i in order], [dom_freqs[i] for i in order]

def ovmd_cost(modes, signal, fs):
    if len(modes) == 0:
        return 10.0
    total_energy = np.sum(signal**2)
    recon = np.sum(modes, axis=0)
    residual_energy = np.sum((signal - recon)**2) / total_energy
    dom_freqs = [get_dominant_frequency(m, fs) for m in modes]
    overlap_penalty = np.mean(np.exp(-np.diff(np.sort(dom_freqs)))) if len(dom_freqs) > 1 else 0.0
    
    # 🚀 OPTIMIZATION: Simplified entropy calculation
    entropy_vals = []
    for m in modes:
        spec = np.abs(fftw_np.rfft(m)) + 1e-12
        p = spec / np.sum(spec)
        # Faster entropy approximation
        entropy_vals.append(-np.mean(p * np.log(p + 1e-12)))
    avg_entropy = np.mean(entropy_vals) / np.log(len(modes) + 1)  # Normalized
    
    return 0.7*residual_energy + 0.2*overlap_penalty + 0.1*avg_entropy

# ==============================================
# Enhanced Optuna with Smart Caching and Complexity Assessment
# ==============================================
_cache = {}
def optuna_objective(trial, signal, fs, precomputed_fft, complexity_params,
                     tau=0.0, DC=0, init=1, tol=1e-6):
    K = trial.suggest_int("K", 2, complexity_params['max_K'])
    alpha = trial.suggest_float("alpha", 
                               complexity_params['alpha_min'], 
                               complexity_params['alpha_max'], log=True)
    
    # 🚀 OPTIMIZATION: Smarter caching with rounded alpha
    cache_key = (K, round(alpha, -1))  # Round to nearest 10
    if cache_key in _cache:
        modes = _cache[cache_key]
    else:
        try:
            modes, _, _ = VMD(None, alpha=alpha, tau=tau, K=K,
                              DC=DC, init=init, tol=tol,
                              precomputed_fft=precomputed_fft,
                              trial=trial)  # <-- pass trial here
            total_energy = np.sum(signal**2)
            modes = [m for m in modes if np.sum(m**2)/total_energy > 0.01]
            
            # 🚀 OPTIMIZATION: Better cache management
            if len(_cache) < 40:  # Slightly larger cache
                _cache[cache_key] = modes
        except optuna.TrialPruned:
            raise  # propagate pruning
        except:
            return 10.0
    if len(modes) == 0:
        return 10.0
    return ovmd_cost(modes, signal, fs)

def optuna_optimized_vmd(signal, fs,
                         n_trials=None,  # Now auto-determined
                         tau=0.0, DC=0, init=1, tol=None,  # Now auto-determined
                         boundary_method='reflect',
                         apply_tapering=True,
                         auto_params=True):  # New parameter
    global _cache
    _cache.clear()
    
    # 🚀 NEW: Assess signal complexity and get smart parameters
    if auto_params:
        complexity_params = assess_signal_complexity(signal, fs)
        if n_trials is None:
            n_trials = complexity_params['n_trials']
        if tol is None:
            tol = complexity_params['tol']
        print(f"🎯 Auto-tuned: n_trials={n_trials}, tol={tol:.0e}, max_K={complexity_params['max_K']}")
    else:
        # Fallback to original behavior
        complexity_params = {
            'max_K': 6, 'alpha_min': 500, 'alpha_max': 5000, 
            'early_stop_patience': 5
        }
        if n_trials is None:
            n_trials = 30
        if tol is None:
            tol = 1e-6
    
    # 🚀 Smart trial reduction for long signals (additional optimization)
    if len(signal) > 2000 and auto_params:
        n_trials = max(10, n_trials // 2)
        print(f"📉 Reduced trials to {n_trials} for long signal")
    
    # Precompute FFT once for all trials
    print("🔄 Computing FFT and boundaries...")
    precomputed_fft = precompute_vmd_fft(signal, boundary_method)
    
    def objective_wrapper(trial):
        return optuna_objective(trial, signal, fs, precomputed_fft, complexity_params, tau, DC, init, tol)
    
    # ✅ Enable pruning with complexity-aware settings
    pruner = optuna.pruners.MedianPruner(
        n_warmup_steps=max(2, complexity_params.get('early_stop_patience', 5) - 2),
        n_startup_trials=min(5, n_trials // 3)
    )
    
    # 🚀 Smart sampler selection
    if len(signal) > 1500:
        sampler = optuna.samplers.TPESampler(n_startup_trials=3)
    else:
        sampler = optuna.samplers.TPESampler(n_startup_trials=5)
    
    study = optuna.create_study(direction="minimize", pruner=pruner, sampler=sampler)
    
    print(f"🔍 Running {n_trials} optimization trials...")
    study.optimize(objective_wrapper, n_trials=n_trials, show_progress_bar=True, n_jobs=-1)
    
    best_K = int(study.best_params["K"])
    best_alpha = study.best_params["alpha"]
    best_cost = study.best_value
    print(f"[Fast-VMD] ✅ Optimal K={best_K}, alpha={best_alpha:.1f}, cost={best_cost:.4f}")
    
    print("🏁 Computing final decomposition...")
    best_modes, _, _ = VMD(None, alpha=best_alpha, tau=tau, K=best_K,
                           DC=DC, init=init, tol=tol,
                           precomputed_fft=precomputed_fft)
    total_energy = np.sum(signal**2)
    best_modes = [m for m in best_modes if np.sum(m**2)/total_energy > 0.01]
    merged_modes = merge_similar_modes(best_modes, fs, freq_tol=0.15)
    sorted_modes, sorted_freqs = sort_modes_by_frequency(merged_modes, fs, low_to_high=True)
    if apply_tapering:
        taper_len = min(100, len(signal)//10)
        sorted_modes = taper_boundaries(sorted_modes, taper_len)
    
    # 🚀 Save FFTW wisdom after first successful run
    save_fftw_wisdom()
    
    return np.array(sorted_modes), sorted_freqs, (best_K, best_alpha, best_cost)

# ==============================================
# Test Script (UNCHANGED)
# ==============================================
if __name__ == "__main__":
    import matplotlib.pyplot as plt, time
    t = np.linspace(0, 8, 1500)
    fs = len(t)/(t[-1]-t[0])
    signal = (0.3*t +
              np.sin(2*np.pi*4*t) +
              0.6*np.sin(2*np.pi*15*t) +
              0.4*np.sin(2*np.pi*35*t) +
              0.05*np.random.normal(size=len(t)))
    print("🚀 Running Smart Auto-Tuned VMD...")
    start_time = time.time()
    
    # 🚀 NEW: Use auto-tuning by default
    modes, freqs, params = optuna_optimized_vmd(signal, fs, 
                                                boundary_method='reflect',
                                                apply_tapering=False,
                                                auto_params=True)  # Enable smart tuning
    elapsed = time.time() - start_time
    print(f"✅ Completed in {elapsed:.2f}s")
    
    # 🚀 Memory cleanup
    clear_memory_pool()
    total_energy = np.sum(signal**2)
    fig, axes = plt.subplots(len(modes)+2, 1, figsize=(14, 2.2*(len(modes)+2)))
    axes[0].plot(t, signal, 'b-', alpha=0.8)
    axes[0].set_title("Original Signal")
    for i, (m, f) in enumerate(zip(modes, freqs)):
        e_pct = 100*np.sum(m**2)/total_energy
        axes[i+1].plot(t, m, alpha=0.85)
        axes[i+1].set_title(f"Mode {i+1} | Dom freq ~{f:.2f} Hz | Energy {e_pct:.1f}%")
    recon = np.sum(modes, axis=0)
    axes[-1].plot(t, signal, 'b-', label="Original")
    axes[-1].plot(t, recon, 'r--', label="Reconstructed")
    mse = np.mean((signal - recon)**2)
    axes[-1].legend()
    axes[-1].set_title(f"Reconstruction MSE: {mse:.3e} | Best K={params[0]}, α={params[1]:.1f}")
    plt.tight_layout()
    plt.show()

# %% [markdown]
# # OK

# %%
# -*- coding: utf-8 -*-
"""
Fast Optuna-Optimized VMD with FFT caching for Optuna trials - Performance Enhanced
"""

import numpy as np
import optuna
import pyfftw
import pyfftw.interfaces.numpy_fft as fftw_np
from numba import njit, prange
import os
import pickle
import gc

# ==============================================
# 🚀 PERFORMANCE OPTIMIZATIONS
# ==============================================

# Configure FFTW for maximum performance
pyfftw.interfaces.cache.enable()
pyfftw.interfaces.cache.set_keepalive_time(7200)  # Extended cache time
pyfftw.config.NUM_THREADS = -1  # Use all cores

# FFTW Wisdom for massive speedup on repeated use
wisdom_file = "vmd_fftw_wisdom.dat"

def load_fftw_wisdom():
    """Load FFTW wisdom for faster FFTs"""
    if os.path.exists(wisdom_file):
        try:
            with open(wisdom_file, 'rb') as f:
                pyfftw.import_wisdom(pickle.load(f))
            print("🧠 FFTW wisdom loaded - FFTs will be faster!")
        except:
            print("⚠️ Could not load FFTW wisdom file")

def save_fftw_wisdom():
    """Save FFTW wisdom for future runs"""
    try:
        with open(wisdom_file, 'wb') as f:
            pickle.dump(pyfftw.export_wisdom(), f)
        print("💾 FFTW wisdom saved for future speedup")
    except:
        print("⚠️ Could not save FFTW wisdom")

# Load wisdom at import
load_fftw_wisdom()

# Memory pool to avoid repeated large allocations
_memory_pool = {}

def get_temp_array(shape, dtype=np.complex128, clear=True):
    """Get temporary array from memory pool"""
    key = (shape, dtype.__name__ if hasattr(dtype, '__name__') else str(dtype))
    if key not in _memory_pool:
        _memory_pool[key] = np.zeros(shape, dtype=dtype)
    
    arr = _memory_pool[key]
    if clear:
        arr.fill(0)  # Clear previous data
    return arr

def clear_memory_pool():
    """Clear memory pool to free RAM"""
    global _memory_pool
    _memory_pool.clear()
    gc.collect()

# Signal complexity assessment for smart parameter tuning
def assess_signal_complexity(signal, fs):
    """Determine optimal parameters based on signal characteristics"""
    # Basic signal stats
    signal_len = len(signal)
    
    # Spectral analysis
    spec = np.abs(fftw_np.rfft(signal))
    freqs = fftw_np.rfftfreq(signal_len, 1/fs)
    
    # Spectral entropy (measure of complexity)
    spec_norm = spec / (np.sum(spec) + 1e-12)
    spectral_entropy = -np.sum(spec_norm * np.log(spec_norm + 1e-12))
    
    # Dominant frequency analysis
    spec[0] = 0  # Remove DC
    peak_idx = np.argmax(spec)
    dominant_freq = freqs[peak_idx]
    
    # Energy distribution
    energy_threshold = 0.05 * np.max(spec)
    significant_freqs = freqs[spec > energy_threshold]
    freq_spread = len(significant_freqs) / len(freqs)
    
    # Derivative-based complexity
    signal_diff = np.diff(signal)
    variability = np.std(signal_diff) / (np.std(signal) + 1e-12)
    
    # Determine complexity level
    complexity_score = (
        0.4 * (spectral_entropy / 10.0) +  # Normalized spectral entropy
        0.3 * freq_spread +                # Frequency spread
        0.3 * min(variability, 2.0) / 2.0  # Normalized variability
    )
    
    # Smart parameter recommendations
    if complexity_score < 0.3:  # Simple signal
        params = {
            'n_trials': max(10, min(15, signal_len // 200)),
            'max_K': 4,
            'tol': 1e-5,
            'alpha_min': 1000,
            'alpha_max': 3000,
            'early_stop_patience': 3
        }
    elif complexity_score < 0.6:  # Moderate complexity
        params = {
            'n_trials': max(15, min(25, signal_len // 150)),
            'max_K': 6,
            'tol': 1e-6,
            'alpha_min': 500,
            'alpha_max': 5000,
            'early_stop_patience': 5
        }
    else:  # Complex signal
        params = {
            'n_trials': max(20, min(35, signal_len // 100)),
            'max_K': 8,
            'tol': 1e-7,
            'alpha_min': 200,
            'alpha_max': 8000,
            'early_stop_patience': 7
        }
    
    # Adjust for signal length
    if signal_len > 3000:
        params['n_trials'] = max(10, params['n_trials'] // 2)
        params['tol'] *= 2  # Relax tolerance for long signals
    
    print(f"🧮 Signal complexity: {complexity_score:.3f} | "
          f"Dominant freq: {dominant_freq:.1f} Hz | "
          f"Recommended trials: {params['n_trials']}, max_K: {params['max_K']}")
    
    return params

# ==============================================
# Boundary Handling Functions (UNCHANGED)
# ==============================================
def apply_window(signal, window_type='tukey', alpha_win=0.1):
    N = len(signal)
    if window_type == 'tukey':
        from scipy.signal import windows
        window = windows.tukey(N, alpha_win)
    elif window_type == 'hann':
        window = np.hanning(N)
    elif window_type == 'hamming':
        window = np.hamming(N)
    else:
        window = np.ones(N)
    return signal * window, window

def extend_signal(signal, method='mirror', extension_ratio=0.25):
    N = len(signal)
    ext_len = int(N * extension_ratio)
    if method == 'mirror':
        left_ext = signal[1:ext_len+1][::-1]
        right_ext = signal[-(ext_len+1):-1][::-1]
        extended = np.concatenate([left_ext, signal, right_ext])
    elif method == 'reflect':
        left_val = signal[0]
        right_val = signal[-1]
        left_ext = 2*left_val - signal[1:ext_len+1][::-1]
        right_ext = 2*right_val - signal[-(ext_len+1):-1][::-1]
        extended = np.concatenate([left_ext, signal, right_ext])
    elif method == 'linear':
        left_slope = (signal[1] - signal[0])
        right_slope = (signal[-1] - signal[-2])
        left_ext = signal[0] + left_slope * np.arange(-ext_len, 0)
        right_ext = signal[-1] + right_slope * np.arange(1, ext_len+1)
        extended = np.concatenate([left_ext, signal, right_ext])
    elif method == 'constant':
        left_ext = np.full(ext_len, signal[0])
        right_ext = np.full(ext_len, signal[-1])
        extended = np.concatenate([left_ext, signal, right_ext])
    else:
        return signal, 0, 0
    return extended, ext_len, ext_len

def taper_boundaries(modes, taper_length=50):
    tapered_modes = []
    for mode in modes:
        tapered = mode.copy()
        N = len(mode)
        taper_len = min(taper_length, N//4)
        taper = np.ones(N)
        taper[:taper_len] = np.sin(np.linspace(0, np.pi/2, taper_len))**2
        taper[-taper_len:] = np.cos(np.linspace(0, np.pi/2, taper_len))**2
        tapered_modes.append(tapered * taper)
    return tapered_modes

# ==============================================
# Enhanced Numba Inner Loop with Optimizations
# ==============================================
@njit(parallel=True, fastmath=True)
def update_modes_numba(freqs, half_T, f_hat_plus, sum_uk,
                       lambda_hat_n, Alpha, omega_n, u_hat_prev, K, tau):
    T = len(freqs)
    freq_slice_start = half_T
    u_hat_plus_next = np.zeros((T, K), dtype=np.complex128)
    omega_next = np.zeros(K)
    mode_sum = np.zeros(T, dtype=np.complex128)
    diff_norm = 0.0
    eps = 1e-14  # ✅ stability

    # 🚀 OPTIMIZATION: Pre-compute squared frequencies for stability
    # freq_sq = freqs * freqs  # Removed unused variable
    
    for k in range(K):
        if k == 0:
            sum_uk += u_hat_prev[:, K - 1] - u_hat_prev[:, 0]
        else:
            sum_uk += u_hat_plus_next[:, k - 1] - u_hat_prev[:, k]

        # 🚀 OPTIMIZATION: Vectorized computation with pre-computed squares
        omega_k = omega_n[k]
        alpha_k = Alpha[k]
        
        for i in range(T):
            freq_diff = freqs[i] - omega_k
            denom = 1.0 + alpha_k * freq_diff * freq_diff + eps  # ✅ stable
            u_hat_plus_next[i, k] = (f_hat_plus[i] - sum_uk[i] - lambda_hat_n[i] * 0.5) / denom

        # 🚀 OPTIMIZATION: More efficient frequency update
        numerator = 0.0
        denominator = 0.0
        for i in range(freq_slice_start, T):
            weight = u_hat_plus_next[i, k].real**2 + u_hat_plus_next[i, k].imag**2
            numerator += freqs[i] * weight
            denominator += weight
        
        if denominator > eps:
            omega_next[k] = numerator / denominator
        else:
            omega_next[k] = omega_k

        mode_sum += u_hat_plus_next[:, k]
        diff = u_hat_plus_next[:, k] - u_hat_prev[:, k]
        diff_norm += np.real(np.vdot(diff, diff)) / T

    lambda_next = lambda_hat_n + tau * (mode_sum - f_hat_plus)
    return u_hat_plus_next, omega_next, sum_uk, lambda_next, diff_norm

# ==============================================
# Precompute FFT+Boundary for all trials (ENHANCED)
# ==============================================

def smooth_edge_junction(extended_signal, original_len, ext_len, smooth_ratio=0.02):
    """
    Smooth the junction between mirrored edges and original signal with a tiny cosine ramp.
    smooth_ratio=0.02 means 2% of signal length at each junction.
    """
    N = len(extended_signal)
    taper_len = max(2, int(original_len * smooth_ratio))

    # Cosine ramps
    ramp_up = 0.5 * (1 - np.cos(np.linspace(0, np.pi, taper_len)))
    ramp_down = ramp_up[::-1]

    # Left junction
    extended_signal[ext_len - taper_len:ext_len] *= ramp_up
    # Right junction
    end_idx = ext_len + original_len
    extended_signal[end_idx:end_idx + taper_len] *= ramp_down
    return extended_signal

def adaptive_extension_ratio(signal):
    N = len(signal)
    # 🚀 OPTIMIZATION: More aggressive ratio reduction for speed
    if N < 500:
        return 0.3  # Reduced from 0.4
    elif N < 2000:
        return 0.2  # Reduced from 0.3
    else:
        return 0.15  # Reduced from 0.2

def auto_window_alpha(signal, min_alpha=0.01, max_alpha=0.1):
    """
    Adaptive Tukey window alpha based on derivative variance.
    
    - Highly oscillatory signals -> smaller alpha (less windowing)
    - Smooth signals -> larger alpha (more windowing)
    """
    deriv = np.diff(signal)
    deriv_var = np.var(deriv)

    # Normalize variance to a reasonable range
    norm_var = deriv_var / (np.mean(np.abs(signal))**2 + 1e-12)

    # Map normalized variance to [min_alpha, max_alpha]
    # More oscillation (large norm_var) => closer to min_alpha
    # Smoother signals (small norm_var) => closer to max_alpha
    smoothness_factor = 1.0 / (1.0 + norm_var)  # ~0 for noisy, ~1 for smooth
    alpha = min_alpha + (max_alpha - min_alpha) * smoothness_factor

    return alpha

def precompute_vmd_fft(signal, boundary_method='reflect', use_soft_junction=False, window_alpha=None):
    orig_len = len(signal)
    if len(signal) % 2:
        signal = signal[:-1]

    # normal extension
    if boundary_method != 'none':
        ratio = adaptive_extension_ratio(signal)
        fMirr, left_ext, right_ext = extend_signal(signal, method=boundary_method, extension_ratio=ratio)
    else:
        fMirr = signal
        left_ext = right_ext = 0

    # ✅ NEW: soft junction smoothing
    if use_soft_junction and boundary_method != 'none':
        fMirr = smooth_edge_junction(fMirr, orig_len, left_ext, smooth_ratio=0.02)

    if window_alpha is None:
        window_alpha = auto_window_alpha(signal)

    # ✅ NEW: apply very light Tukey window before FFT
    if window_alpha > 0:
        from scipy.signal import windows
        win = windows.tukey(len(fMirr), alpha=window_alpha)
        fMirr = fMirr * win

    # ✅ NEW: safer frequency grid
    T = len(fMirr)
    freqs = np.fft.fftshift(np.fft.fftfreq(T))  # more numerically consistent
    f_hat = fftw_np.fftshift(fftw_np.fft(fMirr))
    f_hat_plus = f_hat.copy()
    f_hat_plus[:T // 2] = 0

    return {
        "f_hat_plus": f_hat_plus,
        "freqs": freqs,
        "T": T,
        "half_T": T // 2,
        "orig_len": orig_len,
        "left_ext": left_ext,
        "right_ext": right_ext
    }

def init_from_spectrum(signal, K):
    """
    Initialize omega_curr from the K largest FFT peaks.
    """
    spec = np.abs(fftw_np.rfft(signal))
    freqs = fftw_np.rfftfreq(len(signal))
    peak_idx = np.argsort(spec)[-K:]  # largest K peaks
    return np.sort(freqs[peak_idx])

# ==============================================
# VMD Core with Performance Optimizations
# ==============================================
def VMD(f, alpha, tau, K, DC, init, tol,
        boundary_method='reflect', max_iter=300,
        precomputed_fft=None,
        trial=None):  # <-- now accepts trial
    # If we have a precomputed cache, use it
    if precomputed_fft is not None:
        f_hat_plus = precomputed_fft["f_hat_plus"]
        freqs = precomputed_fft["freqs"]
        T = precomputed_fft["T"]
        half_T = precomputed_fft["half_T"]
        orig_len = precomputed_fft["orig_len"]
        left_ext = precomputed_fft["left_ext"]
        right_ext = precomputed_fft["right_ext"]
    else:
        # Normal path: compute FFT and boundaries
        orig_len = len(f)
        if len(f) % 2:
            f = f[:-1]
        if boundary_method != 'none':
            fMirr, left_ext, right_ext = extend_signal(f, method=boundary_method, extension_ratio=0.3)
        else:
            fMirr = f
            left_ext = right_ext = 0
        T = len(fMirr)
        freqs = np.linspace(0, 1, T) - 0.5 - 1.0/T
        f_hat = fftw_np.fftshift(fftw_np.fft(fMirr))
        f_hat_plus = f_hat.copy()
        f_hat_plus[:T // 2] = 0
        half_T = T // 2

    Alpha = alpha * np.ones(K)
    omega_curr = np.zeros(K)
    if init == 1:
        omega_curr = np.arange(K) * (0.5 / K)
    elif init == 2:
        fs = 1 / T
        omega_curr = np.sort(np.exp(np.log(fs) + (np.log(0.5) - np.log(fs)) * np.random.rand(K)))
    elif init == 3:  # new mode: spectral init
        omega_curr = init_from_spectrum(fMirr if 'fMirr' in locals() else f, K)
    if DC:
        omega_curr[0] = 0.0
    lambda_curr = np.zeros(len(freqs), dtype=np.complex128)
    sum_uk = np.zeros(len(freqs), dtype=np.complex128)
    u_hat_prev = np.zeros((len(freqs), K), dtype=np.complex128)
    uDiff = tol + 1.0
    
    # 🚀 OPTIMIZATION: Early stopping variables
    stagnation_count = 0
    prev_diff = float('inf')
    adaptive_tol = max(tol, 1e-7)  # Slightly relaxed for speed
    
    for n in range(max_iter):
        u_hat_next, omega_next, sum_uk, lambda_next, diff_norm = update_modes_numba(
            freqs, half_T, f_hat_plus, sum_uk, lambda_curr, Alpha, omega_curr, u_hat_prev, K, tau
        )
        if n > 5:
            uDiff = diff_norm

        # 🚀 OPTIMIZATION: Smart early stopping
        if n > 10:
            if abs(diff_norm - prev_diff) < adaptive_tol * 0.1:
                stagnation_count += 1
            else:
                stagnation_count = 0
            
            # Early termination if stagnating
            if stagnation_count >= 5:
                break

        # ✅ Report intermediate value to Optuna for pruning (less frequent for speed)
        if trial is not None and n % 15 == 0:  # Reduced from 10 to 15
            trial.report(uDiff, step=n)
            if trial.should_prune():
                raise optuna.TrialPruned()
        
        u_hat_prev = u_hat_next
        lambda_curr = lambda_next
        omega_curr = omega_next
        prev_diff = diff_norm
        
        if uDiff <= tol:
            break

    # symmetric reconstruction
    u_hat_full = np.zeros((T, K), dtype=np.complex128)
    u_hat_full[half_T:T, :] = u_hat_prev[half_T:T, :]
    idxs = np.arange(1, half_T)
    u_hat_full[idxs, :] = np.conj(u_hat_full[T - idxs, :])
    u_hat_full[0, :] = np.conj(u_hat_full[-1, :])
    # Inverse FFT to time domain
    u = np.real(fftw_np.ifft(fftw_np.ifftshift(u_hat_full, axes=0), axis=0)).T

    if precomputed_fft is not None or boundary_method != 'none':
        start_idx = left_ext
        end_idx = start_idx + orig_len
        u = u[:, start_idx:end_idx]

    if u.shape[1] != orig_len:
        # old time grid (normalized 0..1)
        x_old = np.linspace(0, 1, u.shape[1])
        # new time grid (target length)
        x_new = np.linspace(0, 1, orig_len)
        
        # vectorized interpolation: apply np.interp for each mode row
        u = np.vstack([np.interp(x_new, x_old, mode) for mode in u])

    return u, u_hat_full, omega_curr

# ==============================================
# Helpers (UNCHANGED but with minor optimizations)
# ==============================================
def get_dominant_frequency(sig, fs):
    N = len(sig)
    if N < 4 or np.allclose(sig, 0, atol=1e-12):
        return 0.0
    freqs = fftw_np.rfftfreq(N, d=1/fs)
    spec = np.abs(fftw_np.rfft(sig))
    if len(spec) == 0:
        return 0.0
    spec[0] = 0
    return freqs[np.argmax(spec)]

def merge_similar_modes(modes, fs, freq_tol=0.1):
    if len(modes) <= 1:
        return modes
    dom_freqs = [get_dominant_frequency(m, fs) for m in modes]
    merged = []
    used = np.zeros(len(modes), dtype=bool)
    for i in range(len(modes)):
        if used[i]:
            continue
        group = [modes[i]]
        fi = dom_freqs[i]
        used[i] = True
        for j in range(i+1, len(modes)):
            if used[j]:
                continue
            fj = dom_freqs[j]
            if abs(fi-fj)/max(fi,1e-6) < freq_tol:
                group.append(modes[j])
                used[j] = True
        merged.append(np.sum(group, axis=0))
    return merged

def sort_modes_by_frequency(modes, fs, low_to_high=True):
    dom_freqs = [get_dominant_frequency(m, fs) for m in modes]
    order = np.argsort(dom_freqs)
    if not low_to_high:
        order = order[::-1]
    return [modes[i] for i in order], [dom_freqs[i] for i in order]

def ovmd_cost(modes, signal, fs):
    if len(modes) == 0:
        return 10.0
    total_energy = np.sum(signal**2)
    recon = np.sum(modes, axis=0)
    residual_energy = np.sum((signal - recon)**2) / total_energy
    dom_freqs = [get_dominant_frequency(m, fs) for m in modes]
    overlap_penalty = np.mean(np.exp(-np.diff(np.sort(dom_freqs)))) if len(dom_freqs) > 1 else 0.0
    
    # 🚀 OPTIMIZATION: Simplified entropy calculation
    entropy_vals = []
    for m in modes:
        spec = np.abs(fftw_np.rfft(m)) + 1e-12
        p = spec / np.sum(spec)
        # Faster entropy approximation
        entropy_vals.append(-np.mean(p * np.log(p + 1e-12)))
    avg_entropy = np.mean(entropy_vals) / np.log(len(modes) + 1)  # Normalized
    
    return 0.7*residual_energy + 0.2*overlap_penalty + 0.1*avg_entropy

# ==============================================
# 🚀 HIERARCHICAL MULTI-RESOLUTION VMD
# ==============================================

def hierarchical_vmd(signal, fs, max_levels=3, energy_threshold=0.01, 
                     min_samples_per_level=100, use_anti_aliasing=True):
    """
    Hierarchical Multi-Resolution VMD for complex signals
    
    Decomposes signal at multiple time scales, extracting modes at each resolution
    and combining them intelligently. Excellent for signals with both fast and slow dynamics.
    
    Parameters:
    -----------
    signal : array_like
        Input signal
    fs : float 
        Sampling frequency
    max_levels : int
        Maximum decomposition levels (default: 3)
    energy_threshold : float
        Stop if residual energy drops below this fraction (default: 0.01 = 1%)
    min_samples_per_level : int
        Minimum samples required for decomposition at each level
    use_anti_aliasing : bool
        Apply anti-aliasing filter before downsampling
        
    Returns:
    --------
    final_modes : list
        Combined modes from all resolution levels
    level_info : list  
        Information about each decomposition level
    """
    print(f"🔍 Starting Hierarchical VMD (max_levels={max_levels})...")
    
    all_modes = []
    level_info = []
    residual = signal.copy()
    original_energy = np.sum(signal**2)
    
    # Import scipy for decimation
    try:
        from scipy.signal import decimate, butter, filtfilt
    except ImportError:
        print("⚠️ scipy not available - using simple downsampling")
        use_anti_aliasing = False
    
    for level in range(max_levels):
        print(f"\n📊 Level {level + 1}/{max_levels}")
        
        # Check if we have enough samples for this level
        downsample_factor = 2 ** level
        samples_at_level = len(residual) // downsample_factor
        
        if samples_at_level < min_samples_per_level:
            print(f"⏹️ Stopping: Only {samples_at_level} samples at level {level + 1}")
            break
        
        # Prepare signal for this level
        if level == 0:
            # First level: use original resolution
            signal_level = residual.copy()
            fs_level = fs
            print(f"   Resolution: {len(signal_level)} samples @ {fs_level:.1f} Hz")
        else:
            # Downsample for coarser resolution
            if use_anti_aliasing and 'decimate' in locals():
                # High-quality decimation with anti-aliasing
                try:
                    signal_level = decimate(residual, downsample_factor, 
                                          ftype='fir', zero_phase=True)
                    print(f"   Decimated with anti-aliasing filter")
                except:
                    # Fallback to simple downsampling
                    signal_level = residual[::downsample_factor]
                    print(f"   Simple downsampling (anti-aliasing failed)")
            else:
                # Simple downsampling
                signal_level = residual[::downsample_factor]
            
            fs_level = fs / downsample_factor
            print(f"   Resolution: {len(signal_level)} samples @ {fs_level:.1f} Hz (factor: {downsample_factor})")
        
        # Assess complexity at this level for smart parameters
        level_energy = np.sum(signal_level**2)
        energy_ratio = level_energy / original_energy
        print(f"   Energy at this level: {energy_ratio:.1%}")
        
        # Smart parameter adjustment based on level and energy
        if level == 0:
            # Fine details - use standard parameters
            n_trials_level = None  # Auto-determine
            boundary_method = 'reflect'
        else:
            # Coarser levels - can use fewer trials and simpler boundaries
            complexity_params = assess_signal_complexity(signal_level, fs_level)
            n_trials_level = max(8, complexity_params['n_trials'] // 2)  # Reduce trials
            boundary_method = 'reflect' if level == 1 else 'mirror'  # Simpler for coarse levels
            print(f"   Reduced trials to {n_trials_level} for coarse level")
        
        # Decompose at this level
        try:
            start_time = time.time()
            modes_level, freqs_level, params_level = optuna_optimized_vmd(
                signal_level, fs_level,
                n_trials=n_trials_level,
                boundary_method=boundary_method,
                auto_params=True,
                apply_tapering=False  # Don't taper intermediate results
            )
            level_time = time.time() - start_time
            
            print(f"   ✅ Found {len(modes_level)} modes in {level_time:.2f}s")
            
            # Store level information
            level_info.append({
                'level': level + 1,
                'downsample_factor': downsample_factor,
                'fs': fs_level,
                'n_modes': len(modes_level),
                'frequencies': freqs_level,
                'energy_ratio': energy_ratio,
                'computation_time': level_time,
                'parameters': params_level
            })
            
        except Exception as e:
            print(f"   ❌ Failed at level {level + 1}: {e}")
            break
        
        # Upsample modes back to original resolution if needed
        if level > 0:
            print(f"   🔄 Upsampling {len(modes_level)} modes to original resolution...")
            upsampled_modes = []
            
            for i, mode in enumerate(modes_level):
                if len(mode) == len(signal):
                    # Already correct length
                    upsampled_modes.append(mode)
                else:
                    # High-quality interpolation
                    time_original = np.linspace(0, 1, len(signal))
                    time_decimated = np.linspace(0, 1, len(mode))
                    
                    # Use cubic interpolation for smooth upsampling
                    upsampled = np.interp(time_original, time_decimated, mode)
                    upsampled_modes.append(upsampled)
            
            modes_level = upsampled_modes
            print(f"   ✅ Upsampled to {len(modes_level[0])} samples")
        
        # Add modes to collection
        all_modes.extend(modes_level)
        
        # Update residual for next level
        level_reconstruction = np.sum(modes_level, axis=0)
        new_residual = residual - level_reconstruction
        residual_energy = np.sum(new_residual**2)
        residual_ratio = residual_energy / original_energy
        
        print(f"   📉 Residual energy: {residual_ratio:.1%}")
        
        # Check if we should stop (low residual energy)
        if residual_ratio < energy_threshold:
            print(f"⏹️ Stopping: Residual energy below threshold ({residual_ratio:.1%} < {energy_threshold:.1%})")
            break
        
        residual = new_residual
    
    print(f"\n🎯 Hierarchical decomposition complete!")
    print(f"   Total modes found: {len(all_modes)}")
    print(f"   Levels processed: {len(level_info)}")
    
    # Intelligent mode merging across levels
    print("🔧 Merging similar modes across resolution levels...")
    
    # More aggressive merging for hierarchical decomposition
    merged_modes = merge_similar_modes(all_modes, fs, freq_tol=0.2)
    print(f"   Merged to {len(merged_modes)} distinct modes")
    
    # Sort by frequency for final output
    sorted_modes, sorted_freqs = sort_modes_by_frequency(merged_modes, fs, low_to_high=True)
    
    # Final energy check
    final_reconstruction = np.sum(sorted_modes, axis=0)
    final_mse = np.mean((signal - final_reconstruction)**2)
    final_energy_ratio = np.sum((signal - final_reconstruction)**2) / original_energy
    
    print(f"📊 Final Quality Metrics:")
    print(f"   MSE: {final_mse:.3e}")
    print(f"   Residual Energy: {final_energy_ratio:.1%}")
    print(f"   Final Mode Count: {len(sorted_modes)}")
    
    return np.array(sorted_modes), sorted_freqs, level_info

def print_hierarchical_summary(level_info):
    """Print detailed summary of hierarchical decomposition"""
    print("\n" + "="*60)
    print("🔍 HIERARCHICAL VMD SUMMARY")
    print("="*60)
    
    total_modes = sum(info['n_modes'] for info in level_info)
    total_time = sum(info['computation_time'] for info in level_info)
    
    print(f"📊 Overall Statistics:")
    print(f"   Levels processed: {len(level_info)}")
    print(f"   Total modes found: {total_modes}")
    print(f"   Total computation time: {total_time:.2f}s")
    print(f"   Average time per level: {total_time/len(level_info):.2f}s")
    
    print(f"\n📋 Level Details:")
    for info in level_info:
        print(f"   Level {info['level']}:")
        print(f"      Sampling rate: {info['fs']:.1f} Hz")
        print(f"      Downsample factor: {info['downsample_factor']}x")
        print(f"      Modes found: {info['n_modes']}")
        print(f"      Energy ratio: {info['energy_ratio']:.1%}")
        print(f"      Computation time: {info['computation_time']:.2f}s")
        print(f"      Dominant frequencies: {[f'{f:.1f}' for f in info['frequencies'][:3]]} Hz")

# Enhanced main function with hierarchical option
def ultra_fast_vmd(signal, fs, method='standard', **kwargs):
    """
    Main VMD function with multiple decomposition methods
    
    Parameters:
    -----------
    method : str
        'standard' - Regular optimized VMD
        'hierarchical' - Multi-resolution hierarchical VMD
    """
    if method == 'hierarchical':
        return hierarchical_vmd(signal, fs, **kwargs)
    else:
        return optuna_optimized_vmd(signal, fs, **kwargs)

# ==============================================
# Enhanced Optuna with Smart Caching and Complexity Assessment
# ==============================================
_cache = {}
def optuna_objective(trial, signal, fs, precomputed_fft, complexity_params,
                     tau=0.0, DC=0, init=1, tol=1e-6):
    K = trial.suggest_int("K", 2, complexity_params['max_K'])
    alpha = trial.suggest_float("alpha", 
                               complexity_params['alpha_min'], 
                               complexity_params['alpha_max'], log=True)
    
    # 🚀 OPTIMIZATION: Smarter caching with rounded alpha
    cache_key = (K, round(alpha, -1))  # Round to nearest 10
    if cache_key in _cache:
        modes = _cache[cache_key]
    else:
        try:
            modes, _, _ = VMD(None, alpha=alpha, tau=tau, K=K,
                              DC=DC, init=init, tol=tol,
                              precomputed_fft=precomputed_fft,
                              trial=trial)  # <-- pass trial here
            total_energy = np.sum(signal**2)
            modes = [m for m in modes if np.sum(m**2)/total_energy > 0.01]
            
            # 🚀 OPTIMIZATION: Better cache management
            if len(_cache) < 40:  # Slightly larger cache
                _cache[cache_key] = modes
        except optuna.TrialPruned:
            raise  # propagate pruning
        except:
            return 10.0
    if len(modes) == 0:
        return 10.0
    return ovmd_cost(modes, signal, fs)

def optuna_optimized_vmd(signal, fs,
                         n_trials=None,  # Now auto-determined
                         tau=0.0, DC=0, init=1, tol=None,  # Now auto-determined
                         boundary_method='reflect',
                         apply_tapering=True,
                         auto_params=True):  # New parameter
    global _cache
    _cache.clear()
    
    # 🚀 NEW: Assess signal complexity and get smart parameters
    if auto_params:
        complexity_params = assess_signal_complexity(signal, fs)
        if n_trials is None:
            n_trials = complexity_params['n_trials']
        if tol is None:
            tol = complexity_params['tol']
        print(f"🎯 Auto-tuned: n_trials={n_trials}, tol={tol:.0e}, max_K={complexity_params['max_K']}")
    else:
        # Fallback to original behavior
        complexity_params = {
            'max_K': 6, 'alpha_min': 500, 'alpha_max': 5000, 
            'early_stop_patience': 5
        }
        if n_trials is None:
            n_trials = 30
        if tol is None:
            tol = 1e-6
    
    # 🚀 Smart trial reduction for long signals (additional optimization)
    if len(signal) > 2000 and auto_params:
        n_trials = max(10, n_trials // 2)
        print(f"📉 Reduced trials to {n_trials} for long signal")
    
    # Precompute FFT once for all trials
    print("🔄 Computing FFT and boundaries...")
    precomputed_fft = precompute_vmd_fft(signal, boundary_method)
    
    def objective_wrapper(trial):
        return optuna_objective(trial, signal, fs, precomputed_fft, complexity_params, tau, DC, init, tol)
    
    # ✅ Enable pruning with complexity-aware settings
    pruner = optuna.pruners.MedianPruner(
        n_warmup_steps=max(2, complexity_params.get('early_stop_patience', 5) - 2),
        n_startup_trials=min(5, n_trials // 3)
    )
    
    # 🚀 Smart sampler selection
    if len(signal) > 1500:
        sampler = optuna.samplers.TPESampler(n_startup_trials=3)
    else:
        sampler = optuna.samplers.TPESampler(n_startup_trials=5)
    
    study = optuna.create_study(direction="minimize", pruner=pruner, sampler=sampler)
    
    print(f"🔍 Running {n_trials} optimization trials...")
    study.optimize(objective_wrapper, n_trials=n_trials, show_progress_bar=True, n_jobs=-1)
    
    best_K = int(study.best_params["K"])
    best_alpha = study.best_params["alpha"]
    best_cost = study.best_value
    print(f"[Fast-VMD] ✅ Optimal K={best_K}, alpha={best_alpha:.1f}, cost={best_cost:.4f}")
    
    print("🏁 Computing final decomposition...")
    best_modes, _, _ = VMD(None, alpha=best_alpha, tau=tau, K=best_K,
                           DC=DC, init=init, tol=tol,
                           precomputed_fft=precomputed_fft)
    total_energy = np.sum(signal**2)
    best_modes = [m for m in best_modes if np.sum(m**2)/total_energy > 0.01]
    merged_modes = merge_similar_modes(best_modes, fs, freq_tol=0.15)
    sorted_modes, sorted_freqs = sort_modes_by_frequency(merged_modes, fs, low_to_high=True)
    if apply_tapering:
        taper_len = min(100, len(signal)//10)
        sorted_modes = taper_boundaries(sorted_modes, taper_len)
    
    # 🚀 Save FFTW wisdom after first successful run
    save_fftw_wisdom()
    
    return np.array(sorted_modes), sorted_freqs, (best_K, best_alpha, best_cost)


# ==============================================
# Test Script (UNCHANGED)
# ==============================================
if __name__ == "__main__":
    import matplotlib.pyplot as plt, time
    t = np.linspace(0, 8, 1500)
    fs = len(t)/(t[-1]-t[0])
    signal = (0.3*t +
              np.sin(2*np.pi*4*t) +
              0.6*np.sin(2*np.pi*15*t) +
              0.4*np.sin(2*np.pi*35*t) +
              0.05*np.random.normal(size=len(t)))
    print("🚀 Testing both Standard and Hierarchical VMD...")
    
    # Test standard VMD
    print("\n" + "="*50)
    print("🔧 STANDARD VMD")
    print("="*50)
    start_time = time.time()
    modes_std, freqs_std, params_std = optuna_optimized_vmd(signal, fs, 
                                                            boundary_method='reflect',
                                                            apply_tapering=False,
                                                            auto_params=True)
    std_time = time.time() - start_time
    print(f"✅ Standard VMD completed in {std_time:.2f}s")
    
    # Test hierarchical VMD
    print("\n" + "="*50) 
    print("🏗️ HIERARCHICAL VMD")
    print("="*50)
    start_time = time.time()
    modes_hier, freqs_hier, level_info = hierarchical_vmd(signal, fs, 
                                                          max_levels=3,
                                                          energy_threshold=0.02)
    hier_time = time.time() - start_time
    
    # Print detailed summary
    print_hierarchical_summary(level_info)
    
    print(f"\n⚡ PERFORMANCE COMPARISON:")
    print(f"   Standard VMD: {std_time:.2f}s ({len(modes_std)} modes)")
    print(f"   Hierarchical VMD: {hier_time:.2f}s ({len(modes_hier)} modes)")
    print(f"   Time ratio: {hier_time/std_time:.1f}x")
    
    # Compare reconstruction quality
    recon_std = np.sum(modes_std, axis=0)
    recon_hier = np.sum(modes_hier, axis=0)
    mse_std = np.mean((signal - recon_std)**2)
    mse_hier = np.mean((signal - recon_hier)**2)
    
    print(f"\n🎯 QUALITY COMPARISON:")
    print(f"   Standard MSE: {mse_std:.3e}")
    print(f"   Hierarchical MSE: {mse_hier:.3e}")
    print(f"   Quality ratio: {mse_hier/mse_std:.2f}x {'(better)' if mse_hier < mse_std else '(worse)'}")
    
    # 🚀 Memory cleanup
    clear_memory_pool()
    
    # Choose better result for plotting
    if mse_hier < mse_std:
        modes, freqs, method_used = modes_hier, freqs_hier, "Hierarchical"
        elapsed = hier_time
    else:
        modes, freqs, method_used = modes_std, freqs_std, "Standard" 
        elapsed = std_time
    
    print(f"\n📊 Using {method_used} VMD result for visualization")
    total_energy = np.sum(signal**2)
    fig, axes = plt.subplots(len(modes)+2, 1, figsize=(14, 2.2*(len(modes)+2)))
    axes[0].plot(t, signal, 'b-', alpha=0.8)
    axes[0].set_title("Original Signal")
    for i, (m, f) in enumerate(zip(modes, freqs)):
        e_pct = 100*np.sum(m**2)/total_energy
        axes[i+1].plot(t, m, alpha=0.85)
        axes[i+1].set_title(f"Mode {i+1} | Dom freq ~{f:.2f} Hz | Energy {e_pct:.1f}%")
    recon = np.sum(modes, axis=0)
    axes[-1].plot(t, signal, 'b-', label="Original")
    axes[-1].plot(t, recon, 'r--', label="Reconstructed")
    mse = np.mean((signal - recon)**2)
    axes[-1].legend()
    axes[-1].set_title(f"Reconstruction MSE: {mse:.3e} | Best K={params_std[0]}, α={params_std[1]:.1f}")
    plt.tight_layout()
    plt.show()

# %%
# -*- coding: utf-8 -*-
"""
Fast Optuna-Optimized VMD with FFT caching - Refactored and Organized
"""

import numpy as np
import optuna
import pyfftw
import pyfftw.interfaces.numpy_fft as fftw_np
from numba import njit, prange
import os
import pickle
import gc
import time
from typing import Tuple, List, Dict, Optional, Any
from dataclasses import dataclass


@dataclass
class VMDParameters:
    """Configuration parameters for VMD decomposition"""
    n_trials: int = 30
    max_K: int = 6
    tol: float = 1e-6
    alpha_min: float = 500
    alpha_max: float = 5000
    early_stop_patience: int = 5
    tau: float = 0.0
    DC: int = 0
    init: int = 1
    max_iter: int = 300
    boundary_method: str = 'reflect'
    apply_tapering: bool = True


@dataclass
class HierarchicalParameters:
    """Configuration parameters for hierarchical VMD"""
    max_levels: int = 3
    energy_threshold: float = 0.01
    min_samples_per_level: int = 100
    use_anti_aliasing: bool = True


class FFTWManager:
    """Manages FFTW optimization and wisdom caching"""
    
    def __init__(self, wisdom_file: str = "vmd_fftw_wisdom.dat"):
        self.wisdom_file = wisdom_file
        self._setup_fftw()
        self.load_wisdom()
    
    def _setup_fftw(self):
        """Configure FFTW for maximum performance"""
        pyfftw.interfaces.cache.enable()
        pyfftw.interfaces.cache.set_keepalive_time(7200)
        pyfftw.config.NUM_THREADS = -1
    
    def load_wisdom(self):
        """Load FFTW wisdom for faster FFTs"""
        if os.path.exists(self.wisdom_file):
            try:
                with open(self.wisdom_file, 'rb') as f:
                    pyfftw.import_wisdom(pickle.load(f))
                print("🧠 FFTW wisdom loaded - FFTs will be faster!")
            except:
                print("⚠️ Could not load FFTW wisdom file")
    
    def save_wisdom(self):
        """Save FFTW wisdom for future runs"""
        try:
            with open(self.wisdom_file, 'wb') as f:
                pickle.dump(pyfftw.export_wisdom(), f)
            print("💾 FFTW wisdom saved for future speedup")
        except:
            print("⚠️ Could not save FFTW wisdom")


class MemoryManager:
    """Manages memory pools for temporary arrays"""
    
    def __init__(self):
        self._memory_pool = {}
    
    def get_temp_array(self, shape, dtype=np.complex128, clear=True):
        """Get temporary array from memory pool"""
        key = (shape, dtype.__name__ if hasattr(dtype, '__name__') else str(dtype))
        if key not in self._memory_pool:
            self._memory_pool[key] = np.zeros(shape, dtype=dtype)
        
        arr = self._memory_pool[key]
        if clear:
            arr.fill(0)
        return arr
    
    def clear_pool(self):
        """Clear memory pool to free RAM"""
        self._memory_pool.clear()
        gc.collect()


class SignalAnalyzer:
    """Analyzes signal characteristics for parameter optimization"""
    
    @staticmethod
    def assess_complexity(signal: np.ndarray, fs: float) -> VMDParameters:
        """Determine optimal parameters based on signal characteristics"""
        signal_len = len(signal)
        
        # Spectral analysis
        spec = np.abs(fftw_np.rfft(signal))
        freqs = fftw_np.rfftfreq(signal_len, 1/fs)
        
        # Spectral entropy (measure of complexity)
        spec_norm = spec / (np.sum(spec) + 1e-12)
        spectral_entropy = -np.sum(spec_norm * np.log(spec_norm + 1e-12))
        
        # Dominant frequency analysis
        spec[0] = 0  # Remove DC
        peak_idx = np.argmax(spec)
        dominant_freq = freqs[peak_idx]
        
        # Energy distribution
        energy_threshold = 0.05 * np.max(spec)
        significant_freqs = freqs[spec > energy_threshold]
        freq_spread = len(significant_freqs) / len(freqs)
        
        # Derivative-based complexity
        signal_diff = np.diff(signal)
        variability = np.std(signal_diff) / (np.std(signal) + 1e-12)
        
        # Determine complexity level
        complexity_score = (
            0.4 * (spectral_entropy / 10.0) +
            0.3 * freq_spread +
            0.3 * min(variability, 2.0) / 2.0
        )
        
        # Smart parameter recommendations
        if complexity_score < 0.3:  # Simple signal
            params = VMDParameters(
                n_trials=max(10, min(15, signal_len // 200)),
                max_K=4, tol=1e-5, alpha_min=1000, alpha_max=3000,
                early_stop_patience=3
            )
        elif complexity_score < 0.6:  # Moderate complexity
            params = VMDParameters(
                n_trials=max(15, min(25, signal_len // 150)),
                max_K=6, tol=1e-6, alpha_min=500, alpha_max=5000,
                early_stop_patience=5
            )
        else:  # Complex signal
            params = VMDParameters(
                n_trials=max(20, min(35, signal_len // 100)),
                max_K=8, tol=1e-7, alpha_min=200, alpha_max=8000,
                early_stop_patience=7
            )
        
        # Adjust for signal length
        if signal_len > 3000:
            params.n_trials = max(10, params.n_trials // 2)
            params.tol *= 2
        
        print(f"🧮 Signal complexity: {complexity_score:.3f} | "
              f"Dominant freq: {dominant_freq:.1f} Hz | "
              f"Recommended trials: {params.n_trials}, max_K: {params.max_K}")
        
        return params


class BoundaryHandler:
    """Handles signal boundary conditions and windowing"""
    
    @staticmethod
    def apply_window(signal: np.ndarray, window_type: str = 'tukey', alpha_win: float = 0.1) -> Tuple[np.ndarray, np.ndarray]:
        """Apply windowing function to signal"""
        N = len(signal)
        if window_type == 'tukey':
            from scipy.signal import windows
            window = windows.tukey(N, alpha_win)
        elif window_type == 'hann':
            window = np.hanning(N)
        elif window_type == 'hamming':
            window = np.hamming(N)
        else:
            window = np.ones(N)
        return signal * window, window
    
    @staticmethod
    def extend_signal(signal: np.ndarray, method: str = 'mirror', extension_ratio: float = 0.25) -> Tuple[np.ndarray, int, int]:
        """Extend signal using various methods"""
        N = len(signal)
        ext_len = int(N * extension_ratio)
        
        if method == 'mirror':
            left_ext = signal[1:ext_len+1][::-1]
            right_ext = signal[-(ext_len+1):-1][::-1]
            extended = np.concatenate([left_ext, signal, right_ext])
        elif method == 'reflect':
            left_val = signal[0]
            right_val = signal[-1]
            left_ext = 2*left_val - signal[1:ext_len+1][::-1]
            right_ext = 2*right_val - signal[-(ext_len+1):-1][::-1]
            extended = np.concatenate([left_ext, signal, right_ext])
        elif method == 'linear':
            left_slope = (signal[1] - signal[0])
            right_slope = (signal[-1] - signal[-2])
            left_ext = signal[0] + left_slope * np.arange(-ext_len, 0)
            right_ext = signal[-1] + right_slope * np.arange(1, ext_len+1)
            extended = np.concatenate([left_ext, signal, right_ext])
        elif method == 'constant':
            left_ext = np.full(ext_len, signal[0])
            right_ext = np.full(ext_len, signal[-1])
            extended = np.concatenate([left_ext, signal, right_ext])
        else:
            return signal, 0, 0
        
        return extended, ext_len, ext_len
    
    @staticmethod
    def taper_boundaries(modes: List[np.ndarray], taper_length: int = 50) -> List[np.ndarray]:
        """Apply boundary tapering to modes"""
        tapered_modes = []
        for mode in modes:
            tapered = mode.copy()
            N = len(mode)
            taper_len = min(taper_length, N//4)
            taper = np.ones(N)
            taper[:taper_len] = np.sin(np.linspace(0, np.pi/2, taper_len))**2
            taper[-taper_len:] = np.cos(np.linspace(0, np.pi/2, taper_len))**2
            tapered_modes.append(tapered * taper)
        return tapered_modes
    
    @staticmethod
    def adaptive_extension_ratio(signal: np.ndarray) -> float:
        """Calculate adaptive extension ratio based on signal length"""
        N = len(signal)
        if N < 500:
            return 0.3
        elif N < 2000:
            return 0.2
        else:
            return 0.15
    
    @staticmethod
    def auto_window_alpha(signal: np.ndarray, min_alpha: float = 0.01, max_alpha: float = 0.1) -> float:
        """Adaptive Tukey window alpha based on derivative variance"""
        deriv = np.diff(signal)
        deriv_var = np.var(deriv)
        norm_var = deriv_var / (np.mean(np.abs(signal))**2 + 1e-12)
        smoothness_factor = 1.0 / (1.0 + norm_var)
        alpha = min_alpha + (max_alpha - min_alpha) * smoothness_factor
        return alpha


class VMDCore:
    """Core VMD implementation with optimized algorithms"""
    
    def __init__(self, fftw_manager: FFTWManager, boundary_handler: BoundaryHandler):
        self.fftw_manager = fftw_manager
        self.boundary_handler = boundary_handler
    
    def precompute_fft(self, signal: np.ndarray, boundary_method: str = 'reflect', 
                      use_soft_junction: bool = False, window_alpha: Optional[float] = None) -> Dict[str, Any]:
        """Precompute FFT and boundary handling for all trials"""
        orig_len = len(signal)
        if len(signal) % 2:
            signal = signal[:-1]
        
        # Extension
        if boundary_method != 'none':
            ratio = self.boundary_handler.adaptive_extension_ratio(signal)
            fMirr, left_ext, right_ext = self.boundary_handler.extend_signal(
                signal, method=boundary_method, extension_ratio=ratio
            )
        else:
            fMirr = signal
            left_ext = right_ext = 0
        
        # Soft junction smoothing
        if use_soft_junction and boundary_method != 'none':
            fMirr = self._smooth_edge_junction(fMirr, orig_len, left_ext)
        
        # Window application
        if window_alpha is None:
            window_alpha = self.boundary_handler.auto_window_alpha(signal)
        
        if window_alpha > 0:
            from scipy.signal import windows
            win = windows.tukey(len(fMirr), alpha=window_alpha)
            fMirr = fMirr * win
        
        # FFT computation
        T = len(fMirr)
        freqs = np.fft.fftshift(np.fft.fftfreq(T))
        f_hat = fftw_np.fftshift(fftw_np.fft(fMirr))
        f_hat_plus = f_hat.copy()
        f_hat_plus[:T // 2] = 0
        
        return {
            "f_hat_plus": f_hat_plus,
            "freqs": freqs,
            "T": T,
            "half_T": T // 2,
            "orig_len": orig_len,
            "left_ext": left_ext,
            "right_ext": right_ext
        }
    
    def _smooth_edge_junction(self, extended_signal: np.ndarray, original_len: int, 
                             ext_len: int, smooth_ratio: float = 0.02) -> np.ndarray:
        """Smooth junction between mirrored edges and original signal"""
        taper_len = max(2, int(original_len * smooth_ratio))
        ramp_up = 0.5 * (1 - np.cos(np.linspace(0, np.pi, taper_len)))
        ramp_down = ramp_up[::-1]
        
        # Apply smoothing
        extended_signal[ext_len - taper_len:ext_len] *= ramp_up
        end_idx = ext_len + original_len
        extended_signal[end_idx:end_idx + taper_len] *= ramp_down
        
        return extended_signal
    
    def init_from_spectrum(self, signal: np.ndarray, K: int) -> np.ndarray:
        """Initialize omega from K largest FFT peaks"""
        spec = np.abs(fftw_np.rfft(signal))
        freqs = fftw_np.rfftfreq(len(signal))
        peak_idx = np.argsort(spec)[-K:]
        return np.sort(freqs[peak_idx])
    
    def decompose(self, f: Optional[np.ndarray], alpha: float, tau: float, K: int, 
                 DC: int, init: int, tol: float, boundary_method: str = 'reflect',
                 max_iter: int = 300, precomputed_fft: Optional[Dict] = None,
                 trial: Optional[Any] = None) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Core VMD decomposition algorithm"""
        # Use precomputed FFT if available
        if precomputed_fft is not None:
            f_hat_plus = precomputed_fft["f_hat_plus"]
            freqs = precomputed_fft["freqs"]
            T = precomputed_fft["T"]
            half_T = precomputed_fft["half_T"]
            orig_len = precomputed_fft["orig_len"]
            left_ext = precomputed_fft["left_ext"]
            right_ext = precomputed_fft["right_ext"]
        else:
            # Fallback to normal computation
            orig_len = len(f)
            if len(f) % 2:
                f = f[:-1]
            if boundary_method != 'none':
                fMirr, left_ext, right_ext = self.boundary_handler.extend_signal(
                    f, method=boundary_method, extension_ratio=0.3
                )
            else:
                fMirr = f
                left_ext = right_ext = 0
            T = len(fMirr)
            freqs = np.linspace(0, 1, T) - 0.5 - 1.0/T
            f_hat = fftw_np.fftshift(fftw_np.fft(fMirr))
            f_hat_plus = f_hat.copy()
            f_hat_plus[:T // 2] = 0
            half_T = T // 2
        
        # Initialize parameters
        Alpha = alpha * np.ones(K)
        omega_curr = np.zeros(K)
        
        if init == 1:
            omega_curr = np.arange(K) * (0.5 / K)
        elif init == 2:
            fs = 1 / T
            omega_curr = np.sort(np.exp(np.log(fs) + (np.log(0.5) - np.log(fs)) * np.random.rand(K)))
        elif init == 3:
            omega_curr = self.init_from_spectrum(fMirr if 'fMirr' in locals() else f, K)
        
        if DC:
            omega_curr[0] = 0.0
        
        # Initialize variables
        lambda_curr = np.zeros(len(freqs), dtype=np.complex128)
        sum_uk = np.zeros(len(freqs), dtype=np.complex128)
        u_hat_prev = np.zeros((len(freqs), K), dtype=np.complex128)
        uDiff = tol + 1.0
        
        # Optimization variables
        stagnation_count = 0
        prev_diff = float('inf')
        adaptive_tol = max(tol, 1e-7)
        
        # Main iteration loop
        for n in range(max_iter):
            u_hat_next, omega_next, sum_uk, lambda_next, diff_norm = self._update_modes_numba(
                freqs, half_T, f_hat_plus, sum_uk, lambda_curr, Alpha, omega_curr, u_hat_prev, K, tau
            )
            
            if n > 5:
                uDiff = diff_norm
            
            # Smart early stopping
            if n > 10:
                if abs(diff_norm - prev_diff) < adaptive_tol * 0.1:
                    stagnation_count += 1
                else:
                    stagnation_count = 0
                
                if stagnation_count >= 5:
                    break
            
            # Optuna pruning
            if trial is not None and n % 15 == 0:
                trial.report(uDiff, step=n)
                if trial.should_prune():
                    raise optuna.TrialPruned()
            
            # Update variables
            u_hat_prev = u_hat_next
            lambda_curr = lambda_next
            omega_curr = omega_next
            prev_diff = diff_norm
            
            if uDiff <= tol:
                break
        
        # Reconstruction
        u_hat_full = np.zeros((T, K), dtype=np.complex128)
        u_hat_full[half_T:T, :] = u_hat_prev[half_T:T, :]
        idxs = np.arange(1, half_T)
        u_hat_full[idxs, :] = np.conj(u_hat_full[T - idxs, :])
        u_hat_full[0, :] = np.conj(u_hat_full[-1, :])
        
        # Inverse FFT
        u = np.real(fftw_np.ifft(fftw_np.ifftshift(u_hat_full, axes=0), axis=0)).T
        
        # Extract original signal portion
        if precomputed_fft is not None or boundary_method != 'none':
            start_idx = left_ext
            end_idx = start_idx + orig_len
            u = u[:, start_idx:end_idx]
        
        # Interpolate to original length if needed
        if u.shape[1] != orig_len:
            x_old = np.linspace(0, 1, u.shape[1])
            x_new = np.linspace(0, 1, orig_len)
            u = np.vstack([np.interp(x_new, x_old, mode) for mode in u])
        
        return u, u_hat_full, omega_curr
    
    @staticmethod
    def _update_modes_numba(freqs, half_T, f_hat_plus, sum_uk, lambda_hat_n, Alpha, omega_n, u_hat_prev, K, tau):
        """Numba-optimized core update loop - keeping original implementation"""
        return update_modes_numba(freqs, half_T, f_hat_plus, sum_uk, lambda_hat_n, Alpha, omega_n, u_hat_prev, K, tau)


class ModeProcessor:
    """Handles mode processing and analysis"""
    
    @staticmethod
    def get_dominant_frequency(sig: np.ndarray, fs: float) -> float:
        """Get dominant frequency of a signal"""
        N = len(sig)
        if N < 4 or np.allclose(sig, 0, atol=1e-12):
            return 0.0
        freqs = fftw_np.rfftfreq(N, d=1/fs)
        spec = np.abs(fftw_np.rfft(sig))
        if len(spec) == 0:
            return 0.0
        spec[0] = 0
        return freqs[np.argmax(spec)]
    
    def merge_similar_modes(self, modes: List[np.ndarray], fs: float, freq_tol: float = 0.1) -> List[np.ndarray]:
        """Merge modes with similar dominant frequencies"""
        if len(modes) <= 1:
            return modes
        
        dom_freqs = [self.get_dominant_frequency(m, fs) for m in modes]
        merged = []
        used = np.zeros(len(modes), dtype=bool)
        
        for i in range(len(modes)):
            if used[i]:
                continue
            group = [modes[i]]
            fi = dom_freqs[i]
            used[i] = True
            
            for j in range(i+1, len(modes)):
                if used[j]:
                    continue
                fj = dom_freqs[j]
                if abs(fi-fj)/max(fi,1e-6) < freq_tol:
                    group.append(modes[j])
                    used[j] = True
            
            merged.append(np.sum(group, axis=0))
        
        return merged
    
    def sort_modes_by_frequency(self, modes: List[np.ndarray], fs: float, 
                               low_to_high: bool = True) -> Tuple[List[np.ndarray], List[float]]:
        """Sort modes by their dominant frequencies"""
        dom_freqs = [self.get_dominant_frequency(m, fs) for m in modes]
        order = np.argsort(dom_freqs)
        if not low_to_high:
            order = order[::-1]
        return [modes[i] for i in order], [dom_freqs[i] for i in order]
    
    @staticmethod
    def calculate_cost(modes: List[np.ndarray], signal: np.ndarray, fs: float) -> float:
        """Calculate VMD cost function"""
        if len(modes) == 0:
            return 10.0
        
        total_energy = np.sum(signal**2)
        recon = np.sum(modes, axis=0)
        residual_energy = np.sum((signal - recon)**2) / total_energy
        
        # Overlap penalty
        dom_freqs = [ModeProcessor.get_dominant_frequency(m, fs) for m in modes]
        overlap_penalty = np.mean(np.exp(-np.diff(np.sort(dom_freqs)))) if len(dom_freqs) > 1 else 0.0
        
        # Entropy calculation
        entropy_vals = []
        for m in modes:
            spec = np.abs(fftw_np.rfft(m)) + 1e-12
            p = spec / np.sum(spec)
            entropy_vals.append(-np.mean(p * np.log(p + 1e-12)))
        avg_entropy = np.mean(entropy_vals) / np.log(len(modes) + 1)
        
        return 0.7*residual_energy + 0.2*overlap_penalty + 0.1*avg_entropy


class HierarchicalVMD:
    """Hierarchical Multi-Resolution VMD implementation"""
    
    def __init__(self, vmd_optimizer):
        self.vmd_optimizer = vmd_optimizer
    
    def decompose(self, signal: np.ndarray, fs: float, params: HierarchicalParameters) -> Tuple[np.ndarray, List[float], List[Dict]]:
        """Perform hierarchical VMD decomposition"""
        print(f"🔍 Starting Hierarchical VMD (max_levels={params.max_levels})...")
        
        all_modes = []
        level_info = []
        residual = signal.copy()
        original_energy = np.sum(signal**2)
        
        # Import scipy for decimation
        try:
            from scipy.signal import decimate
        except ImportError:
            print("⚠️ scipy not available - using simple downsampling")
            params.use_anti_aliasing = False
        
        for level in range(params.max_levels):
            print(f"\n📊 Level {level + 1}/{params.max_levels}")
            
            # Check sample count
            downsample_factor = 2 ** level
            samples_at_level = len(residual) // downsample_factor
            
            if samples_at_level < params.min_samples_per_level:
                print(f"⏹️ Stopping: Only {samples_at_level} samples at level {level + 1}")
                break
            
            # Prepare signal for this level
            if level == 0:
                signal_level = residual.copy()
                fs_level = fs
                print(f"   Resolution: {len(signal_level)} samples @ {fs_level:.1f} Hz")
            else:
                if params.use_anti_aliasing and 'decimate' in locals():
                    try:
                        signal_level = decimate(residual, downsample_factor, ftype='fir', zero_phase=True)
                        print(f"   Decimated with anti-aliasing filter")
                    except:
                        signal_level = residual[::downsample_factor]
                        print(f"   Simple downsampling (anti-aliasing failed)")
                else:
                    signal_level = residual[::downsample_factor]
                
                fs_level = fs / downsample_factor
                print(f"   Resolution: {len(signal_level)} samples @ {fs_level:.1f} Hz (factor: {downsample_factor})")
            
            # Energy analysis
            level_energy = np.sum(signal_level**2)
            energy_ratio = level_energy / original_energy
            print(f"   Energy at this level: {energy_ratio:.1%}")
            
            # Decompose at this level
            try:
                start_time = time.time()
                modes_level, freqs_level, params_level = self.vmd_optimizer.optimize(
                    signal_level, fs_level,
                    n_trials=max(8, 15 // (level + 1)) if level > 0 else None,
                    boundary_method='reflect' if level <= 1 else 'mirror',
                    auto_params=True,
                    apply_tapering=False
                )
                level_time = time.time() - start_time
                
                print(f"   ✅ Found {len(modes_level)} modes in {level_time:.2f}s")
                
                # Store level info
                level_info.append({
                    'level': level + 1,
                    'downsample_factor': downsample_factor,
                    'fs': fs_level,
                    'n_modes': len(modes_level),
                    'frequencies': freqs_level,
                    'energy_ratio': energy_ratio,
                    'computation_time': level_time,
                    'parameters': params_level
                })
                
            except Exception as e:
                print(f"   ❌ Failed at level {level + 1}: {e}")
                break
            
            # Upsample modes if needed
            if level > 0:
                print(f"   🔄 Upsampling {len(modes_level)} modes to original resolution...")
                upsampled_modes = []
                
                for mode in modes_level:
                    if len(mode) == len(signal):
                        upsampled_modes.append(mode)
                    else:
                        time_original = np.linspace(0, 1, len(signal))
                        time_decimated = np.linspace(0, 1, len(mode))
                        upsampled = np.interp(time_original, time_decimated, mode)
                        upsampled_modes.append(upsampled)
                
                modes_level = upsampled_modes
                print(f"   ✅ Upsampled to {len(modes_level[0])} samples")
            
            # Update residual
            all_modes.extend(modes_level)
            level_reconstruction = np.sum(modes_level, axis=0)
            new_residual = residual - level_reconstruction
            residual_energy = np.sum(new_residual**2)
            residual_ratio = residual_energy / original_energy
            
            print(f"   📉 Residual energy: {residual_ratio:.1%}")
            
            if residual_ratio < params.energy_threshold:
                print(f"⏹️ Stopping: Residual energy below threshold ({residual_ratio:.1%} < {params.energy_threshold:.1%})")
                break
            
            residual = new_residual
        
        print(f"\n🎯 Hierarchical decomposition complete!")
        print(f"   Total modes found: {len(all_modes)}")
        print(f"   Levels processed: {len(level_info)}")
        
        # Process final modes
        mode_processor = ModeProcessor()
        merged_modes = mode_processor.merge_similar_modes(all_modes, fs, freq_tol=0.2)
        print(f"   Merged to {len(merged_modes)} distinct modes")
        
        sorted_modes, sorted_freqs = mode_processor.sort_modes_by_frequency(merged_modes, fs, low_to_high=True)
        
        # Quality metrics
        final_reconstruction = np.sum(sorted_modes, axis=0)
        final_mse = np.mean((signal - final_reconstruction)**2)
        final_energy_ratio = np.sum((signal - final_reconstruction)**2) / original_energy
        
        print(f"📊 Final Quality Metrics:")
        print(f"   MSE: {final_mse:.3e}")
        print(f"   Residual Energy: {final_energy_ratio:.1%}")
        print(f"   Final Mode Count: {len(sorted_modes)}")
        
        return np.array(sorted_modes), sorted_freqs, level_info
    
    @staticmethod
    def print_summary(level_info: List[Dict]):
        """Print detailed summary of hierarchical decomposition"""
        print("\n" + "="*60)
        print("🔍 HIERARCHICAL VMD SUMMARY")
        print("="*60)
        
        total_modes = sum(info['n_modes'] for info in level_info)
        total_time = sum(info['computation_time'] for info in level_info)
        
        print(f"📊 Overall Statistics:")
        print(f"   Levels processed: {len(level_info)}")
        print(f"   Total modes found: {total_modes}")
        print(f"   Total computation time: {total_time:.2f}s")
        print(f"   Average time per level: {total_time/len(level_info):.2f}s")
        
        print(f"\n📋 Level Details:")
        for info in level_info:
            print(f"   Level {info['level']}:")
            print(f"      Sampling rate: {info['fs']:.1f} Hz")
            print(f"      Downsample factor: {info['downsample_factor']}x")
            print(f"      Modes found: {info['n_modes']}")
            print(f"      Energy ratio: {info['energy_ratio']:.1%}")
            print(f"      Computation time: {info['computation_time']:.2f}s")
            print(f"      Dominant frequencies: {[f'{f:.1f}' for f in info['frequencies'][:3]]} Hz")


class VMDOptimizer:
    """Main VMD optimizer using Optuna"""
    
    def __init__(self, fftw_manager: FFTWManager, memory_manager: MemoryManager):
        self.fftw_manager = fftw_manager
        self.memory_manager = memory_manager
        self.vmd_core = VMDCore(fftw_manager, BoundaryHandler())
        self.mode_processor = ModeProcessor()
        self.signal_analyzer = SignalAnalyzer()
        self._cache = {}
    
    def _objective(self, trial, signal: np.ndarray, fs: float, precomputed_fft: Dict, 
                  complexity_params: VMDParameters) -> float:
        """Optuna objective function"""
        K = trial.suggest_int("K", 2, complexity_params.max_K)
        alpha = trial.suggest_float("alpha", complexity_params.alpha_min, 
                                   complexity_params.alpha_max, log=True)
        
        # Smart caching with rounded alpha
        cache_key = (K, round(alpha, -1))
        if cache_key in self._cache:
            modes = self._cache[cache_key]
        else:
            try:
                modes, _, _ = self.vmd_core.decompose(
                    None, alpha=alpha, tau=complexity_params.tau, K=K,
                    DC=complexity_params.DC, init=complexity_params.init, 
                    tol=complexity_params.tol, precomputed_fft=precomputed_fft,
                    trial=trial
                )
                
                total_energy = np.sum(signal**2)
                modes = [m for m in modes if np.sum(m**2)/total_energy > 0.01]
                
                # Cache management
                if len(self._cache) < 40:
                    self._cache[cache_key] = modes
            except optuna.TrialPruned:
                raise
            except:
                return 10.0
        
        if len(modes) == 0:
            return 10.0
        
        return self.mode_processor.calculate_cost(modes, signal, fs)
    
    def optimize(self, signal: np.ndarray, fs: float, n_trials: Optional[int] = None,
                tau: float = 0.0, DC: int = 0, init: int = 1, tol: Optional[float] = None,
                boundary_method: str = 'reflect', apply_tapering: bool = True,
                auto_params: bool = True) -> Tuple[np.ndarray, List[float], Tuple[int, float, float]]:
        """Optimize VMD parameters using Optuna"""
        self._cache.clear()
        
        # Get complexity-based parameters
        if auto_params:
            complexity_params = self.signal_analyzer.assess_complexity(signal, fs)
            if n_trials is None:
                n_trials = complexity_params.n_trials
            if tol is None:
                tol = complexity_params.tol
            print(f"🎯 Auto-tuned: n_trials={n_trials}, tol={tol:.0e}, max_K={complexity_params.max_K}")
        else:
            complexity_params = VMDParameters(max_K=6, alpha_min=500, alpha_max=5000)
            if n_trials is None:
                n_trials = 30
            if tol is None:
                tol = 1e-6
        
        # Update parameters
        complexity_params.tau = tau
        complexity_params.DC = DC
        complexity_params.init = init
        complexity_params.tol = tol
        
        # Smart trial reduction for long signals
        if len(signal) > 2000 and auto_params:
            n_trials = max(10, n_trials // 2)
            print(f"📉 Reduced trials to {n_trials} for long signal")
        
        # Precompute FFT
        print("🔄 Computing FFT and boundaries...")
        precomputed_fft = self.vmd_core.precompute_fft(signal, boundary_method)
        
        # Setup Optuna study
        pruner = optuna.pruners.MedianPruner(
            n_warmup_steps=max(2, complexity_params.early_stop_patience - 2),
            n_startup_trials=min(5, n_trials // 3)
        )
        
        sampler = optuna.samplers.TPESampler(
            n_startup_trials=3 if len(signal) > 1500 else 5
        )
        
        study = optuna.create_study(direction="minimize", pruner=pruner, sampler=sampler)
        
        # Define objective wrapper
        def objective_wrapper(trial):
            return self._objective(trial, signal, fs, precomputed_fft, complexity_params)
        
        # Optimize
        print(f"🔍 Running {n_trials} optimization trials...")
        study.optimize(objective_wrapper, n_trials=n_trials, show_progress_bar=True, n_jobs=-1)
        
        # Get best parameters
        best_K = int(study.best_params["K"])
        best_alpha = study.best_params["alpha"]
        best_cost = study.best_value
        print(f"[Fast-VMD] ✅ Optimal K={best_K}, alpha={best_alpha:.1f}, cost={best_cost:.4f}")
        
        # Final decomposition
        print("🏁 Computing final decomposition...")
        best_modes, _, _ = self.vmd_core.decompose(
            None, alpha=best_alpha, tau=tau, K=best_K,
            DC=DC, init=init, tol=tol, precomputed_fft=precomputed_fft
        )
        
        # Post-process modes
        total_energy = np.sum(signal**2)
        best_modes = [m for m in best_modes if np.sum(m**2)/total_energy > 0.01]
        merged_modes = self.mode_processor.merge_similar_modes(best_modes, fs, freq_tol=0.15)
        sorted_modes, sorted_freqs = self.mode_processor.sort_modes_by_frequency(
            merged_modes, fs, low_to_high=True
        )
        
        if apply_tapering:
            taper_len = min(100, len(signal)//10)
            sorted_modes = BoundaryHandler.taper_boundaries(sorted_modes, taper_len)
        
        # Save FFTW wisdom
        self.fftw_manager.save_wisdom()
        
        return np.array(sorted_modes), sorted_freqs, (best_K, best_alpha, best_cost)


class FastVMD:
    """Main FastVMD class - unified interface for all VMD methods"""
    
    def __init__(self, wisdom_file: str = "vmd_fftw_wisdom.dat"):
        self.fftw_manager = FFTWManager(wisdom_file)
        self.memory_manager = MemoryManager()
        self.vmd_optimizer = VMDOptimizer(self.fftw_manager, self.memory_manager)
        self.hierarchical_vmd = HierarchicalVMD(self.vmd_optimizer)
    
    def decompose(self, signal: np.ndarray, fs: float, method: str = 'standard', 
                 **kwargs) -> Tuple[np.ndarray, List[float], Any]:
        """
        Main VMD decomposition function
        
        Parameters:
        -----------
        signal : np.ndarray
            Input signal
        fs : float
            Sampling frequency
        method : str
            'standard' - Regular optimized VMD
            'hierarchical' - Multi-resolution hierarchical VMD
        **kwargs
            Additional parameters for specific methods
            
        Returns:
        --------
        modes : np.ndarray
            Decomposed modes
        frequencies : List[float] 
            Dominant frequencies of each mode
        info : Any
            Method-specific information (parameters for standard, level_info for hierarchical)
        """
        if method == 'hierarchical':
            # Parse hierarchical parameters
            hierarchical_params = HierarchicalParameters(
                max_levels=kwargs.get('max_levels', 3),
                energy_threshold=kwargs.get('energy_threshold', 0.01),
                min_samples_per_level=kwargs.get('min_samples_per_level', 100),
                use_anti_aliasing=kwargs.get('use_anti_aliasing', True)
            )
            return self.hierarchical_vmd.decompose(signal, fs, hierarchical_params)
        else:
            # Standard VMD
            return self.vmd_optimizer.optimize(signal, fs, **kwargs)
    
    def clear_cache(self):
        """Clear all caches and memory pools"""
        self.memory_manager.clear_pool()
        self.vmd_optimizer._cache.clear()
    
    def __del__(self):
        """Cleanup on destruction"""
        self.clear_cache()


# Keep the original numba function for compatibility
@njit(parallel=True, fastmath=True)
def update_modes_numba(freqs, half_T, f_hat_plus, sum_uk,
                      lambda_hat_n, Alpha, omega_n, u_hat_prev, K, tau):
    """Numba-optimized mode update function - unchanged from original"""
    T = len(freqs)
    freq_slice_start = half_T
    u_hat_plus_next = np.zeros((T, K), dtype=np.complex128)
    omega_next = np.zeros(K)
    mode_sum = np.zeros(T, dtype=np.complex128)
    diff_norm = 0.0
    eps = 1e-14

    for k in range(K):
        if k == 0:
            sum_uk += u_hat_prev[:, K - 1] - u_hat_prev[:, 0]
        else:
            sum_uk += u_hat_plus_next[:, k - 1] - u_hat_prev[:, k]

        omega_k = omega_n[k]
        alpha_k = Alpha[k]
        
        for i in range(T):
            freq_diff = freqs[i] - omega_k
            denom = 1.0 + alpha_k * freq_diff * freq_diff + eps
            u_hat_plus_next[i, k] = (f_hat_plus[i] - sum_uk[i] - lambda_hat_n[i] * 0.5) / denom

        numerator = 0.0
        denominator = 0.0
        for i in range(freq_slice_start, T):
            weight = u_hat_plus_next[i, k].real**2 + u_hat_plus_next[i, k].imag**2
            numerator += freqs[i] * weight
            denominator += weight
        
        if denominator > eps:
            omega_next[k] = numerator / denominator
        else:
            omega_next[k] = omega_k

        mode_sum += u_hat_plus_next[:, k]
        diff = u_hat_plus_next[:, k] - u_hat_prev[:, k]
        diff_norm += np.real(np.vdot(diff, diff)) / T

    lambda_next = lambda_hat_n + tau * (mode_sum - f_hat_plus)
    return u_hat_plus_next, omega_next, sum_uk, lambda_next, diff_norm


# Backward compatibility functions
def optuna_optimized_vmd(signal, fs, **kwargs):
    """Backward compatibility wrapper for optuna_optimized_vmd"""
    vmd = FastVMD()
    return vmd.decompose(signal, fs, method='standard', **kwargs)


def hierarchical_vmd(signal, fs, **kwargs):
    """Backward compatibility wrapper for hierarchical_vmd"""
    vmd = FastVMD()
    return vmd.decompose(signal, fs, method='hierarchical', **kwargs)


def ultra_fast_vmd(signal, fs, method='standard', **kwargs):
    """Backward compatibility wrapper for ultra_fast_vmd"""
    vmd = FastVMD()
    return vmd.decompose(signal, fs, method=method, **kwargs)


def print_hierarchical_summary(level_info):
    """Backward compatibility wrapper for print_hierarchical_summary"""
    HierarchicalVMD.print_summary(level_info)


def clear_memory_pool():
    """Global memory pool clearing function for backward compatibility"""
    # This now requires a FastVMD instance, but we'll create a temporary one
    temp_vmd = FastVMD()
    temp_vmd.clear_cache()


# ==============================================
# Test Script (Updated to use new interface)
# ==============================================
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    
    # Create test signal
    t = np.linspace(0, 8, 1500)
    fs = len(t)/(t[-1]-t[0])
    signal = (0.3*t +
              np.sin(2*np.pi*4*t) +
              0.6*np.sin(2*np.pi*15*t) +
              0.4*np.sin(2*np.pi*35*t) +
              0.05*np.random.normal(size=len(t)))
    
    print("🚀 Testing both Standard and Hierarchical VMD with new organized structure...")
    
    # Create VMD instance
    vmd = FastVMD()
    
    # Test standard VMD
    print("\n" + "="*50)
    print("🔧 STANDARD VMD")
    print("="*50)
    start_time = time.time()
    modes_std, freqs_std, params_std = vmd.decompose(
        signal, fs, method='standard',
        boundary_method='reflect',
        apply_tapering=False,
        auto_params=True
    )
    std_time = time.time() - start_time
    print(f"✅ Standard VMD completed in {std_time:.2f}s")
    
    # Test hierarchical VMD
    print("\n" + "="*50) 
    print("🏗️ HIERARCHICAL VMD")
    print("="*50)
    start_time = time.time()
    modes_hier, freqs_hier, level_info = vmd.decompose(
        signal, fs, method='hierarchical',
        max_levels=3,
        energy_threshold=0.02
    )
    hier_time = time.time() - start_time
    
    # Print detailed summary
    HierarchicalVMD.print_summary(level_info)
    
    print(f"\n⚡ PERFORMANCE COMPARISON:")
    print(f"   Standard VMD: {std_time:.2f}s ({len(modes_std)} modes)")
    print(f"   Hierarchical VMD: {hier_time:.2f}s ({len(modes_hier)} modes)")
    print(f"   Time ratio: {hier_time/std_time:.1f}x")
    
    # Compare reconstruction quality
    recon_std = np.sum(modes_std, axis=0)
    recon_hier = np.sum(modes_hier, axis=0)
    mse_std = np.mean((signal - recon_std)**2)
    mse_hier = np.mean((signal - recon_hier)**2)
    
    print(f"\n🎯 QUALITY COMPARISON:")
    print(f"   Standard MSE: {mse_std:.3e}")
    print(f"   Hierarchical MSE: {mse_hier:.3e}")
    print(f"   Quality ratio: {mse_hier/mse_std:.2f}x {'(better)' if mse_hier < mse_std else '(worse)'}")
    
    # Cleanup
    vmd.clear_cache()
    
    # Choose better result for plotting
    if mse_hier < mse_std:
        modes, freqs, method_used = modes_hier, freqs_hier, "Hierarchical"
        elapsed = hier_time
    else:
        modes, freqs, method_used = modes_std, freqs_std, "Standard" 
        elapsed = std_time
    
    print(f"\n📊 Using {method_used} VMD result for visualization")
    
    # Plotting
    total_energy = np.sum(signal**2)
    fig, axes = plt.subplots(len(modes)+2, 1, figsize=(14, 2.2*(len(modes)+2)))
    
    axes[0].plot(t, signal, 'b-', alpha=0.8)
    axes[0].set_title("Original Signal")
    
    for i, (m, f) in enumerate(zip(modes, freqs)):
        e_pct = 100*np.sum(m**2)/total_energy
        axes[i+1].plot(t, m, alpha=0.85)
        axes[i+1].set_title(f"Mode {i+1} | Dom freq ~{f:.2f} Hz | Energy {e_pct:.1f}%")
    
    recon = np.sum(modes, axis=0)
    axes[-1].plot(t, signal, 'b-', label="Original")
    axes[-1].plot(t, recon, 'r--', label="Reconstructed")
    mse = np.mean((signal - recon)**2)
    axes[-1].legend()
    
    if method_used == "Standard":
        axes[-1].set_title(f"Reconstruction MSE: {mse:.3e} | Best K={params_std[0]}, α={params_std[1]:.1f}")
    else:
        axes[-1].set_title(f"Reconstruction MSE: {mse:.3e} | Hierarchical VMD")
    
    plt.tight_layout()
    plt.show()
