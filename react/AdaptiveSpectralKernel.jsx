import React, { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Play, Download, Info, AlertTriangle } from 'lucide-react';

const AdaptiveSpectralKernel = () => {
  const [results, setResults] = useState(null);
  const [running, setRunning] = useState(false);
  const [config, setConfig] = useState({
    nClean: 5,
    nPoisoned: 2,
    noiseLevel: 0.1,
    poisonMagnitude: 5.0,
    alpha: 1.5,
    samples: 512
  });

  // FFT implementation
  const fft = (signal) => {
    const n = signal.length;
    if (n <= 1) return signal.map(x => ({ re: x, im: 0 }));

    const even = fft(signal.filter((_, i) => i % 2 === 0));
    const odd = fft(signal.filter((_, i) => i % 2 === 1));

    const result = new Array(n);
    for (let k = 0; k < n/2; k++) {
      const angle = -2 * Math.PI * k / n;
      const cos = Math.cos(angle);
      const sin = Math.sin(angle);
      const tRe = cos * odd[k].re - sin * odd[k].im;
      const tIm = cos * odd[k].im + sin * odd[k].re;
      
      result[k] = {
        re: even[k].re + tRe,
        im: even[k].im + tIm
      };
      result[k + n/2] = {
        re: even[k].re - tRe,
        im: even[k].im - tIm
      };
    }
    return result;
  };

  const ifft = (spectrum) => {
    const n = spectrum.length;
    const conjugate = spectrum.map(c => ({ re: c.re, im: -c.im }));
    const result = fft(conjugate);
    return result.map(c => c.re / n);
  };

  const norm = (arr1, arr2) => {
    return Math.sqrt(arr1.reduce((sum, val, i) => sum + (val - arr2[i]) ** 2, 0));
  };

  const median = (signals) => {
    const n = signals[0].length;
    const result = new Array(n);
    for (let i = 0; i < n; i++) {
      const values = signals.map(s => s[i]).sort((a, b) => a - b);
      result[i] = values[Math.floor(values.length / 2)];
    }
    return result;
  };

  const runBenchmark = () => {
    setRunning(true);

    setTimeout(() => {
      const { nClean, nPoisoned, noiseLevel, poisonMagnitude, alpha, samples } = config;
      const n = nClean + nPoisoned;
      
      // Generate ground truth: sinusoidal signal (periodic compliance pattern)
      const t = Array.from({ length: samples }, (_, i) => i / samples * 4 * Math.PI);
      const groundTruth = t.map(x => Math.sin(x) + 0.3 * Math.sin(3 * x));
      
      // Generate signals
      const signals = [];
      
      // Clean sensors with small noise
      for (let i = 0; i < nClean; i++) {
        signals.push(groundTruth.map(val => val + (Math.random() - 0.5) * noiseLevel));
      }
      
      // Poisoned sensors with large offset
      for (let i = 0; i < nPoisoned; i++) {
        signals.push(groundTruth.map(val => val + (Math.random() - 0.5) * noiseLevel + poisonMagnitude));
      }
      
      // Method 1: Fixed equal weights
      const equalWeights = new Array(n).fill(1/n);
      const equalMean = groundTruth.map((_, i) => 
        signals.reduce((sum, sig) => sum + sig[i], 0) / n
      );
      
      // Method 2: Fixed sector priors (higher weight to "clean" sensors)
      const priorWeights = [
        ...new Array(nClean).fill(0.8 / nClean),
        ...new Array(nPoisoned).fill(0.2 / nPoisoned)
      ];
      const priorMean = groundTruth.map((_, i) =>
        signals.reduce((sum, sig, j) => sum + sig[i] * priorWeights[j], 0)
      );
      
      // Method 3: Adaptive weights (robust)
      const robustCenter = median(signals);
      const distances = signals.map(sig => norm(sig, robustCenter));
      const distancesCopy = [...distances];
      distancesCopy.sort((a, b) => a - b);
      const medianDist = distancesCopy[Math.floor(distancesCopy.length / 2)];
      const tau = alpha * medianDist;
      
      let adaptiveWeights = distances.map(d => Math.exp(-(d ** 2) / (2 * tau ** 2)));
      const weightSum = adaptiveWeights.reduce((a, b) => a + b, 0);
      adaptiveWeights = adaptiveWeights.map(w => w / weightSum);
      
      const adaptiveMean = groundTruth.map((_, i) =>
        signals.reduce((sum, sig, j) => sum + sig[i] * adaptiveWeights[j], 0)
      );
      
      // FFT fusion for adaptive method
      const spectra = signals.map(sig => fft(sig));
      const avgSpectrum = spectra[0].map((_, i) => ({
        re: spectra.reduce((sum, spec, j) => sum + spec[i].re * adaptiveWeights[j], 0),
        im: spectra.reduce((sum, spec, j) => sum + spec[i].im * adaptiveWeights[j], 0)
      }));
      const adaptiveFFT = ifft(avgSpectrum);
      
      // Calculate RMSE
      const rmseEqual = Math.sqrt(equalMean.reduce((sum, val, i) => sum + (val - groundTruth[i]) ** 2, 0) / samples);
      const rmsePrior = Math.sqrt(priorMean.reduce((sum, val, i) => sum + (val - groundTruth[i]) ** 2, 0) / samples);
      const rmseAdaptive = Math.sqrt(adaptiveMean.reduce((sum, val, i) => sum + (val - groundTruth[i]) ** 2, 0) / samples);
      const rmseAdaptiveFFT = Math.sqrt(adaptiveFFT.reduce((sum, val, i) => sum + (val - groundTruth[i]) ** 2, 0) / samples);
      
      // Prepare chart data (downsample for display)
      const chartData = t.map((time, i) => ({
        time: time,
        truth: groundTruth[i],
        equal: equalMean[i],
        prior: priorMean[i],
        adaptive: adaptiveMean[i],
        adaptiveFFT: adaptiveFFT[i]
      })).filter((_, i) => i % 4 === 0);
      
      // Weight visualization
      const weightData = signals.map((_, i) => ({
        sensor: i < nClean ? `Clean ${i+1}` : `Poisoned ${i-nClean+1}`,
        equal: equalWeights[i],
        prior: priorWeights[i],
        adaptive: adaptiveWeights[i],
        type: i < nClean ? 'clean' : 'poisoned'
      }));
      
      setResults({
        rmseEqual,
        rmsePrior,
        rmseAdaptive,
        rmseAdaptiveFFT,
        chartData,
        weightData,
        improvement: ((rmseEqual - rmseAdaptiveFFT) / rmseEqual * 100).toFixed(1),
        tau: tau.toFixed(3)
      });
      
      setRunning(false);
    }, 100);
  };

  const downloadCode = () => {
    const code = `"""
Adaptive Spectral Kernel Oracle - Production Implementation
Lex Liberatum Kernels v1.1
"""

import numpy as np
from scipy.fft import fft, ifft

def adaptive_spectral_kernel(signals, alpha=1.5):
    """
    Fuses multi-source time-series with adaptive outlier-resistant weighting.
    
    Args:
        signals: List of 1D arrays (each signal is a time-series)
        alpha: Sensitivity parameter for tau (typical: 1.0-3.0)
    
    Returns:
        K_w: Fused signal
        weights: Adaptive weights applied
    """
    signals = np.array(signals)
    n = len(signals)
    
    # Step 1: Robust center via median
    robust_center = np.median(signals, axis=0)
    
    # Step 2: Compute distances
    distances = np.array([np.linalg.norm(sig - robust_center) for sig in signals])
    
    # Step 3: Adaptive tau
    tau = alpha * np.median(distances)
    
    # Step 4: Adaptive weights (Gaussian kernel)
    weights = np.exp(-(distances ** 2) / (2 * tau ** 2))
    weights /= weights.sum()  # Normalize
    
    # Step 5: FFT fusion
    spectra = np.array([fft(sig) for sig in signals])
    avg_spectrum = np.average(spectra, axis=0, weights=weights)
    K_w = np.real(ifft(avg_spectrum))
    
    return K_w, weights

# Example usage
if __name__ == "__main__":
    # Simulate 7 sensors: 5 clean + 2 poisoned
    t = np.linspace(0, 4*np.pi, 512)
    ground_truth = np.sin(t) + 0.3 * np.sin(3*t)
    
    signals = []
    # Clean sensors
    for _ in range(5):
        signals.append(ground_truth + 0.1 * np.random.randn(len(t)))
    # Poisoned sensors
    for _ in range(2):
        signals.append(ground_truth + 0.1 * np.random.randn(len(t)) + 5.0)
    
    # Fuse signals
    K_w, weights = adaptive_spectral_kernel(signals, alpha=1.5)
    
    # Evaluate
    rmse = np.sqrt(np.mean((K_w - ground_truth) ** 2))
    print(f"RMSE: {rmse:.4f}")
    print(f"Weights: {weights}")
    print(f"Clean sensor avg weight: {weights[:5].mean():.3f}")
    print(f"Poisoned sensor avg weight: {weights[5:].mean():.3f}")
`;

    const blob = new Blob([code], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'adaptive_spectral_kernel.py';
    a.click();
  };

  return (
    <div className="w-full min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
            Adaptive Spectral Kernel Oracle
          </h1>
          <p className="text-slate-400">Production Implementation & Benchmark Suite</p>
          <p className="text-xs text-slate-500 mt-2">Lex Liberatum Kernels v1.1 - Patent Pending</p>
        </div>

        {/* Configuration Panel */}
        <div className="bg-slate-800/50 backdrop-blur rounded-lg p-6 mb-6 border border-slate-700">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <Info className="w-5 h-5 text-cyan-400" />
            Benchmark Configuration
          </h2>
          
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm text-slate-400 mb-1">Clean Sensors</label>
              <input
                type="number"
                value={config.nClean}
                onChange={(e) => setConfig({...config, nClean: parseInt(e.target.value)})}
                className="w-full bg-slate-700 rounded px-3 py-2 text-white"
                min="1"
                max="10"
              />
            </div>
            
            <div>
              <label className="block text-sm text-slate-400 mb-1">Poisoned Sensors</label>
              <input
                type="number"
                value={config.nPoisoned}
                onChange={(e) => setConfig({...config, nPoisoned: parseInt(e.target.value)})}
                className="w-full bg-slate-700 rounded px-3 py-2 text-white"
                min="0"
                max="5"
              />
            </div>
            
            <div>
              <label className="block text-sm text-slate-400 mb-1">Noise Level</label>
              <input
                type="number"
                value={config.noiseLevel}
                onChange={(e) => setConfig({...config, noiseLevel: parseFloat(e.target.value)})}
                className="w-full bg-slate-700 rounded px-3 py-2 text-white"
                min="0.01"
                max="1"
                step="0.05"
              />
            </div>
            
            <div>
              <label className="block text-sm text-slate-400 mb-1">Poison Magnitude</label>
              <input
                type="number"
                value={config.poisonMagnitude}
                onChange={(e) => setConfig({...config, poisonMagnitude: parseFloat(e.target.value)})}
                className="w-full bg-slate-700 rounded px-3 py-2 text-white"
                min="1"
                max="10"
                step="0.5"
              />
            </div>
            
            <div>
              <label className="block text-sm text-slate-400 mb-1">Alpha (τ sensitivity)</label>
              <input
                type="number"
                value={config.alpha}
                onChange={(e) => setConfig({...config, alpha: parseFloat(e.target.value)})}
                className="w-full bg-slate-700 rounded px-3 py-2 text-white"
                min="0.5"
                max="3"
                step="0.1"
              />
            </div>
            
            <div>
              <label className="block text-sm text-slate-400 mb-1">Samples</label>
              <input
                type="number"
                value={config.samples}
                onChange={(e) => setConfig({...config, samples: parseInt(e.target.value)})}
                className="w-full bg-slate-700 rounded px-3 py-2 text-white"
                min="128"
                max="1024"
                step="128"
              />
            </div>
          </div>
          
          <div className="flex gap-3 mt-6">
            <button
              onClick={runBenchmark}
              disabled={running}
              className="flex items-center gap-2 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 disabled:from-slate-600 disabled:to-slate-600 px-6 py-2 rounded-lg font-semibold transition-all"
            >
              <Play className="w-4 h-4" />
              {running ? 'Running...' : 'Run Benchmark'}
            </button>
            
            <button
              onClick={downloadCode}
              className="flex items-center gap-2 bg-slate-700 hover:bg-slate-600 px-6 py-2 rounded-lg font-semibold transition-all"
            >
              <Download className="w-4 h-4" />
              Download Python Code
            </button>
          </div>
        </div>

        {/* Results */}
        {results && (
          <>
            {/* RMSE Comparison */}
            <div className="bg-slate-800/50 backdrop-blur rounded-lg p-6 mb-6 border border-slate-700">
              <h2 className="text-xl font-semibold mb-4">RMSE Comparison</h2>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div className="bg-slate-700/50 rounded-lg p-4">
                  <div className="text-slate-400 text-sm mb-1">Equal Weights</div>
                  <div className="text-2xl font-bold text-red-400">{results.rmseEqual.toFixed(4)}</div>
                </div>
                
                <div className="bg-slate-700/50 rounded-lg p-4">
                  <div className="text-slate-400 text-sm mb-1">Fixed Priors</div>
                  <div className="text-2xl font-bold text-orange-400">{results.rmsePrior.toFixed(4)}</div>
                </div>
                
                <div className="bg-slate-700/50 rounded-lg p-4">
                  <div className="text-slate-400 text-sm mb-1">Adaptive (Time)</div>
                  <div className="text-2xl font-bold text-yellow-400">{results.rmseAdaptive.toFixed(4)}</div>
                </div>
                
                <div className="bg-gradient-to-br from-green-600/20 to-cyan-600/20 rounded-lg p-4 border border-green-500/30">
                  <div className="text-slate-300 text-sm mb-1 font-semibold">Adaptive FFT ✓</div>
                  <div className="text-2xl font-bold text-green-400">{results.rmseAdaptiveFFT.toFixed(4)}</div>
                  <div className="text-xs text-green-400 mt-1">{results.improvement}% improvement</div>
                </div>
              </div>
              
              <div className="bg-slate-700/30 rounded p-3 text-sm">
                <span className="text-slate-400">Adaptive τ:</span> <span className="text-cyan-400 font-mono">{results.tau}</span>
                <span className="text-slate-500 ml-2">(auto-scaled to data)</span>
              </div>
            </div>

            {/* Signal Reconstruction */}
            <div className="bg-slate-800/50 backdrop-blur rounded-lg p-6 mb-6 border border-slate-700">
              <h2 className="text-xl font-semibold mb-4">Signal Reconstruction</h2>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={results.chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="time" stroke="#94a3b8" />
                  <YAxis stroke="#94a3b8" />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569' }}
                    labelStyle={{ color: '#94a3b8' }}
                  />
                  <Legend />
                  <Line type="monotone" dataKey="truth" stroke="#8b5cf6" strokeWidth={2} name="Ground Truth" dot={false} />
                  <Line type="monotone" dataKey="equal" stroke="#ef4444" strokeWidth={1.5} name="Equal Weights" dot={false} strokeDasharray="5 5" />
                  <Line type="monotone" dataKey="adaptive" stroke="#fbbf24" strokeWidth={1.5} name="Adaptive (Time)" dot={false} strokeDasharray="3 3" />
                  <Line type="monotone" dataKey="adaptiveFFT" stroke="#10b981" strokeWidth={2} name="Adaptive FFT" dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Weight Distribution */}
            <div className="bg-slate-800/50 backdrop-blur rounded-lg p-6 border border-slate-700">
              <h2 className="text-xl font-semibold mb-4">Weight Distribution Comparison</h2>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-700">
                      <th className="text-left py-2 px-3 text-slate-400">Sensor</th>
                      <th className="text-right py-2 px-3 text-slate-400">Equal</th>
                      <th className="text-right py-2 px-3 text-slate-400">Prior</th>
                      <th className="text-right py-2 px-3 text-slate-400">Adaptive</th>
                      <th className="text-left py-2 px-3 text-slate-400">Type</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.weightData.map((row, i) => (
                      <tr key={i} className="border-b border-slate-700/50">
                        <td className="py-2 px-3">{row.sensor}</td>
                        <td className="text-right py-2 px-3 font-mono">{row.equal.toFixed(4)}</td>
                        <td className="text-right py-2 px-3 font-mono">{row.prior.toFixed(4)}</td>
                        <td className="text-right py-2 px-3 font-mono">
                          <span className={row.type === 'clean' ? 'text-green-400' : 'text-red-400'}>
                            {row.adaptive.toFixed(4)}
                          </span>
                        </td>
                        <td className="py-2 px-3">
                          <span className={`px-2 py-1 rounded text-xs ${
                            row.type === 'clean' ? 'bg-green-900/30 text-green-400' : 'bg-red-900/30 text-red-400'
                          }`}>
                            {row.type}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}

        {/* Footer */}
        <div className="mt-8 text-center text-slate-500 text-sm">
          <p>Lex Liberatum Trust - Patent Pending PCT/2025</p>
          <p className="mt-1">Royalty: 25 bp per decision → <span className="font-mono text-cyan-400">0x44f8...C689</span></p>
        </div>
      </div>
    </div>
  );
};

export default AdaptiveSpectralKernel;
