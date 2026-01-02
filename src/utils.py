"""
Utility Functions for Adaptive Spectral Oracle
Lex Liberatum Kernels v1.1

Helper functions for:
- Performance metrics (RMSE, MAE, SNR)
- Signal generation (synthetic test data)
- Outlier detection
- Visualization data preparation
- Configuration helpers

Patent: PCT Pending
"""

import numpy as np
from typing import List, Tuple, Dict, Optional, Union
from scipy import signal as sp_signal


def compute_rmse(
    prediction: np.ndarray,
    ground_truth: np.ndarray
) -> float:
    """
    Compute root mean squared error.
    
    Parameters
    ----------
    prediction : ndarray
        Predicted values
    ground_truth : ndarray
        True values
        
    Returns
    -------
    rmse : float
        Root mean squared error
    """
    return float(np.sqrt(np.mean((prediction - ground_truth) ** 2)))


def compute_mae(
    prediction: np.ndarray,
    ground_truth: np.ndarray
) -> float:
    """
    Compute mean absolute error.
    
    Parameters
    ----------
    prediction : ndarray
        Predicted values
    ground_truth : ndarray
        True values
        
    Returns
    -------
    mae : float
        Mean absolute error
    """
    return float(np.mean(np.abs(prediction - ground_truth)))


def compute_max_error(
    prediction: np.ndarray,
    ground_truth: np.ndarray
) -> float:
    """
    Compute maximum absolute error.
    
    Parameters
    ----------
    prediction : ndarray
        Predicted values
    ground_truth : ndarray
        True values
        
    Returns
    -------
    max_error : float
        Maximum absolute error
    """
    return float(np.max(np.abs(prediction - ground_truth)))


def compute_snr_db(
    prediction: np.ndarray,
    ground_truth: np.ndarray
) -> float:
    """
    Compute signal-to-noise ratio in decibels.
    
    Parameters
    ----------
    prediction : ndarray
        Predicted values
    ground_truth : ndarray
        True values
        
    Returns
    -------
    snr_db : float
        Signal-to-noise ratio in dB
    """
    signal_power = np.mean(ground_truth ** 2)
    noise_power = np.mean((prediction - ground_truth) ** 2)
    
    if noise_power == 0:
        return float('inf')
    
    snr = signal_power / noise_power
    return float(10 * np.log10(snr))


def compute_all_metrics(
    prediction: np.ndarray,
    ground_truth: np.ndarray
) -> Dict[str, float]:
    """
    Compute all performance metrics.
    
    Parameters
    ----------
    prediction : ndarray
        Predicted values
    ground_truth : ndarray
        True values
        
    Returns
    -------
    metrics : dict
        Dictionary with keys: rmse, mae, max_error, snr_db
        
    Examples
    --------
    >>> pred = np.array([1.0, 2.0, 3.0])
    >>> truth = np.array([1.1, 2.1, 2.9])
    >>> metrics = compute_all_metrics(pred, truth)
    >>> print(metrics)
    {'rmse': 0.1, 'mae': 0.1, 'max_error': 0.1, 'snr_db': 20.0}
    """
    return {
        'rmse': compute_rmse(prediction, ground_truth),
        'mae': compute_mae(prediction, ground_truth),
        'max_error': compute_max_error(prediction, ground_truth),
        'snr_db': compute_snr_db(prediction, ground_truth)
    }


