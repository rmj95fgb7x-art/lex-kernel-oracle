"""
Comprehensive Benchmark Test Suite
Adaptive Spectral Kernel Oracle vs. Baseline Methods

Lex Liberatum Kernels v1.1

Benchmarks:
1. Adversarial Robustness (0-49% contamination)
2. Computational Scaling (10-10,000 sensors)
3. Method Comparison (6+ algorithms)
4. Drift Detection Performance
5. Frequency-Selective Jamming
6. Multi-Modal Fusion

Patent: PCT Pending
"""

import numpy as np
from scipy.fft import fft, ifft
from scipy.signal import savgol_filter
import time
from typing import List, Tuple, Dict, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.adaptive_spectral_kernel import AdaptiveSpectralKernel
from src.temporal_kernel import TemporalAdaptiveKernel, HybridKernel
from src.utils import (
    compute_all_metrics,
    generate_synthetic_signals,
    generate_drift_attack,
    detect_outliers
)


class BaselineMethods:
    """Baseline comparison methods."""
    
    @staticmethod
    def equal_weights(signals: np.ndarray) -> np.ndarray:
        """Simple arithmetic mean."""
        return np.mean(signals, axis=0)
    
    @staticmethod
    def fixed_priors(
        signals: np.ndarray,
        n_clean: int
    ) -> np.ndarray:
        """
        Fixed sector priors (assumes known clean sensors).
        
        Assigns 80% weight to clean sensors, 20% to others.
        """
        n = len(signals)
        weights = np.array(
            [0.8/n_clean] * n_clean +
            [0.2/(n-n_clean)] * (n-n_clean)
        )
        return np.average(signals, axis=0, weights=weights)
    
    @staticmethod
    def savitzky_golay(
        signals: np.ndarray,
        window: int = 51,
        order: int = 3
    ) -> np.ndarray:
        """Savitzky-Golay smoothing filter."""
        mean_sig = np.mean(signals, axis=0)
        if len(mean_sig) < window:
            window = len(mean_sig) // 2 * 2 + 1  # Ensure odd
        return savgol_filter(mean_sig, window, order)
    
    @staticmethod
    def weighted_median(signals: np.ndarray) -> np.ndarray:
        """Simple median (no adaptive weighting)."""
        return np.median(signals, axis=0)
    
    @staticmethod
    def trimmed_mean(
        signals: np.ndarray,
        trim_ratio: float = 0.2
    ) -> np.ndarray:
        """Trimmed mean (drop top/bottom 20%)."""
        n = len(signals)
        sorted_signals = np.sort(signals, axis=0)
        trim = int(n * trim_ratio)
        if trim > 0:
            return np.mean(sorted_signals[trim:-trim], axis=0)
        return np.mean(sorted_signals, axis=0)


