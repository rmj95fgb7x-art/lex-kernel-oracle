"""
Unit Tests for Adaptive Spectral Kernel Oracle
Lex Liberatum Kernels v1.1

Test Coverage:
- Core kernel functionality
- Temporal streaming kernel
- Hybrid mode switching
- Edge cases and error handling
- Mathematical properties

Run with: pytest tests/test_kernels.py -v
"""

import pytest
import numpy as np
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.adaptive_spectral_kernel import AdaptiveSpectralKernel, compute_rmse, detect_outliers, fuse_signals
from src.temporal_kernel import TemporalAdaptiveKernel, HybridKernel
from src.utils import (
    generate_synthetic_signals,
    generate_drift_attack,
    compute_all_metrics,
    auto_tune_alpha,
    get_config_preset
)


class TestAdaptiveSpectralKernel:
    """Test suite for base adaptive kernel."""
    
    def test_initialization(self):
        """Test kernel initialization with valid parameters."""
        kernel = AdaptiveSpectralKernel(alpha=1.5, method='median')
        assert kernel.alpha == 1.5
        assert kernel.method == 'median'
        assert kernel.last_tau is None
        assert kernel.last_weights is None
    
    def test_invalid_alpha(self):
        """Test that invalid alpha raises ValueError."""
        with pytest.raises(ValueError):
            AdaptiveSpectralKernel(alpha=0)
        with pytest.raises(ValueError):
            AdaptiveSpectralKernel(alpha=-1.5)
    
    def test_invalid_method(self):
        """Test that invalid method raises ValueError."""
        with pytest.raises(ValueError):
            AdaptiveSpectralKernel(method='unknown')
    
    def test_basic_fusion(self):
        """Test basic signal fusion."""
        # Generate clean signals
        signals, truth = generate_synthetic_signals(
            n_clean=5, n_poisoned=0, T=128
        )
        
        kernel = AdaptiveSpectralKernel(alpha=1.5)
        result, weights = kernel.fit(signals)
        
        # Check output shapes
        assert result.shape == truth.shape
        assert weights.shape == (5,)
        
        # Check weights sum to 1
        assert np.allclose(weights.sum(), 1.0)
        
        # Check all weights positive
        assert np.all(weights >= 0)
        
        # Check RMSE is reasonable
        rmse = compute_rmse(result, truth)
        assert rmse < 0.2  # Should be good on clean data
    
    def test_adversarial_robustness(self):
        """Test robustness to poisoned sensors."""
        # Generate with adversarial sensors
        signals, truth = generate_synthetic_signals(
            n_clean=5, n_poisoned=2, T=128, poison_magnitude=5.0
        )
        
        kernel = AdaptiveSpectralKernel(alpha=1.5)
        result, weights = kernel.fit(signals)
        
        # Poisoned sensors should have low weights
        poisoned_weights = weights[5:]  # Last 2 are poisoned
        clean_weights = weights[:5]
        
        assert np.mean(poisoned_weights) < np.mean(clean_weights)
        assert np.max(poisoned_weights) < 0.2  # Should be heavily downweighted
    
    def test_weight_concentration(self):
        """Test that weights concentrate on good sensors."""
        signals, truth = generate_synthetic_signals(
            n_clean=3, n_poisoned=1, T=128, poison_magnitude=8.0
        )
        
        kernel = AdaptiveSpectralKernel(alpha=1.5)
        result, weights = kernel.fit(signals)
        
        # Clean sensors should have most of the weight
        clean_weight_sum = weights[:3].sum()
        assert clean_weight_sum > 0.9  # At least 90% weight on clean
    
    def test_trimmed_mean_method(self):
        """Test trimmed mean robust center."""
        signals, truth = generate_synthetic_signals(
            n_clean=5, n_poisoned=2, T=128
        )
        
        kernel = AdaptiveSpectralKernel(alpha=1.5, method='trimmed_mean')
        result, weights = kernel.fit(signals)
        
        assert result.shape == truth.shape
        assert np.allclose(weights.sum(), 1.0)
    
    def test_tau_computation(self):
        """Test adaptive tau computation."""
        signals, _ = generate_synthetic_signals(n_clean=5, n_poisoned=0, T=128)
        
        kernel = AdaptiveSpectralKernel(alpha=1.5)
        kernel.fit(signals)
        
        assert kernel.last_tau is not None
        assert kernel.last_tau > 0
    
    def test_edge_case_identical_signals(self):
        """Test behavior with identical signals."""
        T = 128
        signal = np.sin(np.linspace(0, 2*np.pi, T))
        signals = np.array([signal] * 5)
        
        kernel = AdaptiveSpectralKernel(alpha=1.5)
        result, weights = kernel.fit(signals)
        
        # Should assign equal weights when all identical
        assert np.allclose(weights, 0.2, atol=0.01)
        assert np.allclose(result, signal, atol=1e-10)
    
    def test_edge_case_single_outlier(self):
        """Test with single extreme outlier."""
        T = 128
        truth = np.sin(np.linspace(0, 2*np.pi, T))
        
        signals = []
        for _ in range(4):
            signals.append(truth + 0.01*np.random.randn(T))
        signals.append(truth + 100.0)  # Extreme outlier
        
        signals = np.array(signals)
        
        kernel = AdaptiveSpectralKernel(alpha=1.5)
        result, weights = kernel.fit(signals)
        
        # Outlier should be almost completely ignored
        assert weights[4] < 0.001
    
    def test_fit_predict(self):
        """Test fit_predict convenience method."""
        signals, truth = generate_synthetic_signals(n_clean=5, n_poisoned=0, T=128)
        
        kernel = AdaptiveSpectralKernel(alpha=1.5)
        result = kernel.fit_predict(signals)
        
        assert result.shape == truth.shape
    
    def test_get_set_params(self):
        """Test parameter getter/setter."""
        kernel = AdaptiveSpectralKernel(alpha=1.5)
        
        params = kernel.get_params()
        assert params['alpha'] == 1.5
        
        kernel.set_params(alpha=2.0)
        assert kernel.alpha == 2.0
    
    def test_invalid_input_shapes(self):
        """Test error handling for invalid inputs."""
        kernel = AdaptiveSpectralKernel()
        
        # 1D array (should be 2D)
        with pytest.raises(ValueError):
            kernel.fit(np.array([1, 2, 3]))
        
        # Single signal
        with pytest.raises(ValueError):
            kernel.fit(np.array([[1, 2, 3]]))
        
        # Empty signals
        with pytest.raises(ValueError):
            kernel.fit(np.array([[], []]))


