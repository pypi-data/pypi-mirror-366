# === Standard Library ===
import gc
import time
import threading
import pickle
from typing import Any, Dict, List, Optional, Tuple
from sklearn.cluster import DBSCAN

# === Numerical & Scientific ===
import numpy as np
import pyfftw
import pyfftw.interfaces.numpy_fft as fftw_np
from numba import njit, prange

# === Optimization / ML ===
import optuna
import os
from dataclasses import dataclass

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
                with open(self.wisdom_file, "rb") as f:
                    pyfftw.import_wisdom(pickle.load(f))
                print("🧠 FFTW wisdom loaded - FFTs will be faster!")
            except:
                print("⚠️ Could not load FFTW wisdom file")

    def save_wisdom(self):
        """Save FFTW wisdom for future runs"""
        try:
            with open(self.wisdom_file, "wb") as f:
                pickle.dump(pyfftw.export_wisdom(), f)
            print("💾 FFTW wisdom saved for future speedup")
        except:
            print("⚠️ Could not save FFTW wisdom")
     

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
    boundary_method: str = "reflect"
    apply_tapering: bool = True


@dataclass
class HierarchicalParameters:
    """Configuration parameters for hierarchical VMD"""

    max_levels: int = 3
    energy_threshold: float = 0.01
    min_samples_per_level: int = 100
    use_anti_aliasing: bool = True


# Ultra-fast numba implementations
@njit(fastmath=True, cache=True, parallel=True)
def _find_peaks(spec, freqs, threshold_ratio=0.05):
    """Ultra-fast peak finding using numba"""
    max_val = 0.0
    for i in prange(len(spec)):
        if spec[i] > max_val:
            max_val = spec[i]
    
    energy_threshold = threshold_ratio * max_val
    
    # Count peaks above threshold
    peak_count = 0
    for i in range(len(spec)):
        if spec[i] > energy_threshold:
            peak_count += 1
    
    # Extract peaks
    peak_freqs = np.zeros(peak_count)
    peak_amps = np.zeros(peak_count)
    
    idx = 0
    for i in range(len(spec)):
        if spec[i] > energy_threshold:
            peak_freqs[idx] = freqs[i]
            peak_amps[idx] = spec[i]
            idx += 1
    
    return peak_freqs, peak_amps

@njit(fastmath=True, cache=True)
def _spectral_entropy(spec):
    """Ultra-fast spectral entropy calculation"""
    # Normalize spectrum
    total = 0.0
    for i in range(len(spec)):
        total += spec[i]
    
    if total < 1e-12:
        return 0.0
    
    entropy = 0.0
    for i in range(len(spec)):
        p = spec[i] / total
        if p > 1e-12:
            entropy -= p * np.log(p)
    
    return entropy

@njit(fastmath=True, cache=True, parallel=True)
def _signal_stats(signal):
    """Ultra-fast signal statistics calculation"""
    N = len(signal)
    
    # Mean
    mean_val = 0.0
    for i in prange(N):
        mean_val += signal[i]
    mean_val /= N
    
    # Standard deviation
    var = 0.0
    for i in prange(N):
        diff = signal[i] - mean_val
        var += diff * diff
    std_val = np.sqrt(var / N)
    
    # Derivative variance
    if N > 1:
        deriv_var = 0.0
        deriv_mean = 0.0
        
        # Calculate derivative mean
        for i in range(N - 1):
            diff = signal[i + 1] - signal[i]
            deriv_mean += diff
        deriv_mean /= (N - 1)
        
        # Calculate derivative variance
        for i in range(N - 1):
            diff = signal[i + 1] - signal[i]
            deriv_diff = diff - deriv_mean
            deriv_var += deriv_diff * deriv_diff
        deriv_var /= (N - 1)
        
        variability = np.sqrt(deriv_var) / (std_val + 1e-12)
    else:
        variability = 0.0
    
    return mean_val, std_val, variability

