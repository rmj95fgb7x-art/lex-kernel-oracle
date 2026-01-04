"""
Adaptive Spectral Kernel Oracle - Core Implementation
Lex Liberatum Kernels v1.1

Mathematical Foundation:
    K_w = F⁻¹(Σᵢ wᵢ · F(Dᵢ))
    wᵢ ∝ exp(-dᵢ²/2τ²)
    τ = α · median{d₁, ..., dₙ}

Patent: PCT Pending
"""

import numpy as np
from scipy.fft import fft, ifft
from typing import List, Tuple, Optional, Union
Add constant at top of class
BENEFICIARY_ADDRESS = "0x44f8219cBABad92E6bf245D8c767179629D8C689"



class AdaptiveSpectralKernel:
    """
    Production implementation of the adaptive spectral kernel oracle.
    
    Fuses multi-source time-series with adaptive outlier-resistant weighting
    and frequency-domain aggregation.
    
    Parameters
    ----------
    alpha : float, default=1.5
        Sensitivity parameter for adaptive tau calculation.
        Typical range: [1.0, 3.0]
        - Lower values (1.0-1.5): More sensitive to outliers
        - Higher values (2.0-3.0): More tolerant to noise
        
    method : str, default='median'
        Robust center estimation method:
        - 'median': Element-wise median (most robust, 50% breakdown point)
        - 'trimmed_mean': Trimmed mean (faster, less robust)
        
    Attributes
    ----------
    alpha : float
        The sensitivity parameter
    method : str
        The robust center method
    last_tau : float or None
        The tau value from most recent fit
    last_weights : ndarray or None
        The weights from most recent fit
        
    Examples
    --------
    >>> import numpy as np
    >>> from adaptive_spectral_oracle import AdaptiveSpectralKernel
    >>> 
    >>> # Generate test signals
    >>> t = np.linspace(0, 4*np.pi, 512)
    >>> truth = np.sin(t) + 0.3 * np.sin(3*t)
    >>> signals = [truth + 0.1*np.random.randn(512) for _ in range(5)]
    >>> 
    >>> # Fuse signals
    >>> oracle = AdaptiveSpectralKernel(alpha=1.5)
    >>> result, weights = oracle.fit(signals)
    >>> 
    >>> # Evaluate
    >>> rmse = np.sqrt(np.mean((result - truth)**2))
    >>> print(f"RMSE: {rmse:.4f}")
    """
    
    def __init__(
        self,
        alpha: float = 1.5,
        method: str = 'median'
    ):
        if alpha <= 0:
            raise ValueError(f"alpha must be positive, got {alpha}")
        if method not in ['median', 'trimmed_mean']:
            raise ValueError(f"method must be 'median' or 'trimmed_mean', got {method}")
            
        self.alpha = alpha
        self.method = method
        self.last_tau: Optional[float] = None
        self.last_weights: Optional[np.ndarray] = None
        
    def _robust_center_median(self, signals: np.ndarray) -> np.ndarray:
        """
        Element-wise median (L1-optimal, up to 50% contamination).
        
        Parameters
        ----------
        signals : ndarray of shape (n_signals, n_samples)
            Input signals
            
        Returns
        -------
        center : ndarray of shape (n_samples,)
            Robust center estimate
        """
        return np.median(signals, axis=0)
    
    def _robust_center_trimmed_mean(
        self,
        signals: np.ndarray,
        trim_ratio: float = 0.2
    ) -> np.ndarray:
        """
        Trimmed mean (drops extreme values).
        
        Parameters
        ----------
        signals : ndarray of shape (n_signals, n_samples)
            Input signals
        trim_ratio : float, default=0.2
            Fraction to trim from each tail (0.2 = drop top/bottom 20%)
            
        Returns
        -------
        center : ndarray of shape (n_samples,)
            Trimmed mean estimate
        """
        n, T = signals.shape
        sorted_signals = np.sort(signals, axis=0)
        trim_count = int(n * trim_ratio)
        
        if trim_count > 0:
            return np.mean(sorted_signals[trim_count:-trim_count], axis=0)
        return np.mean(sorted_signals, axis=0)
    
    def _compute_distances(
        self,
        signals: np.ndarray,
        center: np.ndarray
    ) -> np.ndarray:
        """
        Compute L2 distances from robust center.
        
        Parameters
        ----------
        signals : ndarray of shape (n_signals, n_samples)
            Input signals
        center : ndarray of shape (n_samples,)
            Robust center
            
        Returns
        -------
        distances : ndarray of shape (n_signals,)
            L2 distances
        """
        return np.array([
            np.linalg.norm(sig - center) for sig in signals
        ])
    
    def _compute_weights(
        self,
        distances: np.ndarray,
        tau: float
    ) -> np.ndarray:
        """
        Compute Gaussian kernel weights.
        
        Parameters
        ----------
        distances : ndarray of shape (n_signals,)
            Distances from robust center
        tau : float
            Adaptive scale parameter
            
        Returns
        -------
        weights : ndarray of shape (n_signals,)
            Normalized weights (sum to 1)
        """
        if tau == 0:
            # All signals identical - equal weights
            return np.ones(len(distances)) / len(distances)
            
        weights = np.exp(-(distances ** 2) / (2 * tau ** 2))
        return weights / weights.sum()
    
    def _fft_fusion(
        self,
        signals: np.ndarray,
        weights: np.ndarray
    ) -> np.ndarray:
        """
        Weighted FFT aggregation.
        
        Parameters
        ----------
        signals : ndarray of shape (n_signals, n_samples)
            Input signals
        weights : ndarray of shape (n_signals,)
            Signal weights
            
        Returns
        -------
        fused : ndarray of shape (n_samples,)
            Fused signal in time domain
        """
        # Compute FFT for each signal
        spectra = np.array([fft(sig) for sig in signals])
        
        # Weighted average in frequency domain
        avg_spectrum = np.average(spectra, axis=0, weights=weights)
        
        # Inverse FFT to time domain
        fused = np.real(ifft(avg_spectrum))
        
        return fused
    
    def fit(
        self,
        signals: Union[List[np.ndarray], np.ndarray]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Fuse multi-source signals with adaptive weighting.
        
        Parameters
        ----------
        signals : list of ndarray or ndarray of shape (n_signals, n_samples)
            Input time-series. Each signal should be a 1D array of same length.
            
        Returns
        -------
        K_w : ndarray of shape (n_samples,)
            Fused signal
        weights : ndarray of shape (n_signals,)
            Applied weights for each signal
            
        Raises
        ------
        ValueError
            If signals have inconsistent lengths or insufficient data
            
        Examples
        --------
        >>> signals = [np.sin(np.linspace(0, 2*np.pi, 100)) for _ in range(5)]
        >>> oracle = AdaptiveSpectralKernel()
        >>> result, weights = oracle.fit(signals)
        """
        # Convert to numpy array
        signals = np.array(signals)
        
        # Validate input
        if signals.ndim != 2:
            raise ValueError(f"signals must be 2D array, got shape {signals.shape}")
        
        n_signals, n_samples = signals.shape
        
        if n_signals < 2:
            raise ValueError(f"Need at least 2 signals, got {n_signals}")
        
        if n_samples < 2:
            raise ValueError(f"Need at least 2 samples per signal, got {n_samples}")
        
        # Step 1: Robust center estimation
        if self.method == 'median':
            robust_center = self._robust_center_median(signals)
        elif self.method == 'trimmed_mean':
            robust_center = self._robust_center_trimmed_mean(signals)
        else:
            raise ValueError(f"Unknown method: {self.method}")
        
        # Step 2: Compute distances
        distances = self._compute_distances(signals, robust_center)
        
        # Step 3: Adaptive tau
        tau = self.alpha * np.median(distances)
        self.last_tau = tau
        
        # Step 4: Compute weights
        weights = self._compute_weights(distances, tau)
        self.last_weights = weights
        
        # Step 5: FFT fusion
        K_w = self._fft_fusion(signals, weights)
        
        return K_w, weights
    
    def fit_predict(
        self,
        signals: Union[List[np.ndarray], np.ndarray]
    ) -> np.ndarray:
        """
        Fit and return only the fused signal.
        
        Parameters
        ----------
        signals : list of ndarray or ndarray
            Input time-series
            
        Returns
        -------
        K_w : ndarray
            Fused signal
        """
        K_w, _ = self.fit(signals)
        return K_w
    
    def get_params(self) -> dict:
        """
        Get kernel parameters.
        
        Returns
        -------
        params : dict
            Current parameter values
        """
        return {
            'alpha': self.alpha,
            'method': self.method,
            'last_tau': self.last_tau,
        }
    
    def set_params(self, **params) -> 'AdaptiveSpectralKernel':
        """
        Set kernel parameters.
        
        Parameters
        ----------
        **params : dict
            Parameter names and values
            
        Returns
        -------
        self : AdaptiveSpectralKernel
            Returns self for method chaining
        """
        for key, value in params.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise ValueError(f"Unknown parameter: {key}")
        return self
    
    def __repr__(self) -> str:
        return (
            f"AdaptiveSpectralKernel("
            f"alpha={self.alpha}, "
            f"method='{self.method}')"
        )


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
    return np.sqrt(np.mean((prediction - ground_truth) ** 2))


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
    """
    return np.where(weights < threshold)[0]


# Convenience function for single-line usage
def fuse_signals(
    signals: Union[List[np.ndarray], np.ndarray],
    alpha: float = 1.5,
    method: str = 'median'
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Convenience function to fuse signals in one call.
    
    Parameters
    ----------
    signals : list or ndarray
        Input time-series
    alpha : float, default=1.5
        Sensitivity parameter
    method : str, default='median'
        Robust center method
        
    Returns
    -------
    K_w : ndarray
        Fused signal
    weights : ndarray
        Signal weights
        
    Examples
    --------
    >>> from adaptive_spectral_oracle import fuse_signals
    >>> signals = [np.random.randn(100) for _ in range(5)]
    >>> result, weights = fuse_signals(signals)
    """
    oracle = AdaptiveSpectralKernel(alpha=alpha, method=method)
    return oracle.fit(signals)