class TestTemporalKernel:
    """Test suite for temporal streaming kernel."""
    
    def test_initialization(self):
        """Test temporal kernel initialization."""
        kernel = TemporalAdaptiveKernel(
            alpha=1.5,
            beta=0.95,
            lambda_jitter=0.5
        )
        
        assert kernel.alpha == 1.5
        assert kernel.beta == 0.95
        assert kernel.lambda_jitter == 0.5
        assert kernel.timestep == 0
        assert kernel.center_prev is None
    
    def test_invalid_beta(self):
        """Test invalid beta values."""
        with pytest.raises(ValueError):
            TemporalAdaptiveKernel(beta=0)
        with pytest.raises(ValueError):
            TemporalAdaptiveKernel(beta=1.0)
        with pytest.raises(ValueError):
            TemporalAdaptiveKernel(beta=-0.5)
    
    def test_streaming_updates(self):
        """Test sequential streaming updates."""
        kernel = TemporalAdaptiveKernel(alpha=1.5, beta=0.95)
        
        for t in range(10):
            signals, _ = generate_synthetic_signals(
                n_clean=5, n_poisoned=0, T=128
            )
            result, weights = kernel.update(signals)
            
            assert result.shape == (128,)
            assert weights.shape == (5,)
            assert kernel.timestep == t + 1
    
    def test_drift_detection(self):
        """Test drift detection functionality."""
        signals_list, truth = generate_drift_attack(
            n_clean=5,
            n_drifting=1,
            T=128,
            n_timesteps=50,
            drift_rate=0.1
        )
        
        kernel = TemporalAdaptiveKernel(alpha=1.5, beta=0.95, drift_threshold=0.1)
        
        drift_detected = False
        detection_time = None
        
        for t, signals_t in enumerate(signals_list):
            result, weights = kernel.update(signals_t)
            
            if kernel.detect_drift(weights) and not drift_detected:
                drift_detected = True
                detection_time = t
        
        # Should detect drift at some point
        assert drift_detected
        assert detection_time is not None
        assert detection_time < 40  # Should detect within 40 timesteps
    
    def test_outlier_detection(self):
        """Test outlier detection."""
        signals, _ = generate_synthetic_signals(
            n_clean=5, n_poisoned=2, T=128, poison_magnitude=5.0
        )
        
        kernel = TemporalAdaptiveKernel(alpha=1.5, drift_threshold=0.1)
        result, weights = kernel.update(signals)
        
        outliers = kernel.get_outliers(weights)
        
        # Should detect the 2 poisoned sensors
        assert len(outliers) >= 1  # At least one detected
    
    def test_drift_history(self):
        """Test drift history tracking."""
        kernel = TemporalAdaptiveKernel(alpha=1.5, drift_threshold=0.1)
        
        # Generate signals with drift
        signals_list, _ = generate_drift_attack(
            n_clean=3, n_drifting=1, T=128, n_timesteps=20
        )
        
        for signals_t in signals_list:
            kernel.update(signals_t)
        
        history = kernel.get_drift_history()
        
        # Should have some drift events
        assert len(history) > 0
        
        # Check history structure
        for event in history:
            assert 'timestep' in event
            assert 'outlier_indices' in event
            assert 'min_weight' in event
    
    def test_reset(self):
        """Test state reset."""
        kernel = TemporalAdaptiveKernel(alpha=1.5)
        
        # Run some updates
        for _ in range(5):
            signals, _ = generate_synthetic_signals(n_clean=3, n_poisoned=0, T=128)
            kernel.update(signals)
        
        assert kernel.timestep == 5
        assert kernel.center_prev is not None
        
        # Reset
        kernel.reset()
        
        assert kernel.timestep == 0
        assert kernel.center_prev is None
        assert len(kernel.drift_alerts) == 0
    
    def test_temporal_memory(self):
        """Test that temporal center uses past information."""
        kernel = TemporalAdaptiveKernel(alpha=1.5, beta=0.95)
        
        # First update
        signals1, _ = generate_synthetic_signals(n_clean=3, n_poisoned=0, T=128)
        kernel.update(signals1)
        
        center_after_first = kernel.center_prev.copy()
        
        # Second update with different data
        signals2, _ = generate_synthetic_signals(n_clean=3, n_poisoned=0, T=128)
        kernel.update(signals2)
        
        # Center should be different but influenced by first
        assert not np.allclose(kernel.center_prev, center_after_first)