@njit(fastmath=True, cache=True, parallel=True)
def _extend_mirror(signal, ext_len):
    """Ultra-fast mirror extension"""
    N = len(signal)
    total_len = N + 2 * ext_len
    extended = np.zeros(total_len)
    
    # Copy original signal
    for i in prange(N):
        extended[ext_len + i] = signal[i]
    
    # Left extension (mirror)
    for i in prange(ext_len):
        if i + 1 < N:
            extended[ext_len - 1 - i] = signal[i + 1]
        else:
            extended[ext_len - 1 - i] = signal[N - 1]
    
    # Right extension (mirror)
    for i in prange(ext_len):
        if N - 2 - i >= 0:
            extended[ext_len + N + i] = signal[N - 2 - i]
        else:
            extended[ext_len + N + i] = signal[0]
    
    return extended

@njit(fastmath=True, cache=True, parallel=True)
def _extend_reflect(signal, ext_len):
    """Ultra-fast reflection extension"""
    N = len(signal)
    total_len = N + 2 * ext_len
    extended = np.zeros(total_len)
    
    left_val = signal[0]
    right_val = signal[N - 1]
    
    # Copy original signal
    for i in prange(N):
        extended[ext_len + i] = signal[i]
    
    # Left extension (reflect)
    for i in prange(ext_len):
        if i + 1 < N:
            extended[ext_len - 1 - i] = 2 * left_val - signal[i + 1]
        else:
            extended[ext_len - 1 - i] = left_val
    
    # Right extension (reflect)
    for i in prange(ext_len):
        if N - 2 - i >= 0:
            extended[ext_len + N + i] = 2 * right_val - signal[N - 2 - i]
        else:
            extended[ext_len + N + i] = right_val
    
    return extended

