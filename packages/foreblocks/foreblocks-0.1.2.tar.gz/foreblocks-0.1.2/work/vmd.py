# -*- coding: utf-8 -*-
"""
Fast Optuna-Optimized VMD with FFT caching - Refactored and Organized
"""
import os
import gc
import time
import pickle
import threading
import warnings
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

# === Numerical & Scientific ===
import numpy as np
import pyfftw
import pyfftw.interfaces.numpy_fft as fftw_np
from numba import njit, prange

# === Machine Learning / Optimization ===
from sklearn.cluster import DBSCAN
import optuna

# === Local Modules ===
from vmd_aux import *

# === Suppress Warnings ===
warnings.filterwarnings('ignore')
     
##################################################3

# Ultra-fast numba implementations
@njit(parallel=True, fastmath=True, cache=True, nogil=True)
def update_modes_ultra_fast(
    freqs, half_T, f_hat_plus, sum_uk, lambda_hat_n, Alpha, omega_n, u_hat_prev, K, tau
):
    """Ultra-optimized mode update with maximum vectorization"""
    T = len(freqs)
    freq_slice_start = half_T
    u_hat_plus_next = np.zeros((T, K), dtype=np.complex128)
    omega_next = np.empty(K)
    diff_norm = 0.0
    eps = 1e-14
    inv_T = 1.0 / T
    
    # Pre-compute lambda adjustment
    lambda_half = lambda_hat_n * 0.5
    
    for k in range(K):
        # Update sum_uk
        if k == 0:
            for i in prange(T):
                sum_uk[i] += u_hat_prev[i, K - 1] - u_hat_prev[i, 0]
        else:
            for i in prange(T):
                sum_uk[i] += u_hat_plus_next[i, k - 1] - u_hat_prev[i, k]
        
        omega_k = omega_n[k]
        alpha_k = Alpha[k]
        
        # Fused mode update and difference norm computation
        local_diff_norm = 0.0
        for i in prange(T):
            freq_diff = freqs[i] - omega_k
            denom = 1.0 + alpha_k * freq_diff * freq_diff + eps
            
            new_val = (f_hat_plus[i] - sum_uk[i] - lambda_half[i]) / denom
            u_hat_plus_next[i, k] = new_val
            
            diff = new_val - u_hat_prev[i, k]
            local_diff_norm += (diff.real * diff.real + diff.imag * diff.imag)
        
        diff_norm += local_diff_norm * inv_T
        
        # Fast omega update
        if freq_slice_start < T:
            numerator = 0.0
            denominator = 0.0
            
            for i in range(freq_slice_start, T):
                val = u_hat_plus_next[i, k]
                weight = val.real * val.real + val.imag * val.imag
                numerator += freqs[i] * weight
                denominator += weight
            
            omega_next[k] = numerator / denominator if denominator > eps else omega_k
        else:
            omega_next[k] = omega_k
    
    # Final lambda update
    mode_sum = np.sum(u_hat_plus_next, axis=1)
    lambda_next = lambda_hat_n + tau * (mode_sum - f_hat_plus)
    
    return u_hat_plus_next, omega_next, sum_uk, lambda_next, diff_norm

@njit(parallel=True, fastmath=True, cache=True)
def _ifft_reconstruction(u_hat_full, T, half_T, K):
    """Fast reconstruction with numba optimization"""
    # Fill conjugate symmetry
    for k in prange(K):
        for i in range(1, half_T):
            u_hat_full[i, k] = np.conj(u_hat_full[T - i, k])
        u_hat_full[0, k] = np.conj(u_hat_full[T - 1, k])
    
    return u_hat_full

@njit(fastmath=True, cache=True)
def spectral_peaks_init(spectrum, freqs, K):
    """Fast spectral initialization without sklearn dependency"""
    # Find top peaks
    n_peaks = min(len(spectrum), 10 * K)
    peak_indices = np.argpartition(spectrum, -n_peaks)[-n_peaks:]
    peak_freqs = freqs[peak_indices]
    peak_vals = spectrum[peak_indices]
    
    # Sort by magnitude
    sort_idx = np.argsort(peak_vals)[::-1]
    peak_freqs = peak_freqs[sort_idx]
    
    # Simple clustering: divide frequency range into K bins
    omega_init = np.zeros(K)
    freq_min, freq_max = np.min(peak_freqs), np.max(peak_freqs)
    
    if freq_max > freq_min:
        bin_size = (freq_max - freq_min) / K
        for k in range(K):
            bin_center = freq_min + (k + 0.5) * bin_size
            # Find closest peak to bin center
            distances = np.abs(peak_freqs - bin_center)
            closest_idx = np.argmin(distances)
            omega_init[k] = peak_freqs[closest_idx]
    else:
        # Fallback to uniform spacing
        omega_init = np.linspace(0.1, 0.4, K)
    
    return omega_init