def generate_synthetic_signals(
    n_clean: int = 5,
    n_poisoned: int = 2,
    T: int = 512,
    noise_level: float = 0.1,
    poison_magnitude: float = 5.0,
    signal_type: str = 'periodic'
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate synthetic test signals with known ground truth.
    
    Parameters
    ----------
    n_clean : int, default=5
        Number of clean (non-corrupted) sensors
    n_poisoned : int, default=2
        Number of poisoned (adversarial) sensors
    T : int, default=512
        Number of time samples
    noise_level : float, default=0.1
        Standard deviation of Gaussian noise
    poison_magnitude : float, default=5.0
        Magnitude of adversarial corruption
    signal_type : str, default='periodic'
        Type of ground truth signal:
        - 'periodic': Multi-frequency sinusoid (compliance patterns)
        - 'chirp': Frequency-swept signal (radar/sonar)
        - 'pulse': Impulse train (event detection)
        - 'random': Random walk (financial time-series)
        
    Returns
    -------
    signals : ndarray of shape (n_clean + n_poisoned, T)
        Generated signals
    ground_truth : ndarray of shape (T,)
        True underlying signal
        
    Examples
    --------
    >>> signals, truth = generate_synthetic_signals(
    ...     n_clean=5, n_poisoned=2, T=512
    ... )
    >>> print(signals.shape)  # (7, 512)
    >>> print(truth.shape)    # (512,)
    """
    t = np.linspace(0, 4 * np.pi, T)
    
    # Generate ground truth based on signal type
    if signal_type == 'periodic':
        # Multi-frequency (simulates daily/weekly compliance cycles)
        ground_truth = (
            np.sin(t) +
            0.3 * np.sin(3 * t) +
            0.2 * np.sin(5 * t)
        )
    elif signal_type == 'chirp':
        # Frequency-swept signal
        ground_truth = sp_signal.chirp(t, f0=1, f1=10, t1=t[-1], method='linear')
    elif signal_type == 'pulse':
        # Impulse train
        ground_truth = np.zeros(T)
        ground_truth[::T//10] = 1.0
    elif signal_type == 'random':
        # Random walk
        np.random.seed(42)
        ground_truth = np.cumsum(np.random.randn(T)) / np.sqrt(T)
    else:
        raise ValueError(f"Unknown signal_type: {signal_type}")
    
    signals = []
    
    # Clean sensors
    for _ in range(n_clean):
        noise = noise_level * np.random.randn(T)
        signals.append(ground_truth + noise)
    
    # Poisoned sensors (adversarial)
    for _ in range(n_poisoned):
        noise = noise_level * np.random.randn(T)
        poison = poison_magnitude * (np.random.rand() - 0.5)
        signals.append(ground_truth + noise + poison)
    
    return np.array(signals), ground_truth


def generate_drift_attack(
    n_clean: int = 5,
    n_drifting: int = 1,
    T: int = 512,
    n_timesteps: int = 100,
    drift_rate: float = 0.05,
    noise_level: float = 0.1
) -> Tuple[List[np.ndarray], np.ndarray]:
    """
    Generate time-series with slowly drifting corruption.
    
    Parameters
    ----------
    n_clean : int
        Number of clean sensors
    n_drifting : int
        Number of sensors with drift
    T : int
        Samples per timestep
    n_timesteps : int
        Number of timesteps
    drift_rate : float
        Rate of drift per timestep
    noise_level : float
        Noise standard deviation
        
    Returns
    -------
    signals_over_time : list of ndarray
        Each element is signals at one timestep
    ground_truth : ndarray
        True signal (same for all timesteps)
        
    Examples
    --------
    >>> signals_list, truth = generate_drift_attack(
    ...     n_clean=5, n_drifting=1, n_timesteps=100
    ... )
    >>> len(signals_list)  # 100 timesteps
    100
    >>> signals_list[0].shape  # (6, 512) at each timestep
    (6, 512)
    """
    t = np.linspace(0, 4 * np.pi, T)
    ground_truth = np.sin(t) + 0.3 * np.sin(3 * t)
    
    signals_over_time = []
    
    for timestep in range(n_timesteps):
        signals = []
        
        # Clean sensors
        for _ in range(n_clean):
            noise = noise_level * np.random.randn(T)
            signals.append(ground_truth + noise)
        
        # Drifting sensors
        for _ in range(n_drifting):
            noise = noise_level * np.random.randn(T)
            drift = drift_rate * timestep  # Linear drift
            signals.append(ground_truth + noise + drift)
        
        signals_over_time.append(np.array(signals))
    
    return signals_over_time, ground_truth


def detect_outliers(
    weights: np.ndarray,
    threshold: float = 0.1
) -> np.ndarray:
    """
    Detect likely outlier signals based on low weights.
    
    Parameters
    ----------
    weights : ndarray
        Signal weights from oracle
    threshold : float, default=0.1
        Weight threshold for outlier detection
        
    Returns
    -------
    outlier_indices : ndarray
        Indices of signals with weights below threshold
        
    Examples
    --------
    >>> weights = np.array([0.3, 0.3, 0.35, 0.05])
    >>> outliers = detect_outliers(weights, threshold=0.1)
    >>> print(outliers)
    [3]
    """
    return np.where(weights < threshold)[0]


def compute_weight_entropy(weights: np.ndarray) -> float:
    """
    Compute Shannon entropy of weight distribution.
    
    Low entropy = weights concentrated on few sensors (possible attack)
    High entropy = weights distributed evenly (clean data)
    
    Parameters
    ----------
    weights : ndarray
        Signal weights
        
    Returns
    -------
    entropy : float
        Shannon entropy in nats
        
    Examples
    --------
    >>> # Equal weights = high entropy
    >>> weights_equal = np.array([0.25, 0.25, 0.25, 0.25])
    >>> compute_weight_entropy(weights_equal)
    1.386...
    
    >>> # Concentrated = low entropy
    >>> weights_concentrated = np.array([0.97, 0.01, 0.01, 0.01])
    >>> compute_weight_entropy(weights_concentrated)
    0.19...
    """
    # Avoid log(0)
    weights = weights[weights > 0]
    return float(-np.sum(weights * np.log(weights)))


def prepare_visualization_data(
    signals: np.ndarray,
    ground_truth: np.ndarray,
    fused: np.ndarray,
    weights: np.ndarray,
    downsample: int = 4
) -> Dict:
    """
    Prepare data for visualization/plotting.
    
    Parameters
    ----------
    signals : ndarray of shape (n_signals, T)
        Input signals
    ground_truth : ndarray of shape (T,)
        True signal
    fused : ndarray of shape (T,)
        Fused result
    weights : ndarray of shape (n_signals,)
        Signal weights
    downsample : int, default=4
        Downsampling factor for plotting
        
    Returns
    -------
    viz_data : dict
        Dictionary with keys:
        - time: downsampled time indices
        - truth: ground truth values
        - fused: fused signal values
        - signals: list of signal values
        - weights: weight values
        - outliers: outlier indices
        
    Examples
    --------
    >>> signals, truth = generate_synthetic_signals(n_clean=3, n_poisoned=1)
    >>> from adaptive_spectral_oracle import AdaptiveSpectralKernel
    >>> oracle = AdaptiveSpectralKernel()
    >>> fused, weights = oracle.fit(signals)
    >>> viz_data = prepare_visualization_data(signals, truth, fused, weights)
    >>> print(viz_data.keys())
    dict_keys(['time', 'truth', 'fused', 'signals', 'weights', 'outliers'])
    """
    T = len(ground_truth)
    time = np.arange(T)[::downsample]
    
    outliers = detect_outliers(weights)
    
    return {
        'time': time.tolist(),
        'truth': ground_truth[::downsample].tolist(),
        'fused': fused[::downsample].tolist(),
        'signals': [sig[::downsample].tolist() for sig in signals],
        'weights': weights.tolist(),
        'outliers': outliers.tolist(),
        'rmse': compute_rmse(fused, ground_truth),
        'weight_entropy': compute_weight_entropy(weights)
    }


def auto_tune_alpha(
    signals: np.ndarray,
    ground_truth: Optional[np.ndarray] = None,
    alpha_range: Tuple[float, float] = (1.0, 3.0),
    n_trials: int = 10
) -> float:
    """
    Auto-tune alpha parameter via grid search.
    
    Parameters
    ----------
    signals : ndarray
        Input signals
    ground_truth : ndarray, optional
        If provided, uses RMSE for tuning
        Otherwise, uses weight entropy (higher is better)
    alpha_range : tuple, default=(1.0, 3.0)
        Range to search
    n_trials : int, default=10
        Number of alpha values to try
        
    Returns
    -------
    best_alpha : float
        Optimal alpha value
        
    Examples
    --------
    >>> signals, truth = generate_synthetic_signals()
    >>> from adaptive_spectral_oracle import auto_tune_alpha
    >>> best_alpha = auto_tune_alpha(signals, truth)
    >>> print(f"Best alpha: {best_alpha:.2f}")
    Best alpha: 1.50
    """
    from .adaptive_spectral_kernel import AdaptiveSpectralKernel
    
    alphas = np.linspace(alpha_range[0], alpha_range[1], n_trials)
    scores = []
    
    for alpha in alphas:
        oracle = AdaptiveSpectralKernel(alpha=alpha)
        fused, weights = oracle.fit(signals)
        
        if ground_truth is not None:
            # Lower RMSE is better
            score = -compute_rmse(fused, ground_truth)
        else:
            # Higher entropy is better (more distributed weights)
            score = compute_weight_entropy(weights)
        
        scores.append(score)
    
    best_idx = np.argmax(scores)
    return float(alphas[best_idx])


def generate_test_suite() -> Dict[str, Tuple[np.ndarray, np.ndarray]]:
    """
    Generate comprehensive test suite for benchmarking.
    
    Returns
    -------
    test_cases : dict
        Dictionary mapping test names to (signals, ground_truth) tuples
        
    Examples
    --------
    >>> from adaptive_spectral_oracle import generate_test_suite
    >>> tests = generate_test_suite()
    >>> print(tests.keys())
    dict_keys(['clean', 'light_attack', 'moderate_attack', ...])
    """
    return {
        'clean': generate_synthetic_signals(
            n_clean=7, n_poisoned=0, T=512
        ),
        'light_attack': generate_synthetic_signals(
            n_clean=9, n_poisoned=1, T=512, poison_magnitude=3.0
        ),
        'moderate_attack': generate_synthetic_signals(
            n_clean=5, n_poisoned=2, T=512, poison_magnitude=5.0
        ),
        'heavy_attack': generate_synthetic_signals(
            n_clean=5, n_poisoned=4, T=512, poison_magnitude=8.0
        ),
        'high_noise': generate_synthetic_signals(
            n_clean=7, n_poisoned=0, T=512, noise_level=0.5
        ),
        'chirp_signal': generate_synthetic_signals(
            n_clean=5, n_poisoned=2, T=512, signal_type='chirp'
        ),
    }


# Configuration helpers
DEFAULT_CONFIG = {
    'alpha': 1.5,
    'beta': 0.95,
    'lambda_jitter': 0.5,
    'method': 'median',
    'drift_threshold': 0.1,
}


def get_config_preset(preset: str) -> Dict:
    """
    Get pre-configured parameter presets.
    
    Parameters
    ----------
    preset : str
        Preset name:
        - 'default': Standard settings (most cases)
        - 'aggressive': More sensitive to outliers
        - 'conservative': More tolerant to noise
        - 'streaming': Optimized for real-time
        - 'batch': Optimized for batch processing
        
    Returns
    -------
    config : dict
        Parameter dictionary
    """
    presets = {
        'default': DEFAULT_CONFIG.copy(),
        'aggressive': {
            'alpha': 1.0,
            'beta': 0.90,
            'lambda_jitter': 1.0,
            'method': 'median',
            'drift_threshold': 0.05,
        },
        'conservative': {
            'alpha': 2.5,
            'beta': 0.98,
            'lambda_jitter': 0.2,
            'method': 'trimmed_mean',
            'drift_threshold': 0.15,
        },
        'streaming': {
            'alpha': 1.5,
            'beta': 0.95,
            'lambda_jitter': 0.5,
            'method': 'median',
            'drift_threshold': 0.1,
        },
        'batch': {
            'alpha': 1.5,
            'beta': 0.0,  # No temporal memory
            'lambda_jitter': 0.0,  # No jitter penalty
            'method': 'median',
            'drift_threshold': 0.1,
        },
    }
    
    if preset not in presets:
        raise ValueError(f"Unknown preset: {preset}. Choose from {list(presets.keys())}")
    
    return presets[preset]