class TestHybridKernel:
    """Test suite for hybrid kernel."""
    
    def test_initialization(self):
        """Test hybrid kernel initialization."""
        kernel = HybridKernel(alpha=1.5, beta=0.95)
        
        assert kernel.mode == 'batch'
        assert len(kernel.recent_drifts) == 0
    
    def test_mode_switching(self):
        """Test automatic mode switching."""
        kernel = HybridKernel(alpha=1.5, drift_detection_window=5)
        
        # Start with clean data (should stay in batch)
        for _ in range(5):
            signals, _ = generate_synthetic_signals(n_clean=5, n_poisoned=0, T=128)
            result, weights, mode = kernel.update(signals)
            
        assert mode == 'batch'
        
        # Switch to heavily contaminated data
        for _ in range(10):
            signals, _ = generate_synthetic_signals(
                n_clean=3, n_poisoned=3, T=128, poison_magnitude=8.0
            )
            result, weights, mode = kernel.update(signals)
        
        # Should eventually switch to streaming
        assert mode == 'streaming'
    
    def test_reset(self):
        """Test hybrid kernel reset."""
        kernel = HybridKernel()
        
        # Run updates
        for _ in range(5):
            signals, _ = generate_synthetic_signals(n_clean=3, n_poisoned=2, T=128)
            kernel.update(signals)
        
        # Reset
        kernel.reset()
        
        assert kernel.mode == 'batch'
        assert len(kernel.recent_drifts) == 0