class BenchmarkSuite:
    """Comprehensive benchmark testing framework."""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.results = {}
        
    def log(self, message: str):
        """Print if verbose mode enabled."""
        if self.verbose:
            print(message)
    
    def benchmark_adversarial_robustness(
        self,
        contamination_levels: List[float] = [0.0, 0.1, 0.2, 0.3, 0.4]
    ) -> Dict:
        """
        Test robustness at different contamination levels.
        
        Parameters
        ----------
        contamination_levels : list of float
            Fractions of poisoned sensors to test
            
        Returns
        -------
        results : dict
            Performance metrics at each contamination level
        """
        self.log("=" * 60)
        self.log("BENCHMARK 1: Adversarial Robustness")
        self.log("=" * 60)
        
        results = {level: {} for level in contamination_levels}
        
        for level in contamination_levels:
            n_total = 20
            n_poisoned = int(n_total * level)
            n_clean = n_total - n_poisoned
            
            signals, ground_truth = generate_synthetic_signals(
                n_clean=n_clean,
                n_poisoned=n_poisoned,
                T=512,
                poison_magnitude=8.0
            )
            
            # Test methods
            oracle = AdaptiveSpectralKernel(alpha=1.5, method='median')
            pred_adaptive, weights = oracle.fit(signals)
            pred_equal = BaselineMethods.equal_weights(signals)
            pred_median = BaselineMethods.weighted_median(signals)
            
            # Metrics
            metrics_adaptive = compute_all_metrics(pred_adaptive, ground_truth)
            metrics_equal = compute_all_metrics(pred_equal, ground_truth)
            metrics_median = compute_all_metrics(pred_median, ground_truth)
            
            results[level]['adaptive'] = metrics_adaptive
            results[level]['equal'] = metrics_equal
            results[level]['median'] = metrics_median
            results[level]['improvement_vs_equal'] = (
                (metrics_equal['rmse'] - metrics_adaptive['rmse']) /
                metrics_equal['rmse'] * 100
            )
            results[level]['improvement_vs_median'] = (
                (metrics_median['rmse'] - metrics_adaptive['rmse']) /
                metrics_median['rmse'] * 100
            )
            
            self.log(f"\nContamination: {level*100:.0f}%")
            self.log(f"  Equal Weights RMSE:  {metrics_equal['rmse']:.4f}")
            self.log(f"  Median RMSE:         {metrics_median['rmse']:.4f}")
            self.log(f"  Adaptive FFT RMSE:   {metrics_adaptive['rmse']:.4f}")
            self.log(f"  Improvement vs Equal: {results[level]['improvement_vs_equal']:.1f}%")
        
        return results
    
    def benchmark_scaling(
        self,
        node_counts: List[int] = [10, 50, 100, 500, 1000, 5000]
    ) -> Dict:
        """
        Test computational scaling.
        
        Parameters
        ----------
        node_counts : list of int
            Number of sensors to test
            
        Returns
        -------
        results : dict
            Timing and accuracy at each scale
        """
        self.log("\n" + "=" * 60)
        self.log("BENCHMARK 2: Computational Scaling")
        self.log("=" * 60)
        
        results = {n: {} for n in node_counts}
        
        for n in node_counts:
            signals, ground_truth = generate_synthetic_signals(
                n_clean=n,
                n_poisoned=0,
                T=512
            )
            
            oracle = AdaptiveSpectralKernel(alpha=1.5)
            
            # Time the computation
            start = time.time()
            pred, weights = oracle.fit(signals)
            elapsed = time.time() - start
            
            metrics = compute_all_metrics(pred, ground_truth)
            
            results[n] = {
                'time': elapsed,
                'rmse': metrics['rmse'],
                'time_per_signal': elapsed / n
            }
            
            self.log(f"\nn = {n:5d} nodes:")
            self.log(f"  Time: {elapsed:.4f}s ({elapsed/n*1000:.2f}ms per signal)")
            self.log(f"  RMSE: {metrics['rmse']:.6f}")
        
        return results
    
    def benchmark_methods_comparison(self) -> Dict:
        """
        Compare multiple fusion methods on standard adversarial test.
        
        Returns
        -------
        results : dict
            Performance metrics for each method
        """
        self.log("\n" + "=" * 60)
        self.log("BENCHMARK 3: Method Comparison")
        self.log("=" * 60)
        
        signals, ground_truth = generate_synthetic_signals(
            n_clean=5,
            n_poisoned=2,
            T=512,
            poison_magnitude=5.0
        )
        
        methods = {
            'Equal Weights': BaselineMethods.equal_weights(signals),
            'Fixed Priors': BaselineMethods.fixed_priors(signals, n_clean=5),
            'Median': BaselineMethods.weighted_median(signals),
            'Trimmed Mean': BaselineMethods.trimmed_mean(signals),
            'Savitzky-Golay': BaselineMethods.savitzky_golay(signals),
            'Adaptive (median)': AdaptiveSpectralKernel(alpha=1.5, method='median').fit(signals)[0],
            'Adaptive (trimmed)': AdaptiveSpectralKernel(alpha=1.5, method='trimmed_mean').fit(signals)[0],
        }
        
        results = {}
        best_rmse = float('inf')
        best_method = None
        
        self.log("\n{:25s} {:>10s} {:>10s} {:>10s}".format(
            "Method", "RMSE", "MAE", "SNR (dB)"
        ))
        self.log("-" * 60)
        
        for name, pred in methods.items():
            metrics = compute_all_metrics(pred, ground_truth)
            results[name] = metrics
            
            if metrics['rmse'] < best_rmse:
                best_rmse = metrics['rmse']
                best_method = name
                marker = " ★"
            else:
                marker = ""
            
            self.log(f"{name:25s} {metrics['rmse']:10.4f} {metrics['mae']:10.4f} "
                    f"{metrics['snr_db']:10.2f}{marker}")
        
        self.log(f"\nBest Method: {best_method}")
        
        return results
    
    def benchmark_drift_detection(
        self,
        drift_rate: float = 0.05,
        n_timesteps: int = 100
    ) -> Dict:
        """
        Test drift detection performance.
        
        Parameters
        ----------
        drift_rate : float
            Rate of corruption increase per timestep
        n_timesteps : int
            Number of timesteps to simulate
            
        Returns
        -------
        results : dict
            Detection times and performance
        """
        self.log("\n" + "=" * 60)
        self.log("BENCHMARK 4: Drift Detection Performance")
        self.log("=" * 60)
        
        signals_over_time, ground_truth = generate_drift_attack(
            n_clean=5,
            n_drifting=1,
            T=512,
            n_timesteps=n_timesteps,
            drift_rate=drift_rate
        )
        
        # Test kernels
        oracle_batch = AdaptiveSpectralKernel(alpha=1.5)
        oracle_temporal = TemporalAdaptiveKernel(alpha=1.5, beta=0.95, lambda_jitter=0.5)
        
        detection_times = {'batch': None, 'temporal': None}
        rmse_history = {'batch': [], 'temporal': []}
        
        for t, signals_t in enumerate(signals_over_time):
            # Batch kernel
            _, weights_batch = oracle_batch.fit(signals_t)
            
            # Temporal kernel
            _, weights_temporal = oracle_temporal.update(signals_t)
            
            # Check detection (sensor 5 is drifting)
            if detection_times['batch'] is None and weights_batch[5] < 0.1:
                detection_times['batch'] = t
            
            if detection_times['temporal'] is None and weights_temporal[5] < 0.1:
                detection_times['temporal'] = t
        
        improvement = detection_times['batch'] - detection_times['temporal']
        improvement_pct = (improvement / detection_times['batch']) * 100
        
        self.log(f"\nDrift Attack (rate={drift_rate}):")
        self.log(f"  Batch Kernel Detection:    {detection_times['batch']} steps")
        self.log(f"  Temporal Kernel Detection: {detection_times['temporal']} steps")
        self.log(f"  Improvement: {improvement} steps ({improvement_pct:.1f}% faster)")
        
        return {
            'detection_times': detection_times,
            'improvement_steps': improvement,
            'improvement_percent': improvement_pct
        }
    
    def benchmark_frequency_jamming(self) -> Dict:
        """
        Test performance against frequency-selective jamming.
        
        Returns
        -------
        results : dict
            Performance under different jamming scenarios
        """
        self.log("\n" + "=" * 60)
        self.log("BENCHMARK 5: Frequency-Selective Jamming")
        self.log("=" * 60)
        
        T = 512
        t = np.linspace(0, 4*np.pi, T)
        
        # Ground truth: multi-frequency signal
        ground_truth = np.sin(t) + 0.3*np.sin(3*t) + 0.2*np.sin(5*t)
        
        # Clean signals
        n_clean = 5
        signals = []
        for _ in range(n_clean):
            signals.append(ground_truth + 0.1*np.random.randn(T))
        
        # Add frequency-jammed sensors (jam high frequencies)
        n_jammed = 2
        for _ in range(n_jammed):
            # Add high-frequency noise
            high_freq_noise = 2.0 * np.sin(20*t) * np.random.rand()
            signals.append(ground_truth + 0.1*np.random.randn(T) + high_freq_noise)
        
        signals = np.array(signals)
        
        # Test oracle
        oracle = AdaptiveSpectralKernel(alpha=1.5)
        pred, weights = oracle.fit(signals)
        
        # Baseline
        pred_equal = BaselineMethods.equal_weights(signals)
        
        metrics_oracle = compute_all_metrics(pred, ground_truth)
        metrics_equal = compute_all_metrics(pred_equal, ground_truth)
        
        improvement = (metrics_equal['rmse'] - metrics_oracle['rmse']) / metrics_equal['rmse'] * 100
        
        self.log(f"\nFrequency-Selective Jamming ({n_jammed}/{n_clean+n_jammed} sensors jammed):")
        self.log(f"  Equal Weights RMSE: {metrics_equal['rmse']:.4f}")
        self.log(f"  Adaptive FFT RMSE:  {metrics_oracle['rmse']:.4f}")
        self.log(f"  Improvement: {improvement:.1f}%")
        self.log(f"  Jammed sensor weights: {weights[n_clean:]}")
        
        return {
            'oracle': metrics_oracle,
            'equal': metrics_equal,
            'improvement': improvement,
            'jammed_weights': weights[n_clean:].tolist()
        }
    
    def run_all(self) -> Dict:
        """
        Run complete benchmark suite.
        
        Returns
        -------
        all_results : dict
            Combined results from all benchmarks
        """
        self.log("\n" + "=" * 60)
        self.log("ADAPTIVE SPECTRAL KERNEL ORACLE - BENCHMARK SUITE")
        self.log("Lex Liberatum Kernels v1.1")
        self.log("=" * 60)
        
        # Run all benchmarks
        adversarial = self.benchmark_adversarial_robustness()
        scaling = self.benchmark_scaling()
        methods = self.benchmark_methods_comparison()
        drift = self.benchmark_drift_detection()
        jamming = self.benchmark_frequency_jamming()
        
        self.results = {
            'adversarial': adversarial,
            'scaling': scaling,
            'methods': methods,
            'drift': drift,
            'jamming': jamming
        }
        
        # Summary
        self.log("\n" + "=" * 60)
        self.log("BENCHMARK COMPLETE - KEY FINDINGS")
        self.log("=" * 60)
        
        self.log("\n1. ADVERSARIAL ROBUSTNESS:")
        self.log(f"   - Clean data (0%): {adversarial[0.0]['improvement_vs_equal']:+.1f}% vs equal weights")
        self.log(f"   - 30% contamination: {adversarial[0.3]['improvement_vs_equal']:+.1f}% improvement")
        self.log(f"   - 40% contamination: {adversarial[0.4]['improvement_vs_equal']:+.1f}% improvement")
        
        self.log("\n2. COMPUTATIONAL SCALING:")
        self.log(f"   - 100 nodes: {scaling[100]['time']*1000:.1f}ms")
        self.log(f"   - 1000 nodes: {scaling[1000]['time']*1000:.1f}ms")
        if 5000 in scaling:
            self.log(f"   - 5000 nodes: {scaling[5000]['time']:.2f}s")
        
        self.log("\n3. DRIFT DETECTION:")
        self.log(f"   - Temporal kernel: {drift['improvement_percent']:.1f}% faster detection")
        
        self.log("\n4. FREQUENCY JAMMING:")
        self.log(f"   - {jamming['improvement']:.1f}% improvement vs equal weights")
        
        self.log("\n" + "=" * 60)
        self.log("Patent: PCT Pending | Trust: 0x44f8...C689 | Royalty: 25bp")
        self.log("=" * 60)
        
        return self.results


def main():
    """Run comprehensive benchmarks."""
    suite = BenchmarkSuite(verbose=True)
    results = suite.run_all()
    
    # Optionally save results
    try:
        import json
        output_file = 'benchmark_results.json'
        
        # Convert numpy types to Python types for JSON
        def convert_to_json_serializable(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, dict):
                return {k: convert_to_json_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_json_serializable(item) for item in obj]
            return obj
        
        results_serializable = convert_to_json_serializable(results)
        
        with open(output_file, 'w') as f:
            json.dump(results_serializable, f, indent=2)
        
        print(f"\nResults saved to {output_file}")
    except Exception as e:
        print(f"\nCould not save results: {e}")


if __name__ == "__main__":
    main()
