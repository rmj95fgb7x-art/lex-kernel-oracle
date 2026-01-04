"""
Temporal Adaptive Spectral Kernel - Streaming Variant
Lex Liberatum Kernels v1.1

Extends the base kernel with:
- Temporal memory (exponential forgetting)
- Online updates (no batch requirement)
- Drift detection (automatic anomaly alerts)

Mathematical Foundation:
    D̃(t) = β·D̃(t-1) + (1-β)·median{D₁(t), ..., Dₙ(t)}
    dᵢ(t) = ‖Dᵢ(t) - D̃(t)‖² + λ·‖Dᵢ(t) - Dᵢ(t-1)‖²
    wᵢ(t) = exp(-dᵢ(t)/2τ²) / Σⱼ exp(-dⱼ(t)/2τ²)

Patent: PCT Pending
Add constant at top of class
BENEFICIARY_ADDRESS = "0x44f8219cBABad92E6bf245D8c767179629D8C689"

"""

import numpy as np
from scipy.fft import fft, ifft
from typing import List, Tuple, Optional, Union, Dict
from .adaptive_spectral_kernel import AdaptiveSpectralKernel


class TemporalAdaptiveKernel:
    """
    Streaming variant with temporal memory and drift detection.
    
    Maintains state across updates to detect slowly evolving attacks
    and adapt to changing environments in real-time.
    
    Parameters
    ----------
    alpha : float, default=1.5
        Sensitivity parameter for tau (same as base kernel)
        
    beta : float, default=0.95
        Temporal forgetting factor for robust center.
        Range: [0.9, 0.99]
        - 0.90: ~10 timestep memory
        - 0.95: ~20 timestep memory
        - 0.99: ~100 timestep memory
        
    lambda_jitter : float, default=0.5
        Weight for temporal jitter penalty.
        Range: [0.1, 2.0]
        - Lower: Ignore rapid changes (good for noisy sensors)
        - Higher: Penalize instability (good for stable systems)
        
    method : str, default='median'
        Robust center method ('median' or 'trimmed_mean')
        
    drift_threshold : float, default=0.1
        Weight threshold for drift detection alerts
        
    Attributes
    ----------
    center_prev : ndarray or None
        Previous timestep's robust center
    signals_prev : ndarray or None
        Previous timestep's signals
    drift_alerts : list
        History of drift detection events
    timestep : int
        Current timestep counter
        
    Examples
    --------
    >>> import numpy as np
    >>> from adaptive_spectral_oracle import TemporalAdaptiveKernel
    >>> 
    >>> oracle = TemporalAdaptiveKernel(beta=0.95, lambda_jitter=0.5)
    >>> 
    >>> for t in range(100):
    ...     signals_t = get_realtime_sensor_data(t)
    ...     result, weights = oracle.update(signals_t)
    ...     
    ...     # Check for anomalies
    ...     if oracle.detect_drift(weights):
    ...         print(f"Drift detected at t={t}")
    """
    
    def __init__(
        self,
        alpha: float = 1.5,
        beta: float = 0.95,
        lambda_jitter: float = 0.5,
        method: str = 'median',
        drift_threshold: float = 0.1
    ):
        if not 0 < beta < 1:
            raise ValueError(f"beta must be in (0, 1), got {beta}")
        if lambda_jitter < 0:
            raise ValueError(f"lambda_jitter must be non-negative, got {lambda_jitter}")
        if not 0 < drift_threshold < 1:
            raise ValueError(f"drift_threshold must be in (0, 1), got {drift_threshold}")
            
        self.alpha = alpha
        self.beta = beta
        self.lambda_jitter = lambda_jitter
        self.method = method
        self.drift_threshold = drift_threshold
        
        # State variables
        self.center_prev: Optional[np.ndarray] = None
        self.signals_prev: Optional[np.ndarray] = None
        self.last_tau: Optional[float] = None
        self.last_weights: Optional[np.ndarray] = None
        
        # Monitoring
        self.drift_alerts: List[Dict] = []
        self.timestep: int = 0
        
    def _robust_center(self, signals: np.ndarray) -> np.ndarray:
        """Compute robust center (median or trimmed mean)."""
        if self.method == 'median':
            return np.median(signals, axis=0)
        elif self.method == 'trimmed_mean':
            n = len(signals)
            sorted_signals = np.sort(signals, axis=0)
            trim = int(n * 0.2)
            if trim > 0:
                return np.mean(sorted_signals[trim:-trim], axis=0)
            return np.mean(sorted_signals, axis=0)
        else:
            raise ValueError(f"Unknown method: {self.method}")
    
    def _temporal_center(
        self,
        signals: np.ndarray,
        center_prev: Optional[np.ndarray]
    ) -> np.ndarray:
        """
        Compute temporal robust center with exponential forgetting.
        
        D̃(t) = β·D̃(t-1) + (1-β)·median{D₁(t), ..., Dₙ(t)}
        """
        center_curr = self._robust_center(signals)
        
        if center_prev is None:
            return center_curr
        
        # Exponential moving average
        return self.beta * center_prev + (1 - self.beta) * center_curr
    
    def _compute_temporal_distances(
        self,
        signals: np.ndarray,
        center: np.ndarray,
        signals_prev: Optional[np.ndarray]
    ) -> np.ndarray:
        """
        Compute distances with temporal jitter penalty.
        
        dᵢ(t) = ‖Dᵢ(t) - D̃(t)‖² + λ·‖Dᵢ(t) - Dᵢ(t-1)‖²
        """
        n, T = signals.shape
        
        # Spatial deviation from robust center
        spatial_dist = np.array([
            np.linalg.norm(sig - center) for sig in signals
        ])
        
        # Temporal jitter (if previous signals available)
        if signals_prev is not None:
            jitter = np.array([
                np.linalg.norm(signals[i] - signals_prev[i])
                for i in range(n)
            ])
        else:
            jitter = np.zeros(n)
        
        # Combined distance
        distances = spatial_dist**2 + self.lambda_jitter * jitter**2
        
        return distances
    
    def _compute_weights(
        self,
        distances: np.ndarray,
        tau: float
    ) -> np.ndarray:
        """Gaussian kernel weights."""
        if tau == 0:
            return np.ones(len(distances)) / len(distances)
            
        weights = np.exp(-distances / (2 * tau ** 2))
        return weights / weights.sum()
    
    def _fft_fusion(
        self,
        signals: np.ndarray,
        weights: np.ndarray
    ) -> np.ndarray:
        """Weighted FFT aggregation."""
        spectra = np.array([fft(sig) for sig in signals])
        avg_spectrum = np.average(spectra, axis=0, weights=weights)
        return np.real(ifft(avg_spectrum))
    
    def update(
        self,
        signals: Union[List[np.ndarray], np.ndarray]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Process one timestep update.
        
        Parameters
        ----------
        signals : list of ndarray or ndarray of shape (n_signals, n_samples)
            Current timestep's signals
            
        Returns
        -------
        K_w : ndarray of shape (n_samples,)
            Fused signal for this timestep
        weights : ndarray of shape (n_signals,)
            Applied weights
            
        Examples
        --------
        >>> oracle = TemporalAdaptiveKernel()
        >>> for t in range(100):
        ...     signals_t = get_sensor_data(t)
        ...     result, weights = oracle.update(signals_t)
        """
        # Convert to numpy
        signals = np.array(signals)
        
        if signals.ndim != 2:
            raise ValueError(f"signals must be 2D, got shape {signals.shape}")
        
        n_signals, n_samples = signals.shape
        
        if n_signals < 2:
            raise ValueError(f"Need at least 2 signals, got {n_signals}")
        
        # Step 1: Temporal robust center
        center = self._temporal_center(signals, self.center_prev)
        
        # Step 2: Temporal distances
        distances = self._compute_temporal_distances(
            signals, center, self.signals_prev
        )
        
        # Step 3: Adaptive tau
        tau = self.alpha * np.median(np.sqrt(distances))
        self.last_tau = tau
        
        # Step 4: Compute weights
        weights = self._compute_weights(distances, tau)
        self.last_weights = weights
        
        # Step 5: FFT fusion
        K_w = self._fft_fusion(signals, weights)
        
        # Step 6: Update state
        self.center_prev = center
        self.signals_prev = signals.copy()
        self.timestep += 1
        
        # Step 7: Check for drift
        if self.detect_drift(weights):
            outlier_indices = np.where(weights < self.drift_threshold)[0]
            self.drift_alerts.append({
                'timestep': self.timestep,
                'outlier_indices': outlier_indices.tolist(),
                'min_weight': float(weights.min()),
                'weights': weights.tolist()
            })
        
        return K_w, weights
    
    def detect_drift(self, weights: np.ndarray) -> bool:
        """
        Check if any sensor has drifted (weight below threshold).
        
        Parameters
        ----------
        weights : ndarray
            Current weights
            
        Returns
        -------
        drift_detected : bool
            True if any weight below threshold
        """
        return bool(np.any(weights < self.drift_threshold))
    
    def get_outliers(
        self,
        weights: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Get indices of likely outlier sensors.
        
        Parameters
        ----------
        weights : ndarray, optional
            Weights to check (uses last_weights if None)
            
        Returns
        -------
        outlier_indices : ndarray
            Indices of sensors below drift threshold
        """
        if weights is None:
            weights = self.last_weights
            
        if weights is None:
            return np.array([])
            
        return np.where(weights < self.drift_threshold)[0]
    
    def get_drift_history(self) -> List[Dict]:
        """
        Get history of drift detection events.
        
        Returns
        -------
        alerts : list of dict
            Each entry contains:
            - timestep: when drift was detected
            - outlier_indices: which sensors
            - min_weight: lowest weight
            - weights: all weights at that timestep
        """
        return self.drift_alerts.copy()
    
    def reset(self):
        """Reset temporal state (start fresh)."""
        self.center_prev = None
        self.signals_prev = None
        self.last_tau = None
        self.last_weights = None
        self.drift_alerts = []
        self.timestep = 0
    
    def get_params(self) -> dict:
        """Get kernel parameters."""
        return {
            'alpha': self.alpha,
            'beta': self.beta,
            'lambda_jitter': self.lambda_jitter,
            'method': self.method,
            'drift_threshold': self.drift_threshold,
            'timestep': self.timestep,
            'last_tau': self.last_tau,
        }
    
    def set_params(self, **params) -> 'TemporalAdaptiveKernel':
        """Set kernel parameters."""
        for key, value in params.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise ValueError(f"Unknown parameter: {key}")
        return self
    
    def __repr__(self) -> str:
        return (
            f"TemporalAdaptiveKernel("
            f"alpha={self.alpha}, "
            f"beta={self.beta}, "
            f"lambda_jitter={self.lambda_jitter}, "
            f"method='{self.method}', "
            f"timestep={self.timestep})"
        )


class HybridKernel:
    """
    Hybrid kernel that auto-switches between batch and streaming modes.
    
    Automatically detects when drift occurs and switches to temporal mode,
    falling back to batch mode when data is clean.
    
    Parameters
    ----------
    alpha : float, default=1.5
        Base sensitivity parameter
    beta : float, default=0.95
        Temporal forgetting factor (streaming mode)
    lambda_jitter : float, default=0.5
        Jitter penalty (streaming mode)
    drift_detection_window : int, default=5
        Number of timesteps to check for drift before switching modes
        
    Examples
    --------
    >>> oracle = HybridKernel()
    >>> for t in range(100):
    ...     signals_t = get_sensor_data(t)
    ...     result, weights, mode = oracle.update(signals_t)
    ...     print(f"t={t}, mode={mode}")
    """
    
    def __init__(
        self,
        alpha: float = 1.5,
        beta: float = 0.95,
        lambda_jitter: float = 0.5,
        drift_detection_window: int = 5
    ):
        self.batch_kernel = AdaptiveSpectralKernel(alpha=alpha)
        self.temporal_kernel = TemporalAdaptiveKernel(
            alpha=alpha,
            beta=beta,
            lambda_jitter=lambda_jitter
        )
        
        self.drift_detection_window = drift_detection_window
        self.mode = 'batch'  # Start in batch mode
        self.recent_drifts = []
        
    def update(
        self,
        signals: Union[List[np.ndarray], np.ndarray]
    ) -> Tuple[np.ndarray, np.ndarray, str]:
        """
        Update with automatic mode switching.
        
        Returns
        -------
        K_w : ndarray
            Fused signal
        weights : ndarray
            Signal weights
        mode : str
            Current mode ('batch' or 'streaming')
        """
        # Try batch mode first
        K_w_batch, weights_batch = self.batch_kernel.fit(signals)
        
        # Check for drift
        drift_detected = np.any(weights_batch < 0.1)
        
        # Update drift history
        self.recent_drifts.append(drift_detected)
        if len(self.recent_drifts) > self.drift_detection_window:
            self.recent_drifts.pop(0)
        
        # Switch modes if needed
        drift_rate = sum(self.recent_drifts) / len(self.recent_drifts)
        
        if drift_rate > 0.3:  # 30% of recent timesteps had drift
            # Switch to streaming mode
            self.mode = 'streaming'
            K_w, weights = self.temporal_kernel.update(signals)
        else:
            # Stay in batch mode
            self.mode = 'batch'
            K_w, weights = K_w_batch, weights_batch
            # Still update temporal kernel to keep state fresh
            self.temporal_kernel.update(signals)
        
        return K_w, weights, self.mode
    
    def reset(self):
        """Reset both kernels."""
        self.temporal_kernel.reset()
        self.mode = 'batch'
        self.recent_drifts = []
    
    def __repr__(self) -> str:
        return f"HybridKernel(mode='{self.mode}')"