class TestUtilityFunctions:
    """Test suite for utility functions."""
    
    def test_compute_rmse(self):
        """Test RMSE computation."""
        pred = np.array([1.0, 2.0, 3.0])
        truth = np.array([1.1, 2.1, 2.9])
        
        rmse = compute_rmse(pred, truth)
        expected = np.sqrt(np.mean([0.01, 0.01, 0.01]))
        
        assert np.isclose(rmse, expected)
    
    def test_detect_outliers(self):
        """Test outlier detection utility."""
        weights = np.array([0.3, 0.3, 0.35, 0.05])
        outliers = detect_outliers(weights, threshold=0.1)
        
        assert len(outliers) == 1
        assert outliers[0] == 3
    
    def test_fuse_signals_convenience(self):
        """Test convenience fuse_signals function."""
        signals, truth = generate_synthetic_signals(n_clean=5, n_poisoned=0, T=128)
        
        result, weights = fuse_signals(signals, alpha=1.5)
        
        assert result.shape == truth.shape
        assert weights.shape == (5,)
    
    def test_auto_tune_alpha(self):
        """Test alpha auto-tuning."""
        signals, truth = generate_synthetic_signals(n_clean=5, n_poisoned=2, T=128)
        
        best_alpha = auto_tune_alpha(signals, truth, n_trials=5)
        
        assert 1.0 <= best_alpha <= 3.0
    
    def test_config_presets(self):
        """Test configuration presets."""
        presets = ['default', 'aggressive', 'conservative', 'streaming', 'batch']
        
        for preset in presets:
            config = get_config_preset(preset)
            
            assert 'alpha' in config
            assert 'beta' in config
            assert 'lambda_jitter' in config
    
    def test_invalid_preset(self):
        """Test invalid preset raises error."""
        with pytest.raises(ValueError):
            get_config_preset('unknown_preset')


class TestMathematicalProperties:
    """Test mathematical properties and invariants."""
    
    def test_weight_normalization(self):
        """Test that weights always sum to 1."""
        for _ in range(10):
            signals, _ = generate_synthetic_signals(
                n_clean=np.random.randint(3, 10),
                n_poisoned=np.random.randint(0, 5),
                T=128
            )
            
            kernel = AdaptiveSpectralKernel(alpha=1.5)
            _, weights = kernel.fit(signals)
            
            assert np.allclose(weights.sum(), 1.0)
    
    def test_weight_positivity(self):
        """Test that all weights are non-negative."""
        signals, _ = generate_synthetic_signals(n_clean=5, n_poisoned=2, T=128)
        
        kernel = AdaptiveSpectralKernel(alpha=1.5)
        _, weights = kernel.fit(signals)
        
        assert np.all(weights >= 0)
    
    def test_determinism(self):
        """Test that results are deterministic."""
        signals, _ = generate_synthetic_signals(n_clean=5, n_poisoned=0, T=128)
        
        kernel1 = AdaptiveSpectralKernel(alpha=1.5)
        kernel2 = AdaptiveSpectralKernel(alpha=1.5)
        
        result1, weights1 = kernel1.fit(signals)
        result2, weights2 = kernel2.fit(signals)
        
        assert np.allclose(result1, result2)
        assert np.allclose(weights1, weights2)
    
    def test_scale_invariance(self):
        """Test behavior under signal scaling."""
        signals, truth = generate_synthetic_signals(n_clean=5, n_poisoned=0, T=128)
        
        kernel = AdaptiveSpectralKernel(alpha=1.5)
        
        # Original
        result1, weights1 = kernel.fit(signals)
        
        # Scaled by 10
        result2, weights2 = kernel.fit(signals * 10)
        
        # Weights should be similar (scale-invariant weighting)
        assert np.allclose(weights1, weights2, atol=0.01)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