@njit(fastmath=True, cache=True, parallel=True)
def _taper_mode(mode, taper_len):
    """Ultra-fast boundary tapering"""
    N = len(mode)
    tapered = np.zeros(N)
    
    # Copy original mode
    for i in prange(N):
        tapered[i] = mode[i]
    
    # Apply tapering
    for i in prange(min(taper_len, N // 4)):
        # Left taper
        factor = np.sin(i * np.pi / (2.0 * taper_len))**2
        tapered[i] *= factor
        
        # Right taper  
        factor = np.cos(i * np.pi / (2.0 * taper_len))**2
        tapered[N - 1 - i] *= factor
    
    return tapered

class SignalAnalyzer:
    """Ultra-optimized signal analyzer for VMD parameter optimization"""
    
    def __init__(self):
        # Cache for repeated analysis
        self._analysis_cache = {}
        self._peak_cache = {}
        
    @staticmethod
    def _find_significant_peaks(
        spec: np.ndarray, freqs: np.ndarray, threshold_ratio: float = 0.05
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Ultra-fast significant peak detection using numba"""
        return _find_peaks(spec, freqs, threshold_ratio)
    
    @staticmethod
    def _cluster_dominant_freqs(freqs: np.ndarray, eps_ratio: float = 0.05) -> np.ndarray:
        """
        Ultra-fast frequency clustering with optimized DBSCAN
        """
        if len(freqs) < 2:
            return np.array([0])
        
        # Optimized clustering for small arrays
        if len(freqs) <= 10:
            # Simple distance-based clustering for small arrays
            sorted_freqs = np.sort(freqs)
            freq_range = sorted_freqs[-1] - sorted_freqs[0]
            eps = eps_ratio * freq_range
            
            labels = []
            current_label = 0
            
            for i, freq in enumerate(sorted_freqs):
                if i == 0:
                    labels.append(current_label)
                else:
                    if freq - sorted_freqs[i-1] > eps:
                        current_label += 1
                    labels.append(current_label)
            
            # Map back to original order
            original_order = np.argsort(np.argsort(freqs))
            return np.array([labels[i] for i in original_order])
        
        # Use DBSCAN for larger arrays
        freq_vals = freqs.reshape(-1, 1)
        eps = eps_ratio * (freqs.max() - freqs.min())
        clustering = DBSCAN(eps=eps, min_samples=1, algorithm='ball_tree').fit(freq_vals)
        return clustering.labels_
    
    def assess_complexity(self, signal: np.ndarray, fs: float):
        """Ultra-fast complexity assessment with intelligent caching"""
        # Generate cache key
        signal_hash = hash(tuple(signal[:min(50, len(signal))].tobytes()))
        cache_key = (signal_hash, len(signal), fs)
        
        if cache_key in self._analysis_cache:
            return self._analysis_cache[cache_key]
        
        start_time = time.time()
        
        N = len(signal)
        
        # Ultra-fast FFT analysis
        spec = np.abs(np.fft.rfft(signal))
        freqs = np.fft.rfftfreq(N, 1 / fs)
        
        # Fast spectral entropy using numba
        spectral_entropy = _spectral_entropy(spec)
        
        # Fast peak detection
        dom_freqs, dom_amps = self._find_significant_peaks(spec, freqs)
        
        # Optimized clustering
        if len(dom_freqs) > 0:
            cluster_labels = self._cluster_dominant_freqs(dom_freqs)
            n_clusters = len(np.unique(cluster_labels))
        else:
            n_clusters = 2  # Default
        
        expected_K = max(2, min(n_clusters, 10))
        
        # Fast bandwidth analysis
        if len(dom_freqs) > 1:
            sorted_freqs = np.sort(dom_freqs)
            freq_diffs = np.diff(sorted_freqs)
            bw = np.median(freq_diffs) if len(freq_diffs) > 0 else fs / (2 * expected_K)
        else:
            bw = fs / (2 * expected_K)
        
        # Smart alpha suggestion
        alpha_suggestion = np.clip(1e3 * (1.0 / (bw + 1e-6)), 300, 8000)
        
        # Ultra-fast signal statistics using numba
        mean_val, std_val, variability = _signal_stats(signal)
        
        # Fast complexity score
        freq_spread = len(dom_freqs) / len(freqs)
        complexity_score = (
            0.4 * (spectral_entropy / 10.0) +
            0.3 * freq_spread +
            0.3 * min(variability, 2.0) / 2.0
        )
        
        # Intelligent parameter selection
        if complexity_score < 0.3:  # Simple
            base_trials = 10  # Reduced for speed
            base_tol = 1e-5
        elif complexity_score < 0.6:  # Moderate
            base_trials = 15  # Reduced for speed
            base_tol = 1e-6
        else:  # Complex
            base_trials = 25  # Reduced for speed
            base_tol = 1e-7
        
        # Create optimized parameters
        params = VMDParameters(
            n_trials=base_trials,
            max_K=min(max(expected_K + 2, 3), 8),  # Reduced max K for speed
            tol=base_tol,
            alpha_min=alpha_suggestion * 0.5,
            alpha_max=alpha_suggestion * 2.0,
            early_stop_patience=4,  # Reduced for speed
        )
        
        analysis_time = time.time() - start_time
        
        print(f"⚡ Signal analysis completed in {analysis_time:.3f}s")
        print(f"🧮 Complexity: {complexity_score:.3f} | Clusters: {expected_K} | K_max: {params.max_K}")
        print(f"📊 Bandwidth: {bw:.2f}Hz → α∈[{params.alpha_min:.0f}, {params.alpha_max:.0f}]")
        print(f"🔍 Trials: {params.n_trials} | Tolerance: {params.tol:.1e}")
        
        # Cache result
        self._analysis_cache[cache_key] = params
        return params

class BoundaryHandler:
    """Ultra-optimized boundary condition handler with numba acceleration"""
    
    def __init__(self):
        # Cache for window functions
        self._window_cache = {}
        
    @staticmethod
    def apply_window(
        signal: np.ndarray, window_type: str = "tukey", alpha_win: float = 0.1
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Ultra-fast windowing with caching"""
        N = len(signal)
        cache_key = (N, window_type, alpha_win)
        
        # Use cached window if available
        if hasattr(BoundaryHandler, '_window_cache') and cache_key in BoundaryHandler._window_cache:
            window = BoundaryHandler._window_cache[cache_key]
        else:
            if window_type == "tukey":
                # Fast Tukey window without scipy
                window = np.ones(N)
                taper_len = int(alpha_win * N / 2)
                if taper_len > 0:
                    t = np.arange(taper_len)
                    taper = 0.5 * (1 - np.cos(np.pi * t / taper_len))
                    window[:taper_len] = taper
                    window[-taper_len:] = taper[::-1]
            elif window_type == "hann":
                window = 0.5 * (1 - np.cos(2 * np.pi * np.arange(N) / (N - 1)))
            elif window_type == "hamming":
                window = 0.54 - 0.46 * np.cos(2 * np.pi * np.arange(N) / (N - 1))
            else:
                window = np.ones(N)
            
            # Cache the window
            if not hasattr(BoundaryHandler, '_window_cache'):
                BoundaryHandler._window_cache = {}
            BoundaryHandler._window_cache[cache_key] = window
        
        return signal * window, window
    
    @staticmethod
    def extend_signal(
        signal: np.ndarray, method: str = "mirror", extension_ratio: float = 0.25
    ) -> Tuple[np.ndarray, int, int]:
        """Ultra-fast signal extension using numba"""
        N = len(signal)
        ext_len = int(N * extension_ratio)
        
        if method == "mirror":
            extended = _extend_mirror(signal, ext_len)
        elif method == "reflect":
            extended = _extend_reflect(signal, ext_len)
        elif method == "linear":
            # Fast linear extension
            left_slope = signal[1] - signal[0] if N > 1 else 0
            right_slope = signal[-1] - signal[-2] if N > 1 else 0
            
            left_ext = signal[0] + left_slope * np.arange(-ext_len, 0)
            right_ext = signal[-1] + right_slope * np.arange(1, ext_len + 1)
            extended = np.concatenate([left_ext, signal, right_ext])
        elif method == "constant":
            # Fast constant extension
            left_ext = np.full(ext_len, signal[0])
            right_ext = np.full(ext_len, signal[-1])
            extended = np.concatenate([left_ext, signal, right_ext])
        else:
            return signal, 0, 0
        
        return extended, ext_len, ext_len
    
    @staticmethod
    def taper_boundaries(
        modes: List[np.ndarray], taper_length: int = 50
    ) -> List[np.ndarray]:
        """Ultra-fast boundary tapering using numba"""
        tapered_modes = []
        
        for mode in modes:
            N = len(mode)
            taper_len = min(taper_length, N // 4)
            
            if taper_len > 0:
                tapered = _taper_mode(mode, taper_len)
            else:
                tapered = mode.copy()
            
            tapered_modes.append(tapered)
        
        return tapered_modes
    
    @staticmethod
    def adaptive_extension_ratio(signal: np.ndarray) -> float:
        """Ultra-fast adaptive extension ratio calculation"""
        N = len(signal)
        if N < 500:
            return 0.3
        elif N < 2000:
            return 0.2
        else:
            return 0.15
    
    @staticmethod
    def auto_window_alpha(
        signal: np.ndarray, min_alpha: float = 0.01, max_alpha: float = 0.1
    ) -> float:
        """Ultra-fast adaptive windowing parameter"""
        if len(signal) < 2:
            return min_alpha
        
        # Fast derivative statistics
        mean_val, std_val, variability = _signal_stats(signal)
        
        # Smoothness factor
        smoothness_factor = 1.0 / (1.0 + variability)
        alpha = min_alpha + (max_alpha - min_alpha) * smoothness_factor
        
        return np.clip(alpha, min_alpha, max_alpha)
    
    def clear_cache(self):
        """Clear window cache to free memory"""
        if hasattr(self, '_window_cache'):
            self._window_cache.clear()
        if hasattr(BoundaryHandler, '_window_cache'):
            BoundaryHandler._window_cache.clear()
        print("🧹 BoundaryHandler cache cleared")
   