class VMDCore:
    """
    Core VMD implementation with advanced optimizations:
    - Cached FFTW plans for repeated runs
    - Cached frequency grids per signal length
    - Reduced memory copies in FFT pipeline
    - Smarter initialization from spectral clusters
    - Adaptive convergence & early stopping
    - Ultra-fast numba kernels
    """

    def __init__(
        self,
        fftw_manager=None,
        boundary_handler=None,
        use_gpu: bool = True,
    ):
        self.fftw_manager = fftw_manager
        self.boundary_handler = boundary_handler

        # Caches
        self._fft_plan_cache = {}
        self._ifft_plan_cache = {}
        self._freq_cache = {}
        self._prev_omega_cache = {}  # warm start cache per signal length

        # GPU optional
        self.use_gpu = use_gpu
        self._xp = None
        if self.use_gpu:
            try:
                import cupy as cp
                self._xp = cp
                print("🚀 GPU acceleration enabled via CuPy")
            except ImportError:
                self._xp = np
                print("⚠️ CuPy not available, falling back to CPU")
        else:
            self._xp = np
        
        # Configure FFTW for maximum performance
        try:
            import multiprocessing
            pyfftw.config.NUM_THREADS = multiprocessing.cpu_count()
        except:
            pyfftw.config.NUM_THREADS = 4  # fallback
        
        try:
            pyfftw.interfaces.cache.enable()
        except:
            pass  # Cache may not be available in all versions

    # =====================================
    # FFT helpers with plan caching
    # =====================================
    def _get_fft_plan(self, length: int):
        """Get or build FFTW plan for a given signal length"""
        if length not in self._fft_plan_cache:
            input_array = pyfftw.empty_aligned(length, dtype='complex128')
            output_array = pyfftw.empty_aligned(length, dtype='complex128')
            
            # Get current thread count safely
            try:
                num_threads = pyfftw.config.NUM_THREADS
            except:
                num_threads = 1
            
            self._fft_plan_cache[length] = pyfftw.FFTW(
                input_array, output_array,
                direction='FFTW_FORWARD',
                flags=('FFTW_ESTIMATE',),
                threads=num_threads
            )
        return self._fft_plan_cache[length]
    
    def _get_ifft_plan(self, length: int):
        """Get or build FFTW IFFT plan for a given signal length"""
        if length not in self._ifft_plan_cache:
            input_array = pyfftw.empty_aligned(length, dtype='complex128')
            output_array = pyfftw.empty_aligned(length, dtype='complex128')
            
            # Get current thread count safely
            try:
                num_threads = pyfftw.config.NUM_THREADS
            except:
                num_threads = 1
            
            self._ifft_plan_cache[length] = pyfftw.FFTW(
                input_array, output_array,
                direction='FFTW_BACKWARD',
                flags=('FFTW_ESTIMATE',),
                threads=num_threads
            )
        return self._ifft_plan_cache[length]

    def _fft(self, x: np.ndarray) -> np.ndarray:
        """Planned FFT with fftshift using cached FFTW plans"""
        length = len(x)
        plan = self._get_fft_plan(length)
        
        # Copy input to plan's aligned input array
        plan.input_array[:] = x
        plan.execute()
        
        # Apply fftshift and return copy
        return np.fft.fftshift(plan.output_array.copy())
    
    def _ifft(self, x: np.ndarray, axis=0) -> np.ndarray:
        """Optimized IFFT using cached plans or numpy fallback for multi-dim"""
        if axis != 0 or x.ndim > 1:
            # Multi-dimensional case - use numpy
            return np.fft.ifft(np.fft.ifftshift(x, axes=axis), axis=axis)
        
        # 1D case - use cached FFTW plan
        length = len(x)
        plan = self._get_ifft_plan(length)
        
        # Apply ifftshift first
        shifted_x = np.fft.ifftshift(x)
        plan.input_array[:] = shifted_x
        plan.execute()
        
        return plan.output_array.copy() / length

    # =====================================
    # Precompute FFT with caching
    # =====================================
    def precompute_fft(
        self,
        signal: np.ndarray,
        boundary_method: str = "reflect",
        use_soft_junction: bool = False,
        window_alpha: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Precompute FFT and boundary handling for all trials (ultra-optimized)"""
        orig_len = len(signal)
        if orig_len % 2:  # enforce even length
            signal = signal[:-1]

        # Boundary extension
        if boundary_method != "none":
            if self.boundary_handler:
                ratio = self.boundary_handler.adaptive_extension_ratio(signal)
                fMirr, left_ext, right_ext = self.boundary_handler.extend_signal(
                    signal, method=boundary_method, extension_ratio=ratio
                )
            else:
                # Fast fallback boundary extension
                ext_len = len(signal) // 4
                if boundary_method == "reflect":
                    left_pad = signal[1:ext_len+1][::-1]
                    right_pad = signal[-(ext_len+1):-1][::-1]
                    fMirr = np.concatenate([left_pad, signal, right_pad])
                    left_ext = right_ext = ext_len
                else:
                    fMirr = signal
                    left_ext = right_ext = 0
        else:
            fMirr = signal
            left_ext = right_ext = 0

        # Optional smoothing
        if use_soft_junction and boundary_method != "none" and left_ext > 0:
            fMirr = self._smooth_edge_junction(fMirr, orig_len, left_ext)

        # Windowing
        if window_alpha is None:
            if self.boundary_handler:
                window_alpha = self.boundary_handler.auto_window_alpha(signal)
            else:
                window_alpha = 0.1 if boundary_method != "none" else 0.0
                
        if window_alpha > 0:
            # Fast Tukey window without scipy dependency
            N = len(fMirr)
            taper_len = int(window_alpha * N / 2)
            if taper_len > 0:
                window = np.ones(N)
                t = np.arange(taper_len)
                taper = 0.5 * (1 - np.cos(np.pi * t / taper_len))
                window[:taper_len] = taper
                window[-taper_len:] = taper[::-1]
                fMirr = fMirr * window

        # FFT
        T = len(fMirr)

        # Cache freq grid
        freqs = self._freq_cache.get(T)
        if freqs is None:
            freqs = np.fft.fftshift(np.fft.fftfreq(T))
            self._freq_cache[T] = freqs

        # Compute FFT (using cached FFTW plan)
        f_hat = self._fft(fMirr)
        # Zero out lower half directly (no extra copy)
        f_hat[: T // 2] = 0

        return {
            "f_hat_plus": f_hat,
            "freqs": freqs,
            "T": T,
            "half_T": T // 2,
            "orig_len": orig_len,
            "left_ext": left_ext,
            "right_ext": right_ext,
        }

    # =====================================
    # Smoothing
    # =====================================
    def _smooth_edge_junction(
        self,
        extended_signal: np.ndarray,
        original_len: int,
        ext_len: int,
        smooth_ratio: float = 0.02,
    ) -> np.ndarray:
        """Smooth junction between mirrored edges and original signal"""
        taper_len = max(2, int(original_len * smooth_ratio))
        ramp_up = 0.5 * (1 - np.cos(np.linspace(0, np.pi, taper_len)))
        ramp_down = ramp_up[::-1]

        # Apply smoothing
        extended_signal[ext_len - taper_len : ext_len] *= ramp_up
        end_idx = ext_len + original_len
        extended_signal[end_idx : end_idx + taper_len] *= ramp_down

        return extended_signal

    # =====================================
    # Smarter spectral initialization
    # =====================================
    def init_from_spectrum(self, signal: np.ndarray, K: int) -> np.ndarray:
        """Initialize omega from top-K FFT peaks spread across spectrum"""
        spec = np.abs(np.fft.rfft(signal))
        freqs = np.fft.rfftfreq(len(signal))
        
        # Use fast numba implementation
        return spectral_peaks_init(spec, freqs, K)

    # =====================================
    # Core Decomposition
    # =====================================
    def decompose(
        self,
        f: Optional[np.ndarray],
        alpha: float,
        tau: float,
        K: int,
        DC: int,
        init: int,
        tol: float,
        boundary_method: str = "reflect",
        max_iter: int = 300,
        precomputed_fft: Optional[Dict] = None,
        trial: Optional[Any] = None,
        warm_start: bool = True,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Core VMD decomposition algorithm (ultra-optimized)"""

        # === Precompute FFT if not provided ===
        if precomputed_fft is not None:
            f_hat_plus = precomputed_fft["f_hat_plus"]
            freqs = precomputed_fft["freqs"]
            T = precomputed_fft["T"]
            half_T = precomputed_fft["half_T"]
            orig_len = precomputed_fft["orig_len"]
            left_ext = precomputed_fft["left_ext"]
            right_ext = precomputed_fft["right_ext"]
        else:
            orig_len = len(f)
            if len(f) % 2:
                f = f[:-1]
            if boundary_method != "none":
                if self.boundary_handler:
                    fMirr, left_ext, right_ext = self.boundary_handler.extend_signal(
                        f, method=boundary_method, extension_ratio=0.3
                    )
                else:
                    # Fast fallback
                    ext_len = len(f) // 4
                    left_pad = f[1:ext_len+1][::-1]
                    right_pad = f[-(ext_len+1):-1][::-1]
                    fMirr = np.concatenate([left_pad, f, right_pad])
                    left_ext = right_ext = ext_len
            else:
                fMirr = f
                left_ext = right_ext = 0
            T = len(fMirr)
            freqs = self._freq_cache.get(T)
            if freqs is None:
                freqs = np.fft.fftshift(np.fft.fftfreq(T))
                self._freq_cache[T] = freqs
            f_hat = self._fft(fMirr)
            f_hat[: T // 2] = 0
            f_hat_plus = f_hat
            half_T = T // 2

        # === Initialize parameters ===
        Alpha = alpha * np.ones(K)
        omega_curr = np.zeros(K)

        # Warm start from previous same-length decomposition
        if warm_start and T in self._prev_omega_cache:
            cached_omega = self._prev_omega_cache[T]
            if len(cached_omega) == K:
                omega_curr = cached_omega.copy()
            else:
                # Smart interpolation for different K
                if len(cached_omega) > 0:
                    omega_curr = np.interp(
                        np.linspace(0, 1, K),
                        np.linspace(0, 1, len(cached_omega)),
                        cached_omega
                    )
        else:
            if init == 1:
                omega_curr = np.arange(K) * (0.5 / K)
            elif init == 2:
                fs = 1 / T
                omega_curr = np.sort(
                    np.exp(np.log(fs) + (np.log(0.5) - np.log(fs)) * np.random.rand(K))
                )
            elif init == 3:
                # Smarter spectrum-based initialization
                omega_curr = self.init_from_spectrum(f if f is not None else fMirr, K)

        if DC:
            omega_curr[0] = 0.0

        # === Initialize loop variables ===
        lambda_curr = np.zeros(len(freqs), dtype=np.complex128)
        sum_uk = np.zeros(len(freqs), dtype=np.complex128)
        u_hat_prev = np.zeros((len(freqs), K), dtype=np.complex128)
        uDiff = tol + 1.0

        # Adaptive stopping
        stagnation_count = 0
        prev_diff = float("inf")
        adaptive_tol = max(tol, 1e-7)

        # === Main Iteration ===
        for n in range(max_iter):
            u_hat_next, omega_next, sum_uk, lambda_next, diff_norm = (
                self._update_modes_numba(
                    freqs,
                    half_T,
                    f_hat_plus,
                    sum_uk,
                    lambda_curr,
                    Alpha,
                    omega_curr,
                    u_hat_prev,
                    K,
                    tau,
                )
            )

            if n > 5:
                uDiff = diff_norm

            # Early stagnation detection
            if n > 10:
                if abs(diff_norm - prev_diff) < adaptive_tol * 0.1:
                    stagnation_count += 1
                else:
                    stagnation_count = 0
                if stagnation_count >= 4:
                    break

            # Optuna pruning
            if trial is not None and n % 15 == 0:
                trial.report(uDiff, step=n)
                if trial.should_prune():
                    try:
                        import optuna
                        raise optuna.TrialPruned()
                    except ImportError:
                        pass

            # Update variables
            u_hat_prev = u_hat_next
            lambda_curr = lambda_next
            omega_curr = omega_next
            prev_diff = diff_norm

            # Final stopping
            if uDiff <= tol:
                break

        # Save warm start cache
        self._prev_omega_cache[T] = omega_curr.copy()

        # === Ultra-fast Reconstruction ===
        u_hat_full = np.zeros((T, K), dtype=np.complex128)
        u_hat_full[half_T:T, :] = u_hat_prev[half_T:T, :]
        
        # Fast conjugate symmetry using numba
        u_hat_full = _ifft_reconstruction(u_hat_full, T, half_T, K)

        # Inverse FFT - handle multi-dimensional case properly
        if K == 1:
            # Single mode - use 1D cached IFFT
            u_temp = np.real(self._ifft(u_hat_full[:, 0]))
            u = u_temp.reshape(1, -1)
        else:
            # Multiple modes - use numpy for 2D
            u_temp = np.real(np.fft.ifft(np.fft.ifftshift(u_hat_full, axes=0), axis=0))
            u = u_temp.T

        # Extract original portion
        if precomputed_fft is not None or boundary_method != "none":
            start_idx = left_ext
            end_idx = start_idx + orig_len
            if end_idx <= u.shape[1]:
                u = u[:, start_idx:end_idx]
            else:
                u = u[:, start_idx:]

        # Fast interpolation if needed
        if u.shape[1] != orig_len:
            if u.shape[1] > orig_len:
                # Simple downsampling
                step = u.shape[1] / orig_len
                indices = np.arange(0, u.shape[1], step).astype(int)[:orig_len]
                u = u[:, indices]
            else:
                # Linear interpolation
                x_old = np.linspace(0, 1, u.shape[1])
                x_new = np.linspace(0, 1, orig_len)
                u = np.array([np.interp(x_new, x_old, mode) for mode in u])

        return u, u_hat_full, omega_curr

    # =====================================
    # Numba core update (compatibility)
    # =====================================
    @staticmethod
    def _update_modes_numba(
        freqs,
        half_T,
        f_hat_plus,
        sum_uk,
        lambda_hat_n,
        Alpha,
        omega_n,
        u_hat_prev,
        K,
        tau,
    ):
        """Numba-optimized core update loop - now ultra-fast"""
        return update_modes_ultra_fast(
            freqs,
            half_T,
            f_hat_plus,
            sum_uk,
            lambda_hat_n,
            Alpha,
            omega_n,
            u_hat_prev,
            K,
            tau,
        )



@njit(fastmath=True, cache=True, parallel=True)
def _merge_modes_numba(modes_to_merge):
    """Ultra-fast mode merging using numba"""
    if len(modes_to_merge) == 0:
        return np.zeros(1)
    
    signal_len = len(modes_to_merge[0])
    merged = np.zeros(signal_len)
    
    for i in range(len(modes_to_merge)):
        for j in prange(signal_len):
            merged[j] += modes_to_merge[i][j]
    
    return merged

class ModeProcessor:
    """Ultra-optimized mode processing and analysis with numba acceleration"""
    
    @staticmethod
    def get_dominant_frequency(sig: np.ndarray, fs: float) -> float:
        """Get dominant frequency of a signal with ultra-fast implementation"""
        N = len(sig)
        if N < 4 or np.allclose(sig, 0, atol=1e-12):
            return 0.0
        
        # Use numpy for compatibility - works with both fftw_np and numpy
        try:
            # Try fftw first if available
            import fftw_np
            freqs = fftw_np.rfftfreq(N, d=1/fs)
            spec = np.abs(fftw_np.rfft(sig))
        except:
            # Fallback to numpy
            freqs = np.fft.rfftfreq(N, d=1/fs)
            spec = np.abs(np.fft.rfft(sig))
        
        spec[0] = 0  # Remove DC
        return freqs[np.argmax(spec)] if len(spec) > 0 else 0.0
    
    def cluster_modes_by_frequency(
        self, modes: List[np.ndarray], fs: float
    ) -> List[List[int]]:
        """
        Cluster mode indices by dominant frequency using optimized DBSCAN
        Returns list of clusters (each is a list of mode indices)
        """
        # Fast dominant frequency calculation
        dom_freqs = np.array([self.get_dominant_frequency(m, fs) for m in modes])
        
        if len(dom_freqs) <= 1:
            return [[0]]
        
        # Check for identical frequencies (optimization)
        if len(np.unique(dom_freqs)) == 1:
            return [list(range(len(modes)))]
        
        # Optimized clustering based on array size
        if len(modes) <= 8:
            # Fast simple clustering for small arrays
            freq_range = max(dom_freqs.max() - dom_freqs.min(), 1e-6)
            eps = 0.05 * freq_range
            
            sorted_indices = np.argsort(dom_freqs)
            sorted_freqs = dom_freqs[sorted_indices]
            
            clusters = []
            current_cluster = [sorted_indices[0]]
            
            for i in range(1, len(sorted_indices)):
                if sorted_freqs[i] - sorted_freqs[i-1] <= eps:
                    current_cluster.append(sorted_indices[i])
                else:
                    clusters.append(current_cluster)
                    current_cluster = [sorted_indices[i]]
            
            clusters.append(current_cluster)
            return clusters
        else:
            # Use DBSCAN for larger arrays
            freq_vals = dom_freqs.reshape(-1, 1)
            freq_range = max(dom_freqs.max() - dom_freqs.min(), 1e-6)
            eps = 0.05 * freq_range  # cluster resolution ~ 5% of spectrum
            
            clustering = DBSCAN(eps=eps, min_samples=1, algorithm='ball_tree').fit(freq_vals)
            labels = clustering.labels_
            
            clusters = []
            for lbl in np.unique(labels):
                clusters.append(list(np.where(labels == lbl)[0]))
            
            return clusters
    
    def merge_similar_modes(
        self, modes: List[np.ndarray], fs: float
    ) -> List[np.ndarray]:
        """
        Automatically merge modes clustered by similar dominant frequencies
        """
        if len(modes) <= 1:
            return modes
        
        # Cluster modes adaptively
        clusters = self.cluster_modes_by_frequency(modes, fs)
        
        if len(clusters) == len(modes):
            # No merging needed
            return modes
        
        merged_modes = []
        for cluster_indices in clusters:
            grouped_modes = [modes[i] for i in cluster_indices]
            
            # Use numba for larger merging operations, numpy for small
            if len(grouped_modes) > 3 and len(grouped_modes[0]) > 100:
                try:
                    merged_mode = _merge_modes_numba(np.array(grouped_modes))
                except:
                    # Fallback to numpy
                    merged_mode = np.sum(grouped_modes, axis=0)
            else:
                merged_mode = np.sum(grouped_modes, axis=0)  # merge by summation
            
            merged_modes.append(merged_mode)
        
        if len(merged_modes) < len(modes):
            print(f"🔗 Merged {len(modes)} → {len(merged_modes)} modes (freq clustering)")
        
        return merged_modes
    
    def sort_modes_by_frequency(
        self, modes: List[np.ndarray], fs: float, low_to_high: bool = True
    ) -> Tuple[List[np.ndarray], List[float]]:
        """Sort modes by their dominant frequencies"""
        if len(modes) <= 1:
            if modes:
                freq = self.get_dominant_frequency(modes[0], fs)
                return modes, [freq]
            else:
                return [], []
        
        # Fast dominant frequency calculation
        dom_freqs = [self.get_dominant_frequency(m, fs) for m in modes]
        
        # Fast sorting
        order = np.argsort(dom_freqs)
        if not low_to_high:
            order = order[::-1]
        
        sorted_modes = [modes[i] for i in order]
        sorted_freqs = [dom_freqs[i] for i in order]
        
        return sorted_modes, sorted_freqs
    
class HierarchicalVMD:
    """
    Ultra-optimized Hybrid Hierarchical VMD:
    - Level 1: Full Optuna optimization (global)
    - Level 2: Quick residual cleanup with fixed K/α (no Optuna)
    - Level 3: Optional tiny cleanup
    - Aggressive early stopping and caching
    """
    
    def __init__(self, vmd_optimizer):
        self.vmd_optimizer = vmd_optimizer
        self.mode_processor = ModeProcessor()
        
        # Performance caches
        self._residual_cache = {}
        self._energy_cache = {}
    
    def decompose(self, signal: np.ndarray, fs: float, params) -> Tuple[np.ndarray, List[float], List[Dict]]:
        """Ultra-fast hierarchical decomposition with intelligent early stopping"""
        print(f"🚀 Starting Ultra-Fast Hierarchical VMD (max_levels={params.max_levels})...")
        
        all_modes = []
        level_info = []
        original_energy = np.sum(signal**2)
        current_residual = signal.copy()
        
        # === LEVEL 1: Full Optuna (global decomposition) ===
        print("\n📊 Level 1: Full Optuna optimization")
        start_time = time.time()
        
        modes_lvl1, freqs_lvl1, best_params_lvl1 = self.vmd_optimizer.optimize(
            signal,
            fs,
            n_trials=max(15, params.max_levels * 8),  # Reduced trials
            boundary_method="reflect",
            auto_params=True,
            apply_tapering=False,
        )
        
        lvl1_time = time.time() - start_time
        
        # Fast energy calculation
        recon_lvl1 = np.sum(modes_lvl1, axis=0)
        current_residual = signal - recon_lvl1
        residual_energy = np.sum(current_residual**2)
        residual_ratio = residual_energy / original_energy
        delta_energy = original_energy - residual_energy
        
        all_modes.extend(modes_lvl1)
        level_info.append({
            "level": 1,
            "n_modes": len(modes_lvl1),
            "energy_reduced": delta_energy / original_energy,
            "residual_ratio": residual_ratio,
            "computation_time": lvl1_time,
            "bands": [(0, fs / 2)],
        })
        
        print(f" ✅ Level 1: {len(modes_lvl1)} modes in {lvl1_time:.2f}s")
        print(f" 📉 Residual: {residual_ratio:.1%} (ΔE={delta_energy/original_energy:.1%})")
        
        # Aggressive early stopping
        if residual_ratio < 0.25:  # Even more aggressive threshold
            print("⚡ Residual below 25% after Level 1 → stopping early!")
            return self._finalize_modes(all_modes, fs, level_info)
        
        # === LEVEL 2: Quick residual cleanup (no Optuna) ===
        if params.max_levels >= 2:
            print("\n📊 Level 2: Ultra-fast residual cleanup")
            K_lvl1, alpha_lvl1, _ = best_params_lvl1
            
            # Optimized parameters for residual cleanup
            quick_K = min(3, max(2, K_lvl1 // 2 + 1))
            quick_alpha = max(300, alpha_lvl1 * 0.3)  # Even tighter bandwidth
            
            start_time = time.time()
            
            modes_lvl2, _, _ = self.vmd_optimizer.vmd_core.decompose(
                current_residual,
                alpha=quick_alpha,
                tau=0.0,
                K=quick_K,
                DC=0,
                init=1,
                tol=1e-5,  # Relaxed tolerance for speed
                boundary_method="mirror",
                max_iter=150,  # Reduced iterations
            )
            
            lvl2_time = time.time() - start_time
            
            # Energy accounting
            recon_lvl2 = np.sum(modes_lvl2, axis=0)
            prev_residual_energy = residual_energy
            current_residual = current_residual - recon_lvl2
            residual_energy = np.sum(current_residual**2)
            residual_ratio = residual_energy / original_energy
            delta_energy2 = prev_residual_energy - residual_energy
            
            all_modes.extend(modes_lvl2)
            level_info.append({
                "level": 2,
                "n_modes": len(modes_lvl2),
                "energy_reduced": delta_energy2 / original_energy,
                "residual_ratio": residual_ratio,
                "computation_time": lvl2_time,
                "bands": [(0, fs / 2)],
            })
            
            print(f" ✅ Level 2: {len(modes_lvl2)} modes in {lvl2_time:.2f}s")
            print(f" 📉 Residual: {residual_ratio:.1%} (ΔE={delta_energy2/original_energy:.1%})")
            
            # Early stopping after level 2
            if residual_ratio < 0.4:  # More aggressive
                print("⚡ Residual acceptable after Level 2 → stopping")
                return self._finalize_modes(all_modes, fs, level_info)
        
        # === LEVEL 3: Micro cleanup (optional) ===
        if params.max_levels >= 3 and residual_ratio > 0.4:
            print("\n📊 Level 3: Micro final cleanup")
            start_time = time.time()
            
            modes_lvl3, _, _ = self.vmd_optimizer.vmd_core.decompose(
                current_residual,
                alpha=quick_alpha * 0.5,
                tau=0.0,
                K=2,  # Minimal modes
                DC=0,
                init=1,
                tol=1e-4,  # Relaxed tolerance
                boundary_method="mirror",
                max_iter=100,  # Very limited iterations
            )
            
            lvl3_time = time.time() - start_time
            
            # Final energy accounting
            recon_lvl3 = np.sum(modes_lvl3, axis=0)
            prev_residual_energy = residual_energy
            current_residual = current_residual - recon_lvl3
            residual_energy = np.sum(current_residual**2)
            residual_ratio = residual_energy / original_energy
            delta_energy3 = prev_residual_energy - residual_energy
            
            all_modes.extend(modes_lvl3)
            level_info.append({
                "level": 3,
                "n_modes": len(modes_lvl3),
                "energy_reduced": delta_energy3 / original_energy,
                "residual_ratio": residual_ratio,
                "computation_time": lvl3_time,
                "bands": [(0, fs / 2)],
            })
            
            print(f" ✅ Level 3: {len(modes_lvl3)} modes in {lvl3_time:.2f}s")
            print(f" 📉 Final residual: {residual_ratio:.1%} (ΔE={delta_energy3/original_energy:.1%})")
        
        return self._finalize_modes(all_modes, fs, level_info)
    
    def _finalize_modes(self, all_modes: List[np.ndarray], fs: float, level_info: List[Dict]) -> Tuple[np.ndarray, List[float], List[Dict]]:
        """Ultra-fast mode finalization with optimized processing"""
        print(f"\n🎯 Finalizing {len(all_modes)} modes...")
        
        # Ultra-fast merging and sorting
        start_time = time.time()
        
        merged_modes = self.mode_processor.merge_similar_modes(all_modes, fs)
        sorted_modes, sorted_freqs = self.mode_processor.sort_modes_by_frequency(
            merged_modes, fs, low_to_high=True
        )
        
        finalize_time = time.time() - start_time
        print(f"⚡ Finalization completed in {finalize_time:.3f}s")
        
        return np.array(sorted_modes), sorted_freqs, level_info
    
    @staticmethod
    def print_summary(level_info: List[Dict]):
        """Ultra-fast summary printing with enhanced metrics"""
        print("\n" + "=" * 60)
        print("🚀 ULTRA-FAST HIERARCHICAL VMD SUMMARY")
        print("=" * 60)
        
        if not level_info:
            print("⚠️ No levels processed.")
            return
        
        # Fast summary calculations
        total_modes = sum(info["n_modes"] for info in level_info)
        total_time = sum(info["computation_time"] for info in level_info)
        total_energy_reduced = sum(info["energy_reduced"] for info in level_info)
        final_residual = level_info[-1]["residual_ratio"]
        
        print(f"📊 Performance Metrics:")
        print(f" • Levels processed: {len(level_info)}")
        print(f" • Total modes found: {total_modes}")
        print(f" • Energy captured: {total_energy_reduced:.1%}")
        print(f" • Final residual: {final_residual:.1%}")
        print(f" • Total time: {total_time:.2f}s")
        print(f" • Speed: {total_modes/total_time:.1f} modes/sec")
        
        print(f"\n📋 Level Details:")
        for info in level_info:
            efficiency = info["n_modes"] / info["computation_time"]
            print(f" Level {info['level']}: {info['n_modes']} modes, "
                  f"{info['energy_reduced']:.1%} energy, "
                  f"{info['computation_time']:.2f}s "
                  f"({efficiency:.1f} modes/s)")
        
        print("=" * 60)
        

@njit(fastmath=True, cache=True, parallel=True)
def _cost_calculation(modes, signal, fs):
    """Ultra-fast cost calculation using numba"""
    if len(modes) == 0:
        return 10.0
    
    # Spectral separation cost
    separation_cost = 0.0
    reconstruction_error = 0.0
    
    # Reconstruction error
    reconstructed = np.zeros_like(signal)
    for i in prange(len(modes)):
        for j in range(len(signal)):
            reconstructed[j] += modes[i][j]
    
    for j in prange(len(signal)):
        diff = signal[j] - reconstructed[j]
        reconstruction_error += diff * diff
    
    reconstruction_error = np.sqrt(reconstruction_error) / np.sqrt(np.sum(signal**2))
    
    # Mode correlation penalty (simplified)
    correlation_penalty = 0.0
    if len(modes) > 1:
        for i in range(len(modes)):
            for j in range(i + 1, len(modes)):
                corr = 0.0
                norm_i = 0.0
                norm_j = 0.0
                for k in range(len(signal)):
                    corr += modes[i][k] * modes[j][k]
                    norm_i += modes[i][k] * modes[i][k]
                    norm_j += modes[j][k] * modes[j][k]
                
                if norm_i > 0 and norm_j > 0:
                    corr = abs(corr) / (np.sqrt(norm_i * norm_j))
                    correlation_penalty += corr
    
    # Complexity penalty
    complexity_penalty = len(modes) * 0.1
    
    return reconstruction_error + correlation_penalty * 0.5 + complexity_penalty

class VMDOptimizer:
    """Ultra-optimized VMD optimizer with aggressive caching and parallel processing"""
    
    def __init__(self, fftw_manager):
        self.fftw_manager = fftw_manager
        self.vmd_core = VMDCore(fftw_manager, BoundaryHandler())
        self.mode_processor = ModeProcessor()
        self.signal_analyzer = SignalAnalyzer()
        
        # Enhanced caching system
        self._mode_cache = {}  # Cache decomposed modes
        self._cost_cache = {}  # Cache computed costs
        self._fft_cache = {}   # Cache FFT results
        
        # Performance tracking
        self._cache_hits = 0
        self._cache_misses = 0
        
    def _get_cache_key(self, K: int, alpha: float, signal_hash: int) -> str:
        """Generate cache key with signal dependency"""
        # Round alpha to reduce cache size while maintaining accuracy
        rounded_alpha = round(alpha, -int(np.log10(alpha)) + 2)  # 2 significant digits
        return f"{signal_hash}_{K}_{rounded_alpha}"
    
    def _objective(
        self,
        trial,
        signal: np.ndarray,
        fs: float,
        precomputed_fft: Dict,
        complexity_params,
        signal_hash: int,
    ) -> float:
        """Ultra-fast objective function with aggressive caching"""
        K = trial.suggest_int("K", 2, complexity_params.max_K)
        alpha = trial.suggest_float(
            "alpha", complexity_params.alpha_min, complexity_params.alpha_max, log=True
        )
        
        # Enhanced cache key with signal hash
        cache_key = self._get_cache_key(K, alpha, signal_hash)
        
        # Check cost cache first (fastest)
        if cache_key in self._cost_cache:
            self._cache_hits += 1
            return self._cost_cache[cache_key]
        
        # Check mode cache
        if cache_key in self._mode_cache:
            modes = self._mode_cache[cache_key]
            self._cache_hits += 1
        else:
            # Perform decomposition
            self._cache_misses += 1
            try:
                modes, _, _ = self.vmd_core.decompose(
                    None,
                    alpha=alpha,
                    tau=complexity_params.tau,
                    K=K,
                    DC=complexity_params.DC,
                    init=complexity_params.init,
                    tol=complexity_params.tol,
                    precomputed_fft=precomputed_fft,
                    trial=trial,
                )
                
                # Fast energy filtering
                total_energy = np.sum(signal**2)
                valid_modes = []
                for i, mode in enumerate(modes):
                    if np.sum(mode**2) / total_energy > 0.01:
                        valid_modes.append(mode)
                modes = valid_modes
                
                # Cache management - keep only most recent entries
                if len(self._mode_cache) >= 50:
                    # Remove oldest 20% of entries
                    keys_to_remove = list(self._mode_cache.keys())[:10]
                    for key in keys_to_remove:
                        del self._mode_cache[key]
                        if key in self._cost_cache:
                            del self._cost_cache[key]
                
                self._mode_cache[cache_key] = modes
                
            except optuna.TrialPruned:
                raise
            except Exception as e:
                # Cache failure result
                self._cost_cache[cache_key] = 10.0
                return 10.0
        
        if len(modes) == 0:
            cost = 10.0
        else:
            # Ultra-fast cost calculation
            cost = _cost_calculation(
                np.array(modes), signal, fs
            )
        
        # Cache the cost
        self._cost_cache[cache_key] = cost
        return cost
    
    def optimize(
        self,
        signal: np.ndarray,
        fs: float,
        n_trials: Optional[int] = None,
        tau: float = 0.0,
        DC: int = 0,
        init: int = 1,
        tol: Optional[float] = None,
        boundary_method: str = "reflect",
        apply_tapering: bool = True,
        auto_params: bool = True,
    ) -> Tuple[np.ndarray, List[float], Tuple[int, float, float]]:
        """Ultra-fast VMD optimization with intelligent caching and search space reduction"""
        
        # Clear caches and reset counters
        self._mode_cache.clear()
        self._cost_cache.clear()
        self._cache_hits = 0
        self._cache_misses = 0
        
        # Generate signal hash for cache consistency
        signal_hash = hash(tuple(signal[:min(100, len(signal))].tobytes()))
        
        print(f"🚀 Starting ultra-fast VMD optimization...")
        start_time = time.time()
        
        # === STEP 1: Complexity-aware spectral analysis ===
        if auto_params:
            complexity_params = self.signal_analyzer.assess_complexity(signal, fs)
            suggested_K = complexity_params.max_K
            alpha_min = complexity_params.alpha_min
            alpha_max = complexity_params.alpha_max
            
            # Intelligent trial count reduction
            if n_trials is None:
                base_trials = complexity_params.n_trials
                # Reduce trials for simple signals or long signals
                if len(signal) > 2000:
                    base_trials = max(8, base_trials // 3)
                elif complexity_params.max_K <= 4:
                    base_trials = max(10, base_trials // 2)
                n_trials = base_trials
                
            if tol is None:
                tol = complexity_params.tol
            
            # Aggressive search space narrowing
            K_low = max(2, suggested_K - 1)
            K_high = min(8, suggested_K + 1)
            
            print(f"🎯 Smart search space: K∈[{K_low}, {K_high}], α∈[{alpha_min:.0f}, {alpha_max:.0f}], trials={n_trials}")
        else:
            # Conservative defaults
            suggested_K = 6
            alpha_min, alpha_max = 500, 5000
            K_low, K_high = 2, 8
            if n_trials is None:
                n_trials = 20  # Reduced default
            if tol is None:
                tol = 1e-6
            
            complexity_params = VMDParameters(
                n_trials=n_trials,
                max_K=K_high,
                tol=tol,
                alpha_min=alpha_min,
                alpha_max=alpha_max,
            )
        
        # Inject parameters
        complexity_params.tau = tau
        complexity_params.DC = DC
        complexity_params.init = init
        complexity_params.tol = tol
        
        # === STEP 2: Ultra-fast FFT precomputation ===
        print("⚡ Precomputing FFT...")
        precomputed_fft = self.vmd_core.precompute_fft(signal, boundary_method)
        
        # === STEP 3: Optimized Optuna setup ===
        pruner = optuna.pruners.MedianPruner(
            n_warmup_steps=max(1, n_trials // 10),
            n_startup_trials=min(3, n_trials // 4),
        )
        sampler = optuna.samplers.TPESampler(
            n_startup_trials=min(3, n_trials // 4),
            multivariate=True,  # Better parameter correlation
        )
        
        study = optuna.create_study(
            direction="minimize", 
            pruner=pruner, 
            sampler=sampler
        )
        
        # === STEP 4: Ultra-fast optimization ===
        def objective_wrapper(trial):
            return self._objective(
                trial, signal, fs, precomputed_fft, complexity_params, signal_hash
            )
        
        print(f"🔥 Running {n_trials} trials with ultra-fast objective...")
        study.optimize(
            objective_wrapper,
            n_trials=n_trials,
            show_progress_bar=True,
            n_jobs=1,  # Single job for better cache efficiency
        )
        
        # === STEP 5: Results ===
        best_K = int(study.best_params["K"])
        best_alpha = study.best_params["alpha"]
        best_cost = study.best_value
        
        cache_hit_rate = self._cache_hits / (self._cache_hits + self._cache_misses) * 100
        optimization_time = time.time() - start_time
        
        print(f"✅ Optimal: K={best_K}, α={best_alpha:.0f}, cost={best_cost:.4f}")
        print(f"📈 Cache hit rate: {cache_hit_rate:.1f}%, Time: {optimization_time:.2f}s")
        
        # === STEP 6: Final decomposition ===
        print("🏁 Final decomposition...")
        final_cache_key = self._get_cache_key(best_K, best_alpha, signal_hash)
        
        if final_cache_key in self._mode_cache:
            best_modes = self._mode_cache[final_cache_key]
            print("⚡ Used cached final result!")
        else:
            best_modes, _, _ = self.vmd_core.decompose(
                None,
                alpha=best_alpha,
                tau=tau,
                K=best_K,
                DC=DC,
                init=init,
                tol=tol,
                precomputed_fft=precomputed_fft,
            )
            
            # Energy filtering
            total_energy = np.sum(signal**2)
            best_modes = [m for m in best_modes if np.sum(m**2) / total_energy > 0.01]
        
        # === STEP 7: Post-processing ===
        merged_modes = self.mode_processor.merge_similar_modes(best_modes, fs)
        sorted_modes, sorted_freqs = self.mode_processor.sort_modes_by_frequency(
            merged_modes, fs, low_to_high=True
        )
        
        if apply_tapering:
            taper_len = min(100, len(signal) // 10)
            sorted_modes = BoundaryHandler.taper_boundaries(sorted_modes, taper_len)
        
        self.fftw_manager.save_wisdom()
        
        total_time = time.time() - start_time
        print(f"🎉 Total optimization time: {total_time:.2f}s")
        
        return np.array(sorted_modes), sorted_freqs, (best_K, best_alpha, best_cost)

class FastVMD:
    """Main FastVMD class - unified interface for all VMD methods"""

    def __init__(self, wisdom_file: str = "vmd_fftw_wisdom.dat"):
        self.fftw_manager = FFTWManager(wisdom_file)
        self.vmd_optimizer = VMDOptimizer(self.fftw_manager)
        self.hierarchical_vmd = HierarchicalVMD(self.vmd_optimizer)

    def decompose(
        self, signal: np.ndarray, fs: float, method: str = "standard", **kwargs
    ) -> Tuple[np.ndarray, List[float], Any]:
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
        if method == "hierarchical":
            # Parse hierarchical parameters
            hierarchical_params = HierarchicalParameters(
                max_levels=kwargs.get("max_levels", 3),
                energy_threshold=kwargs.get("energy_threshold", 0.01),
                min_samples_per_level=kwargs.get("min_samples_per_level", 100),
                use_anti_aliasing=kwargs.get("use_anti_aliasing", True),
            )
            return self.hierarchical_vmd.decompose(signal, fs, hierarchical_params)
        else:
            # Standard VMD
            return self.vmd_optimizer.optimize(signal, fs, **kwargs)

    def clear_cache(self):
        """Clear all caches and memory pools"""
        #self.memory_manager.clear_pool()
        #self.vmd_optimizer._cache.clear()

    def __del__(self):
        """Cleanup on destruction"""
        self.clear_cache()

##############

import numpy as np
from numba import njit, prange
from typing import Dict, List, Tuple, Optional, Any
import time
from scipy.special import digamma, gammaln
from scipy.stats import gamma, invgamma
import matplotlib.pyplot as plt
from dataclasses import dataclass

###############################################################
# === Variational Bayesian VMD Integration (Hz-consistent) ===
###############################################################
import numpy as np
from numba import njit, prange
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
import time
import numpy as np
import time
from dataclasses import dataclass
from typing import List, Tuple, Dict
from numba import njit, prange
import numpy as np
from numba import njit, prange
from typing import List, Tuple, Dict
from dataclasses import dataclass
import time
from dataclasses import dataclass
import numpy as np
from numba import njit, prange

# === PRIOR STRUCTURES ===

@dataclass
class GaussianPrior:
    mu: float
    sigma: float

@dataclass
class VBPosterior:
    omega_mu: np.ndarray      # mean frequency in Hz
    omega_sigma: np.ndarray   # std dev of ω in Hz
    alpha_mu: np.ndarray      # log-normal mean
    alpha_sigma: np.ndarray   # log-normal std

@dataclass
class ELBOComponents:
    data_likelihood: float
    mode_regularization: float
    kl_omega: float
    kl_alpha: float
    total_elbo: float


# === CORE MATH UTILITIES ===

@njit(fastmath=True, cache=True)
def kl_gaussian(mu_q, sigma_q, mu_p, sigma_p):
    """KL between two Gaussians"""
    return np.log(sigma_p / sigma_q + 1e-12) + \
           (sigma_q**2 + (mu_q - mu_p)**2) / (2 * sigma_p**2) - 0.5

@njit(fastmath=True, cache=True)
def kl_lognormal(mu_q, sigma_q, mu_p, sigma_p):
    """KL between log-normals derived from Gaussians"""
    return kl_gaussian(mu_q, sigma_q, mu_p, sigma_p)

@njit(fastmath=True, cache=True)
def compute_reconstruction_likelihood(signal, modes, noise_precision):
    """Vectorized likelihood under Gaussian noise"""
    residual = signal - np.sum(modes, axis=0)
    residual_sq = np.sum(residual**2)
    N = signal.shape[0]
    return (
        -0.5 * N * np.log(2*np.pi)
        + 0.5 * N * np.log(noise_precision + 1e-12)
        - 0.5 * noise_precision * residual_sq
    )
@njit(fastmath=True, cache=True, parallel=True)
def compute_mode_regularization_term_fft(modes_fft_real, modes_fft_imag,
                                         omega_mu, alpha_mu, alpha_sigma,
                                         freqs_rad):
    """
    Proper E[log p(u|ω,α)] term in frequency domain.
    
    - freqs_rad must be in rad/s
    - FFT energies normalized by N
    - Corrected log-determinant sign
    """
    K, N = modes_fft_real.shape
    total = 0.0
    
    inv_N = 1.0 / N  # FFT normalization
    
    for k in prange(K):
        # E[α_k] for log-normal distribution
        exp_alpha = np.exp(alpha_mu[k] + 0.5 * alpha_sigma[k]**2)
        omega_k_rad = 2 * np.pi * omega_mu[k]  # still using rad/s for consistency
        
        mode_total = 0.0
        for f in range(N):
            freq_diff = freqs_rad[f] - omega_k_rad
            energy = (modes_fft_real[k, f]**2 + modes_fft_imag[k, f]**2) * inv_N
            
            # Spectral concentration term
            mode_total += -0.5 * exp_alpha * (freq_diff**2) * energy
        
        # log-determinant term (should penalize complexity)
        mode_total -= 0.5 * (alpha_mu[k] + 0.5 * alpha_sigma[k]**2)
        
        total += mode_total
    
    return total


# === ELBO COMPUTATION ===
def compute_true_elbo(signal, modes, vb_post: VBPosterior, fs: float,
                      noise_precision: float,
                      prior_omega: GaussianPrior,
                      prior_alpha: GaussianPrior) -> ELBOComponents:
    N = signal.shape[0]
    
    # Use rad/s for frequency grid to match regularization term
    freqs_rad = 2 * np.pi * np.fft.fftfreq(N, d=1/fs)
    fft_modes = np.fft.fft(modes, axis=1)
    
    reg_term = compute_mode_regularization_term_fft(
        fft_modes.real, fft_modes.imag,
        vb_post.omega_mu,
        vb_post.alpha_mu,
        vb_post.alpha_sigma,
        freqs_rad
    )
    
    likelihood = compute_reconstruction_likelihood(signal, modes, noise_precision)
    
    kl_omega = np.sum([
        kl_gaussian(vb_post.omega_mu[k], vb_post.omega_sigma[k],
                    prior_omega.mu, prior_omega.sigma)
        for k in range(len(vb_post.omega_mu))
    ])
    
    kl_alpha = np.sum([
        kl_lognormal(vb_post.alpha_mu[k], vb_post.alpha_sigma[k],
                     prior_alpha.mu, prior_alpha.sigma)
        for k in range(len(vb_post.alpha_mu))
    ])
    
    total = likelihood + reg_term - kl_omega - kl_alpha
    
    return ELBOComponents(
        data_likelihood=likelihood,
        mode_regularization=reg_term,
        kl_omega=kl_omega,
        kl_alpha=kl_alpha,
        total_elbo=total
    )


@njit(fastmath=True, cache=True)
def fast_bayesian_update_omega(freqs_hz, u_real, u_imag,
                               mu_prior, sigma_prior, sigma_noise,
                               damping=0.1):
    spec = u_real**2 + u_imag**2
    peak_idx = np.argmax(spec)
    f_peak = freqs_hz[peak_idx]
    
    prec_prior = 1.0 / (sigma_prior**2)
    prec_lik = (1.0 / (sigma_noise**2)) * damping  # damp likelihood influence
    prec_post = prec_prior + prec_lik
    
    mu_post = (mu_prior * prec_prior + f_peak * prec_lik) / prec_post
    sigma_post = np.sqrt(1.0 / prec_post)
    
    return abs(mu_post), sigma_post

@njit(fastmath=True, cache=True)
def fast_bayesian_update_alpha(u_real, u_imag, mu_prior, sigma_prior):
    N = u_real.shape[0]
    log_energy_sum = 0.0
    log_energy_sq_sum = 0.0
    
    for i in range(N):
        e = u_real[i]**2 + u_imag[i]**2
        # Clip to avoid log(0) and huge spikes
        e = max(e, 1e-12)
        le = np.log1p(e)  # log(1+energy)
        log_energy_sum += le
        log_energy_sq_sum += le**2
    
    mean_log = log_energy_sum / N
    var_log = log_energy_sq_sum / N - mean_log**2
    
    mu_post = 0.5 * (mu_prior + mean_log)
    sigma_post = np.sqrt(sigma_prior**2 + var_log)
    
    return mu_post, sigma_post


@njit(fastmath=True, cache=True)
def fast_exp_alpha_computation(mu, sigma):
    K = mu.shape[0]
    result = np.empty(K)
    for i in range(K):
        result[i] = np.exp(mu[i] + 0.5 * sigma[i]**2)
    return result

from scipy.special import digamma  # for ψ(a) when needed

@dataclass
class GammaPrior:
    a: float  # shape
    b: float  # rate

def vb_update_omega_full(freqs, U_real, U_imag, alpha_exp, mu_prior, sigma_prior):
    # Compute spectral moments
    energy = U_real**2 + U_imag**2
    
    sum_energy = np.sum(energy)
    sum_f_energy = np.sum(freqs * energy)
    sum_f2_energy = np.sum(freqs**2 * energy)
    
    # Likelihood quadratic terms
    A = alpha_exp * sum_energy
    B = alpha_exp * sum_f_energy
    
    # Likelihood mean & variance
    if A < 1e-12:  # Avoid div by zero
        mu_lik = mu_prior
        sigma_lik2 = 1e6
    else:
        mu_lik = B / A
        sigma_lik2 = 1.0 / A
    
    # Combine with Gaussian prior
    prec_prior = 1.0 / (sigma_prior**2)
    prec_lik = 1.0 / sigma_lik2
    prec_post = prec_prior + prec_lik
    
    mu_post = (mu_prior * prec_prior + mu_lik * prec_lik) / prec_post
    sigma_post = np.sqrt(1.0 / prec_post)
    return mu_post, sigma_post

def vb_update_alpha_full(freqs, U_real, U_imag, omega_k, mu_prior, sigma_prior):
    # Compute Γ_k = 0.5 ∑ (f-ω)^2 |U|^2
    energy = U_real**2 + U_imag**2
    freq_diff2 = (freqs - omega_k)**2
    Gamma_k = 0.5 * np.sum(freq_diff2 * energy)
    
    # Prior precision in log-space
    prior_prec = 1.0 / (sigma_prior**2)
    
    # Approx MAP update (log-domain)
    # log α_MAP ≈ μ0 - σ0^2 - log(Γ_k)
    log_alpha_map = mu_prior - sigma_prior**2 - np.log(Gamma_k + 1e-12)
    
    mu_post = 0.5 * (mu_prior + log_alpha_map)
    sigma_post = sigma_prior  # keep same, or shrink slightly
    
    return mu_post, sigma_post

# ==============================
# === ENHANCED VBVMDCore =====
# ==============================
class VBVMDCore:
    def __init__(self,
                 vmd_core,
                 mu_omega_prior_hz: float = 0.0,
                 sigma_omega_prior_hz: float = 50.0,
                 mu_alpha_prior: float = 5.0,
                 sigma_alpha_prior: float = 1.0,
                 noise_precision: float = 100.0,
                 estimate_noise: bool = True,
                 bayesian_noise: bool = True,
                 noise_prior_shape: float = 1e-3,
                 noise_prior_rate: float = 1e-3):

        self.vmd_core = vmd_core
        self.mu_omega_prior_hz = mu_omega_prior_hz
        self.sigma_omega_prior_hz = sigma_omega_prior_hz
        self.mu_alpha_prior = mu_alpha_prior
        self.sigma_alpha_prior = sigma_alpha_prior
        self.noise_precision = noise_precision
        self.estimate_noise = estimate_noise
        self.bayesian_noise = bayesian_noise

        # Gamma prior for noise precision
        self.noise_prior = GammaPrior(noise_prior_shape, noise_prior_rate)
        self.noise_post_a = noise_prior_shape
        self.noise_post_b = noise_prior_rate

        # Cache & tracking
        self._freq_cache = {}
        self._elbo_history = []
        self._elbo_components_history = []



    def _update_noise_gamma_posterior(self, signal: np.ndarray, modes: np.ndarray):
        """Update Gamma posterior for β using conjugacy"""
        residual = signal - np.sum(modes, axis=0)
        rss = np.sum(residual**2)
        N = len(signal)
        # Posterior parameters
        self.noise_post_a = self.noise_prior.a + N/2.0
        self.noise_post_b = self.noise_prior.b + 0.5 * rss
        return self.noise_post_a / self.noise_post_b  # E[β]

    def _expected_log_beta(self):
        return digamma(self.noise_post_a) - np.log(self.noise_post_b)


    def _estimate_noise_precision(self, signal: np.ndarray, modes: np.ndarray) -> float:
        reconstruction = np.sum(modes, axis=0)
        residual = signal - reconstruction
        mse = np.mean(residual**2)
        return 1.0 / (mse + 1e-12)

    def _get_frequency_grid(self, N: int, fs: float) -> np.ndarray:
        key = (N, fs)
        if key not in self._freq_cache:
            self._freq_cache[key] = np.fft.fftfreq(N, d=1/fs)
        return self._freq_cache[key]

    def vb_decompose(self,
                     f: np.ndarray,
                     fs: float,
                     K: int,
                     vb_iters: int = 10,
                     convergence_tol: float = 1e-4,
                     verbose: bool = True,
                     **kwargs) -> Tuple[np.ndarray, VBPosterior, List[ELBOComponents]]:

        if verbose:
            print(f"🔬 Mathematically Correct VB-VMD")
            print(f"   K={K}, max_iters={vb_iters}")
            print(f"   Noise estimation: {self.estimate_noise}")

        start_time = time.time()
        N = len(f)
        freqs_hz = self._get_frequency_grid(N, fs)

        # === INITIALIZATION ===
        if verbose:
            print("⚡ Initializing with deterministic VMD...")

        init_modes, _, omega_est_bins = self.vmd_core.decompose(
            f, alpha=2000, tau=0.0, K=K, DC=0, init=1, tol=1e-6, **kwargs
        )

        omega_mu_hz = omega_est_bins * fs
        omega_sigma_hz = np.ones(K) * self.sigma_omega_prior_hz * 0.1
        alpha_mu = np.ones(K) * self.mu_alpha_prior
        alpha_sigma = np.ones(K) * self.sigma_alpha_prior * 0.5

        current_noise_precision = self.noise_precision
        if self.estimate_noise:
            if self.bayesian_noise:
                current_noise_precision = self._update_noise_gamma_posterior(f, np.array(init_modes))
            else:
                current_noise_precision = self._estimate_noise_precision(f, np.array(init_modes))

        modes = init_modes
        self._elbo_history.clear()
        self._elbo_components_history.clear()
        prev_elbo = -np.inf

        # Prepare prior objects once
        prior_omega = GaussianPrior(self.mu_omega_prior_hz, self.sigma_omega_prior_hz)
        prior_alpha = GaussianPrior(self.mu_alpha_prior, self.sigma_alpha_prior)

        # === VB-EM ITERATIONS ===
        for it in range(vb_iters):
            iter_start = time.time()
            if verbose:
                print(f"\n🔄 VB-EM iteration {it+1}/{vb_iters}")

            # E-step: Update posteriors q(ω_k), q(α_k)
            fft_modes = [np.fft.fft(mode) for mode in modes]
            for k in range(K):
                u_hat_k = fft_modes[k]
                mu_ω, sig_ω = fast_bayesian_update_omega(
                    freqs_hz, u_hat_k.real, u_hat_k.imag,
                    self.mu_omega_prior_hz,
                    self.sigma_omega_prior_hz,
                    1.0 / np.sqrt(current_noise_precision)
                )
                omega_mu_hz[k] = mu_ω
                omega_sigma_hz[k] = sig_ω

                mu_α, sig_α = fast_bayesian_update_alpha(
                    u_hat_k.real, u_hat_k.imag,
                    self.mu_alpha_prior,
                    self.sigma_alpha_prior
                )
                alpha_mu[k] = mu_α
                alpha_sigma[k] = sig_α

            # M-step: Recompute modes with expected α
            exp_alpha = fast_exp_alpha_computation(alpha_mu, alpha_sigma)
            mean_alpha = np.mean(exp_alpha)

            modes, _, _ = self.vmd_core.decompose(
                f, alpha=mean_alpha, tau=0.0, K=K, DC=0, init=modes, tol=1e-6, **kwargs
            )

            if self.estimate_noise:
                current_noise_precision = self._estimate_noise_precision(f, np.array(modes))

            vb_post = VBPosterior(
                omega_mu=omega_mu_hz.copy(),
                omega_sigma=omega_sigma_hz.copy(),
                alpha_mu=alpha_mu.copy(),
                alpha_sigma=alpha_sigma.copy()
            )

            # Correct ELBO with prior objects
            elbo_components = compute_true_elbo(
                f,
                np.array(modes),
                vb_post,
                fs,
                current_noise_precision,
                prior_omega,
                prior_alpha
            )

            current_elbo = elbo_components.total_elbo
            self._elbo_history.append(current_elbo)
            self._elbo_components_history.append(elbo_components)

            # Convergence
            if it > 0:
                elbo_change = current_elbo - prev_elbo
                rel_change = abs(elbo_change) / (abs(prev_elbo) + 1e-12)

                if verbose:
                    print(f"   ELBO: {current_elbo:8.2f} (Δ={elbo_change:+7.2f}, rel={rel_change:.2e})")
                    print(f"   Components: L={elbo_components.data_likelihood:.1f}, Reg={elbo_components.mode_regularization:.1f}")
                    print(f"               KLω={elbo_components.kl_omega:.1f}, KLα={elbo_components.kl_alpha:.1f}")
                    if self.estimate_noise:
                        print(f"               Noise precision: {current_noise_precision:.2f}")

                if rel_change < convergence_tol and elbo_change > -1e-6:
                    if verbose:
                        print(f"✅ Converged at iteration {it+1}")
                    break
            else:
                if verbose:
                    print(f"   Initial ELBO: {current_elbo:.2f}")

            prev_elbo = current_elbo
            if verbose:
                print(f"   Iteration time: {time.time() - iter_start:.3f}s")

        total_time = time.time() - start_time
        if verbose:
            print(f"\n🎯 VB-VMD completed in {total_time:.2f}s")
            print(f"📊 Final ELBO: {current_elbo:.2f}")
            print(f"🔊 Final noise precision: {current_noise_precision:.2f}")
            print(f"📈 Estimated frequencies:")
            for k in range(K):
                print(f"   Mode {k+1}: {omega_mu_hz[k]:6.1f} ± {omega_sigma_hz[k]:5.1f} Hz")

        return modes, vb_post, self._elbo_components_history
    def plot_elbo_convergence(self, figsize=(12, 8)):
        """Plot ELBO convergence with component breakdown"""
        if not self._elbo_components_history:
            print("No ELBO history available.")
            return
        
        import matplotlib.pyplot as plt
        
        iterations = range(len(self._elbo_components_history))
        
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        
        # Total ELBO
        total_elbos = [comp.total_elbo for comp in self._elbo_components_history]
        axes[0, 0].plot(iterations, total_elbos, 'b-', linewidth=2)
        axes[0, 0].set_title('Total ELBO')
        axes[0, 0].set_ylabel('ELBO')
        axes[0, 0].grid(True, alpha=0.3)
        
        # Data likelihood
        likelihoods = [comp.data_likelihood for comp in self._elbo_components_history]
        axes[0, 1].plot(iterations, likelihoods, 'g-', linewidth=2)
        axes[0, 1].set_title('Data Likelihood')
        axes[0, 1].set_ylabel('Log Likelihood')
        axes[0, 1].grid(True, alpha=0.3)
        
        # KL divergences
        kl_omega = [comp.kl_omega for comp in self._elbo_components_history]
        kl_alpha = [comp.kl_alpha for comp in self._elbo_components_history]
        axes[1, 0].plot(iterations, kl_omega, 'r-', linewidth=2, label='KL(ω)')
        axes[1, 0].plot(iterations, kl_alpha, 'm-', linewidth=2, label='KL(α)')
        axes[1, 0].set_title('KL Divergences')
        axes[1, 0].set_ylabel('KL Divergence')
        axes[1, 0].set_xlabel('Iteration')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # ELBO change
        if len(total_elbos) > 1:
            elbo_changes = np.diff(total_elbos)
            axes[1, 1].plot(iterations[1:], elbo_changes, 'k-', linewidth=2)
            axes[1, 1].axhline(y=0, color='r', linestyle='--', alpha=0.5)
            axes[1, 1].set_title('ELBO Change')
            axes[1, 1].set_ylabel('ΔELBO')
            axes[1, 1].set_xlabel('Iteration')
            axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()

# ==============================
# === FAST BAYESIAN UPDATES ===
# ==============================


import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import seaborn as sns
from typing import List, Optional
import warnings
warnings.filterwarnings('ignore')

# Set modern plotting style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

class VBVMDPlotter:
    """
    Comprehensive plotting suite for Variational Bayesian VMD
    
    Features:
    - Mode decomposition with uncertainty bands
    - Frequency posterior visualization
    - ELBO convergence analysis
    - Spectral analysis with uncertainty
    - Comparative analysis
    - Publication-ready figures
    """
    
    def __init__(self, figsize_scale=1.0, style='modern'):
        self.figsize_scale = figsize_scale
        self.style = style
        
        # Color schemes
        self.colors = {
            'primary': '#2E86AB',
            'secondary': '#A23B72', 
            'accent': '#F18F01',
            'success': '#C73E1D',
            'info': '#6A994E',
            'light': '#F5F5F5',
            'dark': '#2D3436'
        }
        
        # Font settings
        plt.rcParams.update({
            'font.size': 10,
            'axes.titlesize': 12,
            'axes.labelsize': 10,
            'xtick.labelsize': 9,
            'ytick.labelsize': 9,
            'legend.fontsize': 9,
            'figure.titlesize': 14
        })
    
    def plot_complete_analysis(self, t, signal, modes, vb_post, elbo_history, fs, 
                              save_path=None, show_uncertainty=True):
        """
        Complete VB-VMD analysis in one comprehensive figure
        """
        K = len(modes)
        
        # Create subplot layout
        fig = plt.figure(figsize=(16*self.figsize_scale, 12*self.figsize_scale))
        gs = fig.add_gridspec(5, 3, height_ratios=[1, 2, 2, 1.5, 1.5], hspace=0.3, wspace=0.3)
        
        # 1. Original Signal
        ax_orig = fig.add_subplot(gs[0, :])
        ax_orig.plot(t, signal, color=self.colors['dark'], linewidth=1.5, alpha=0.8)
        ax_orig.set_title('🔬 Original Signal', fontsize=14, pad=15)
        ax_orig.set_ylabel('Amplitude')
        ax_orig.grid(True, alpha=0.3)
        
        # Add signal statistics
        signal_stats = f"Mean: {np.mean(signal):.3f} | Std: {np.std(signal):.3f} | Length: {len(signal)} samples"
        ax_orig.text(0.02, 0.95, signal_stats, transform=ax_orig.transAxes, 
                    bbox=dict(boxstyle="round,pad=0.3", facecolor=self.colors['light'], alpha=0.8),
                    fontsize=9, verticalalignment='top')
        
        # 2. Mode Decomposition with better layout for trend components
        mode_axes = []
        for k in range(K):
            ax_mode = fig.add_subplot(gs[1, k] if K <= 3 else gs[1 + k//3, k%3])
            mode_axes.append(ax_mode)
            
            # Plot mode
            ax_mode.plot(t, modes[k], color=f'C{k}', linewidth=2, alpha=0.8, 
                        label=f'Mode {k+1}')
            
            # Add uncertainty bands if requested
            if show_uncertainty and hasattr(vb_post, 'mode_uncertainties'):
                mode_std = getattr(vb_post, 'mode_uncertainties', None)
                if mode_std is not None and len(mode_std) > k:
                    ax_mode.fill_between(t, modes[k] - 2*mode_std[k], 
                                       modes[k] + 2*mode_std[k],
                                       alpha=0.2, color=f'C{k}', label='95% CI')
            
            # Posterior statistics
            omega_mean = vb_post.omega_mu[k]
            omega_std = vb_post.omega_sigma[k]
            alpha_mean = vb_post.alpha_mu[k]
            alpha_std = vb_post.alpha_sigma[k]
            
            # Handle trend/DC components differently
            if omega_mean < 0.1:  # Likely trend/DC component
                title = f'Mode {k+1} (Trend/DC)\nω: {omega_mean:.3f}±{omega_std:.3f} Hz'
            else:
                title = f'Mode {k+1}\nω: {omega_mean:.1f}±{omega_std:.1f} Hz'
            
            ax_mode.set_title(title, fontsize=11)
            ax_mode.grid(True, alpha=0.3)
            ax_mode.legend(loc='upper right', fontsize=8)
            
            if k >= K - (K % 3 or 3):  # Bottom row
                ax_mode.set_xlabel('Time (s)')
            ax_mode.set_ylabel('Amplitude')
        
        # 3. Enhanced Frequency Domain Analysis
        ax_freq = fig.add_subplot(gs[3, :])
        
        # Original signal spectrum
        freqs = np.fft.rfftfreq(len(signal), d=1/fs)
        signal_fft = np.abs(np.fft.rfft(signal))
        ax_freq.plot(freqs, signal_fft, color=self.colors['dark'], 
                    alpha=0.6, linewidth=1, label='Original spectrum')
        
        # Separate trend and oscillatory modes
        trend_modes = []
        osc_modes = []
        trend_indices = []
        osc_indices = []
        
        for k in range(K):
            omega_mean = vb_post.omega_mu[k]
            if omega_mean < 0.1:  # Trend/DC component
                trend_modes.append(k)
                trend_indices.append(k)
            else:
                osc_modes.append(k)
                osc_indices.append(k)
        
        # Plot oscillatory modes normally
        for k in osc_indices:
            mode_fft = np.abs(np.fft.rfft(modes[k]))
            ax_freq.plot(freqs, mode_fft, color=f'C{k}', linewidth=2, 
                        alpha=0.8, label=f'Mode {k+1}')
            
            # Frequency posterior
            omega_mean = vb_post.omega_mu[k]
            omega_std = vb_post.omega_sigma[k]
            
            # Mark mean frequency
            ax_freq.axvline(omega_mean, color=f'C{k}', linestyle='--', 
                          alpha=0.8, linewidth=2)
            
            # Uncertainty region
            ax_freq.axvspan(max(0, omega_mean - omega_std), 
                          omega_mean + omega_std,
                          alpha=0.15, color=f'C{k}')
            
            # Add frequency annotation
            max_fft_val = np.max(mode_fft)
            if max_fft_val > 0.01 * np.max(signal_fft):  # Only annotate significant peaks
                ax_freq.annotate(f'{omega_mean:.1f}±{omega_std:.1f}Hz', 
                               xy=(omega_mean, max_fft_val*0.8), 
                               xytext=(10, 10), textcoords='offset points',
                               fontsize=9, ha='center',
                               bbox=dict(boxstyle="round,pad=0.3", 
                                       facecolor=f'C{k}', alpha=0.7),
                               arrowprops=dict(arrowstyle='->', color=f'C{k}'))
        
        # Handle trend modes with special annotation
        if trend_indices:
            # Add text box explaining trend components
            trend_text = "Trend/DC Components:\n"
            for k in trend_indices:
                omega_mean = vb_post.omega_mu[k]
                omega_std = vb_post.omega_sigma[k]
                trend_text += f"Mode {k+1}: {omega_mean:.3f}±{omega_std:.3f} Hz\n"
            
            ax_freq.text(0.02, 0.98, trend_text.strip(), transform=ax_freq.transAxes,
                        bbox=dict(boxstyle="round,pad=0.5", facecolor=self.colors['light'], alpha=0.9),
                        fontsize=9, verticalalignment='top',
                        family='monospace')
        
        ax_freq.set_xlabel('Frequency (Hz)')
        ax_freq.set_ylabel('Magnitude')
        ax_freq.set_title('🌊 Spectral Analysis with Uncertainty', fontsize=12)
        ax_freq.legend(loc='upper right')
        ax_freq.grid(True, alpha=0.3)
        
        # Adjust frequency range to show relevant content
        max_meaningful_freq = max([vb_post.omega_mu[k] + 2*vb_post.omega_sigma[k] 
                                  for k in osc_indices] + [fs/8])
        ax_freq.set_xlim(0, min(max_meaningful_freq, fs/4))
        
        # 4. ELBO Convergence
        ax_elbo = fig.add_subplot(gs[2, 2])
        
        if elbo_history:
            iterations = range(len(elbo_history))
            elbo_values = [comp.total_elbo for comp in elbo_history]
            
            ax_elbo.plot(iterations, elbo_values, color=self.colors['primary'], 
                        linewidth=3, marker='o', markersize=4)
            
            # Highlight convergence
            if len(elbo_values) > 1:
                final_change = abs(elbo_values[-1] - elbo_values[-2])
                if final_change < 1e-3:
                    ax_elbo.scatter(iterations[-1], elbo_values[-1], 
                                  color=self.colors['success'], s=100, 
                                  marker='*', zorder=5, label='Converged')
            
            ax_elbo.set_xlabel('Iteration')
            ax_elbo.set_ylabel('ELBO')
            ax_elbo.set_title('📈 ELBO Convergence', fontsize=12)
            ax_elbo.grid(True, alpha=0.3)
            
            # Add final ELBO value
            final_elbo = elbo_values[-1]
            ax_elbo.text(0.05, 0.95, f'Final ELBO: {final_elbo:.2f}', 
                        transform=ax_elbo.transAxes,
                        bbox=dict(boxstyle="round,pad=0.3", 
                                facecolor=self.colors['light'], alpha=0.8),
                        fontsize=9, verticalalignment='top')
        
        # 5. Enhanced Reconstruction Quality
        ax_recon = fig.add_subplot(gs[4, :])
        
        # Reconstructed signal
        reconstruction = np.sum(modes, axis=0)
        residual = signal - reconstruction
        
        ax_recon.plot(t, signal, color=self.colors['dark'], linewidth=2, 
                     alpha=0.7, label='Original')
        ax_recon.plot(t, reconstruction, color=self.colors['accent'], 
                     linewidth=2, alpha=0.8, label='Reconstruction')
        ax_recon.plot(t, residual, color=self.colors['secondary'], 
                     linewidth=1, alpha=0.6, label='Residual')
        
        # Add individual mode contributions for trend components
        if trend_indices:
            for k in trend_indices:
                ax_recon.plot(t, modes[k], color=f'C{k}', linewidth=1.5, 
                            alpha=0.7, linestyle=':', 
                            label=f'Mode {k+1} (Trend)')
        
        # Reconstruction metrics
        mse = np.mean(residual**2)
        snr = 10 * np.log10(np.var(signal) / (mse + 1e-12))
        
        # Mode contribution analysis
        mode_energies = [np.var(mode) for mode in modes]
        total_mode_energy = sum(mode_energies)
        mode_contributions = [energy/total_mode_energy*100 for energy in mode_energies]
        
        contribution_text = " | ".join([f"M{k+1}: {cont:.1f}%" 
                                       for k, cont in enumerate(mode_contributions)])
        
        ax_recon.set_xlabel('Time (s)')
        ax_recon.set_ylabel('Amplitude')
        title_text = f'🎯 Reconstruction Quality | MSE: {mse:.4f} | SNR: {snr:.1f} dB\nMode Contributions: {contribution_text}'
        ax_recon.set_title(title_text, fontsize=12)
        ax_recon.legend(loc='upper right')
        ax_recon.grid(True, alpha=0.3)
        
        # Overall title
        fig.suptitle('🔬 Variational Bayesian VMD - Complete Analysis', 
                    fontsize=16, y=0.98)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            print(f"💾 Figure saved to: {save_path}")
        
        plt.tight_layout()
        plt.show()
    
    def plot_posterior_distributions(self, vb_post, save_path=None):
        """
        Plot posterior distributions for all parameters
        """
        K = len(vb_post.omega_mu)
        
        fig, axes = plt.subplots(2, 2, figsize=(12*self.figsize_scale, 10*self.figsize_scale))
        
        # 1. Frequency Posteriors
        ax_omega = axes[0, 0]
        for k in range(K):
            mu = vb_post.omega_mu[k]
            sigma = vb_post.omega_sigma[k]
            
            # Generate distribution
            x = np.linspace(max(0, mu - 4*sigma), mu + 4*sigma, 200)
            y = np.exp(-0.5 * ((x - mu) / sigma)**2) / (sigma * np.sqrt(2*np.pi))
            
            ax_omega.plot(x, y, color=f'C{k}', linewidth=2, 
                         label=f'ω_{k+1}: {mu:.1f}±{sigma:.1f} Hz')
            ax_omega.fill_between(x, 0, y, alpha=0.3, color=f'C{k}')
            
            # Mark mean
            ax_omega.axvline(mu, color=f'C{k}', linestyle='--', alpha=0.8)
        
        ax_omega.set_xlabel('Frequency (Hz)')
        ax_omega.set_ylabel('Posterior Density')
        ax_omega.set_title('🌊 Frequency Posteriors q(ω_k)', fontsize=12)
        ax_omega.legend()
        ax_omega.grid(True, alpha=0.3)
        
        # 2. Alpha Posteriors (Log-Normal)
        ax_alpha = axes[0, 1]
        for k in range(K):
            mu_log = vb_post.alpha_mu[k]
            sigma_log = vb_post.alpha_sigma[k]
            
            # Log-normal distribution
            x = np.linspace(0.1, np.exp(mu_log + 3*sigma_log), 200)
            y = (1 / (x * sigma_log * np.sqrt(2*np.pi)) * 
                 np.exp(-0.5 * ((np.log(x) - mu_log) / sigma_log)**2))
            
            ax_alpha.plot(x, y, color=f'C{k}', linewidth=2,
                         label=f'α_{k+1}: exp({mu_log:.1f}±{sigma_log:.1f})')
            ax_alpha.fill_between(x, 0, y, alpha=0.3, color=f'C{k}')
            
            # Mark expected value
            exp_alpha = np.exp(mu_log + 0.5 * sigma_log**2)
            ax_alpha.axvline(exp_alpha, color=f'C{k}', linestyle='--', alpha=0.8)
        
        ax_alpha.set_xlabel('Alpha (Regularization)')
        ax_alpha.set_ylabel('Posterior Density')
        ax_alpha.set_title('⚖️ Regularization Posteriors q(α_k)', fontsize=12)
        ax_alpha.legend()
        ax_alpha.grid(True, alpha=0.3)
        ax_alpha.set_xscale('log')
        
        # 3. Parameter Correlations
        ax_corr = axes[1, 0]
        
        # Create correlation matrix
        omega_values = vb_post.omega_mu
        alpha_values = [np.exp(mu + 0.5*sig**2) for mu, sig in 
                       zip(vb_post.alpha_mu, vb_post.alpha_sigma)]
        
        # Scatter plot
        ax_corr.scatter(omega_values, alpha_values, 
                       c=range(K), cmap='viridis', s=100, alpha=0.7)
        
        for k in range(K):
            ax_corr.annotate(f'Mode {k+1}', 
                           (omega_values[k], alpha_values[k]),
                           xytext=(5, 5), textcoords='offset points',
                           fontsize=9)
        
        ax_corr.set_xlabel('Frequency ω (Hz)')
        ax_corr.set_ylabel('Expected Alpha E[α]')
        ax_corr.set_title('🔗 Parameter Relationships', fontsize=12)
        ax_corr.grid(True, alpha=0.3)
        
        # 4. Uncertainty Summary
        ax_summary = axes[1, 1]
        
        # Bar plot of uncertainties
        omega_uncertainties = vb_post.omega_sigma
        alpha_uncertainties = vb_post.alpha_sigma
        
        x = np.arange(K)
        width = 0.35
        
        bars1 = ax_summary.bar(x - width/2, omega_uncertainties, width, 
                              label='Frequency σ(ω)', alpha=0.8, color=self.colors['primary'])
        bars2 = ax_summary.bar(x + width/2, alpha_uncertainties, width,
                              label='Alpha σ(log α)', alpha=0.8, color=self.colors['accent'])
        
        # Add value labels on bars
        for bar in bars1:
            height = bar.get_height()
            ax_summary.annotate(f'{height:.2f}',
                              xy=(bar.get_x() + bar.get_width() / 2, height),
                              xytext=(0, 3), textcoords="offset points",
                              ha='center', va='bottom', fontsize=8)
        
        for bar in bars2:
            height = bar.get_height()
            ax_summary.annotate(f'{height:.2f}',
                              xy=(bar.get_x() + bar.get_width() / 2, height),
                              xytext=(0, 3), textcoords="offset points",
                              ha='center', va='bottom', fontsize=8)
        
        ax_summary.set_xlabel('Mode')
        ax_summary.set_ylabel('Posterior Standard Deviation')
        ax_summary.set_title('📊 Uncertainty Summary', fontsize=12)
        ax_summary.set_xticks(x)
        ax_summary.set_xticklabels([f'Mode {k+1}' for k in range(K)])
        ax_summary.legend()
        ax_summary.grid(True, alpha=0.3)
        
        fig.suptitle('🎲 Posterior Distribution Analysis', fontsize=16, y=0.98)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            print(f"💾 Posterior plots saved to: {save_path}")
        
        plt.tight_layout()
        plt.show()
    
    def plot_elbo_decomposition(self, elbo_history, save_path=None):
        """
        Detailed ELBO component analysis
        """
        if not elbo_history:
            print("❌ No ELBO history available")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(14*self.figsize_scale, 10*self.figsize_scale))
        
        iterations = range(len(elbo_history))
        
        # Extract components
        total_elbo = [comp.total_elbo for comp in elbo_history]
        data_likelihood = [comp.data_likelihood for comp in elbo_history]
        kl_omega = [comp.kl_omega for comp in elbo_history]
        kl_alpha = [comp.kl_alpha for comp in elbo_history]
        
        # 1. Total ELBO
        ax_total = axes[0, 0]
        ax_total.plot(iterations, total_elbo, color=self.colors['primary'], 
                     linewidth=3, marker='o', markersize=4)
        ax_total.set_title('📈 Total ELBO', fontsize=12)
        ax_total.set_ylabel('ELBO')
        ax_total.grid(True, alpha=0.3)
        
        # Highlight final value
        ax_total.annotate(f'Final: {total_elbo[-1]:.2f}',
                         xy=(iterations[-1], total_elbo[-1]),
                         xytext=(10, 10), textcoords='offset points',
                         bbox=dict(boxstyle="round,pad=0.3", 
                                 facecolor=self.colors['primary'], alpha=0.7),
                         fontsize=9, color='white')
        
        # 2. Data Likelihood
        ax_likelihood = axes[0, 1]
        ax_likelihood.plot(iterations, data_likelihood, color=self.colors['success'], 
                          linewidth=2, marker='s', markersize=3)
        ax_likelihood.set_title('🎯 Data Likelihood E[log p(f|u)]', fontsize=12)
        ax_likelihood.set_ylabel('Log Likelihood')
        ax_likelihood.grid(True, alpha=0.3)
        
        # 3. KL Divergences
        ax_kl = axes[1, 0]
        ax_kl.plot(iterations, kl_omega, color=self.colors['accent'], 
                  linewidth=2, marker='^', markersize=3, label='KL[q(ω)||p(ω)]')
        ax_kl.plot(iterations, kl_alpha, color=self.colors['secondary'], 
                  linewidth=2, marker='v', markersize=3, label='KL[q(α)||p(α)]')
        ax_kl.set_title('⚖️ KL Divergences', fontsize=12)
        ax_kl.set_ylabel('KL Divergence')
        ax_kl.set_xlabel('Iteration')
        ax_kl.legend()
        ax_kl.grid(True, alpha=0.3)
        
        # 4. ELBO Change (Convergence)
        ax_change = axes[1, 1]
        if len(total_elbo) > 1:
            elbo_changes = np.diff(total_elbo)
            ax_change.plot(iterations[1:], elbo_changes, color=self.colors['dark'], 
                          linewidth=2, marker='o', markersize=3)
            ax_change.axhline(y=0, color='red', linestyle='--', alpha=0.5)
            
            # Mark convergence threshold
            convergence_line = 1e-3
            ax_change.axhline(y=convergence_line, color='orange', 
                            linestyle=':', alpha=0.7, label='Convergence threshold')
            ax_change.axhline(y=-convergence_line, color='orange', 
                            linestyle=':', alpha=0.7)
            
            ax_change.set_title('🎯 ELBO Change (Convergence)', fontsize=12)
            ax_change.set_ylabel('ΔELBO')
            ax_change.set_xlabel('Iteration')
            ax_change.legend()
            ax_change.grid(True, alpha=0.3)
            ax_change.set_yscale('symlog', linthresh=1e-6)
        
        fig.suptitle('🔬 ELBO Component Analysis', fontsize=16, y=0.98)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            print(f"💾 ELBO analysis saved to: {save_path}")
        
        plt.tight_layout()
        plt.show()
    
    def plot_comparison_with_classical(self, t, signal, vb_modes, vb_post, 
                                     classical_modes, classical_freqs=None, 
                                     save_path=None):
        """
        Compare VB-VMD with classical VMD
        """
        K = len(vb_modes)
        
        fig, axes = plt.subplots(K+1, 3, figsize=(15*self.figsize_scale, 
                                                  (K+1)*3*self.figsize_scale))
        
        # Original signal
        for col in range(3):
            axes[0, col].plot(t, signal, color=self.colors['dark'], 
                            linewidth=2, alpha=0.8)
            axes[0, col].set_title(['Original Signal', 'Original Signal', 
                                  'Original Signal'][col])
            axes[0, col].grid(True, alpha=0.3)
        
        # Mode comparisons
        for k in range(K):
            # VB-VMD Mode
            axes[k+1, 0].plot(t, vb_modes[k], color=f'C{k}', linewidth=2)
            omega_vb = vb_post.omega_mu[k]
            sigma_vb = vb_post.omega_sigma[k]
            axes[k+1, 0].set_title(f'VB Mode {k+1}\nω: {omega_vb:.1f}±{sigma_vb:.1f} Hz')
            axes[k+1, 0].grid(True, alpha=0.3)
            
            # Classical VMD Mode
            if k < len(classical_modes):
                axes[k+1, 1].plot(t, classical_modes[k], color=f'C{k}', linewidth=2)
                freq_classical = classical_freqs[k] if classical_freqs else "N/A"
                axes[k+1, 1].set_title(f'Classical Mode {k+1}\nω: {freq_classical:.1f} Hz' 
                                     if isinstance(freq_classical, (int, float)) 
                                     else f'Classical Mode {k+1}')
                axes[k+1, 1].grid(True, alpha=0.3)
            
            # Difference
            if k < len(classical_modes):
                diff = vb_modes[k] - classical_modes[k]
                axes[k+1, 2].plot(t, diff, color=self.colors['secondary'], linewidth=2)
                mse = np.mean(diff**2)
                axes[k+1, 2].set_title(f'Difference Mode {k+1}\nMSE: {mse:.4f}')
                axes[k+1, 2].grid(True, alpha=0.3)
        
        # Set labels
        for row in range(K+1):
            axes[row, 0].set_ylabel('Amplitude')
            if row == K:  # Bottom row
                for col in range(3):
                    axes[row, col].set_xlabel('Time (s)')
        
        # Column titles
        fig.text(0.2, 0.98, '🔬 Variational Bayesian VMD', ha='center', 
                fontsize=14, weight='bold')
        fig.text(0.5, 0.98, '⚙️ Classical VMD', ha='center', 
                fontsize=14, weight='bold')
        fig.text(0.8, 0.98, '📊 Difference', ha='center', 
                fontsize=14, weight='bold')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            print(f"💾 Comparison plot saved to: {save_path}")
        
        plt.tight_layout()
        plt.show()

# Updated test and plotting code
def generate_test_signal():
    """Generate a more interesting test signal"""
    t = np.linspace(0, 8, 1500)
    fs = len(t)/(t[-1]-t[0])
    
    # Multi-component signal with trend
    signal = (0.3*t +  # Trend
              np.sin(2*np.pi*4*t) +  # 4 Hz
              0.6*np.sin(2*np.pi*15*t) +  # 15 Hz  
              0.4*np.sin(2*np.pi*35*t) +  # 35 Hz
              0.05*np.random.normal(size=len(t)))  # Noise
    
    return t, signal, fs

def demo_vb_vmd_plotting():
    """Comprehensive demonstration of VB-VMD plotting"""
    
    print("🎨 VB-VMD Plotting Suite Demonstration")
    print("="*50)
    
    # Generate test signal
    t, signal, fs = generate_test_signal()
    print(f"📊 Signal: {len(signal)} samples @ {fs:.1f} Hz")
    
    # Setup VB-VMD (replace with your actual implementation)
    try:
        from vmd import VMDCore, VBVMDCore
        vmd_core = VMDCore()
        vb_core = VBVMDCore(
            vmd_core=vmd_core,
            mu_omega_prior_hz=0.0,
            sigma_omega_prior_hz=50.0,
            mu_alpha_prior=5.0,
            sigma_alpha_prior=1.0,
        )
        
        # Run VB-VMD
        print("🔬 Running VB-VMD...")
        K = 4
        modes, vb_post, elbo_history = vb_core.vb_decompose(
            signal, fs,
            K=K,
            vb_iters=8,
            convergence_tol=1e-3,
            verbose=True
        )
        
        # Initialize plotter
        plotter = VBVMDPlotter(figsize_scale=1.0)
        
        # 1. Complete analysis
        print("\n📈 Creating complete analysis plot...")
        plotter.plot_complete_analysis(t, signal, modes, vb_post, 
                                     elbo_history, fs, show_uncertainty=True)
        
        # 2. Posterior distributions
        print("\n🎲 Creating posterior distribution plots...")
        plotter.plot_posterior_distributions(vb_post)
        
        # 3. ELBO decomposition
        print("\n📊 Creating ELBO decomposition plots...")
        plotter.plot_elbo_decomposition(elbo_history)
        
        print("\n✅ All plots generated successfully!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure VMDCore and VBVMDCore are available")
    except Exception as e:
        print(f"❌ Error during plotting: {e}")

if __name__ == "__main__":
    demo_vb_vmd_plotting()