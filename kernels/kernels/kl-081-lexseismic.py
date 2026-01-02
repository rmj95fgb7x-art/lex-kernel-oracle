"""
KL-081-LEXSEISMIC: Earthquake Early Warning Kernel
Lex Liberatum Kernels v1.1
Patent: PCT Pending | Royalty: 25bp → 0x44f8...C689
"""

import numpy as np
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime
import json
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.temporal_kernel import TemporalAdaptiveKernel


@dataclass
class SeismicSensor:
    sensor_id: str
    location: str
    latitude: float
    longitude: float
    p_wave_amplitude: float
    s_wave_amplitude: float
    ground_velocity_cm_s: float
    frequency_hz: float
    timestamp: float


class LexSeismicKernel:
    def __init__(self):
        self.kernel = TemporalAdaptiveKernel(alpha=0.8, beta=0.99, lambda_jitter=0.15, drift_threshold=0.04)
        self.earthquake_alerts = []
        self.timestep = 0
        self.readings = 0
    
    def detect_earthquake(self, sensors: List[SeismicSensor]) -> Dict:
        signals = np.array([[s.p_wave_amplitude, s.s_wave_amplitude, s.ground_velocity_cm_s, s.frequency_hz] for s in sensors])
        fused, weights = self.kernel.update(signals)
        p_wave = fused[0]
        s_wave = fused[1]
        velocity = fused[2]
        freq = fused[3]
        magnitude_est = 2.0 + np.log10(max(s_wave, 0.1)) * 0.8
        earthquake = p_wave > 0.5 or s_wave > 1.0 or velocity > 5.0
        severe = magnitude_est > 5.0
        if earthquake:
            epicenter_lat = np.average([s.latitude for s in sensors], weights=weights)
            epicenter_lon = np.average([s.longitude for s in sensors], weights=weights)
            self.earthquake_alerts.append({'timestamp': datetime.now().isoformat(), 'magnitude': float(magnitude_est), 'epicenter': [float(epicenter_lat), float(epicenter_lon)], 'p_wave': float(p_wave), 's_wave': float(s_wave), 'velocity': float(velocity)})
        failed = [s.sensor_id for i, s in enumerate(sensors) if weights[i] < 0.04]
        self.timestep += 1
        self.readings += len(sensors)
        return {'p_wave_amplitude': float(p_wave), 's_wave_amplitude': float(s_wave), 'ground_velocity': float(velocity), 'frequency': float(freq), 'magnitude_estimate': float(magnitude_est), 'earthquake_detected': earthquake, 'severe_earthquake': severe, 'failed_sensors': failed, 'timestep': self.timestep}
    
    def get_report(self) -> Dict:
        return {'timesteps': self.timestep, 'readings': self.readings, 'earthquakes': len(self.earthquake_alerts), 'severe_count': sum(1 for a in self.earthquake_alerts if a['magnitude'] > 5.0), 'royalty': (self.readings * 25) / 10000, 'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'}
    
    def export_log(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump({'kernel': 'kl-081-lexseismic', 'report': self.get_report(), 'alerts': self.earthquake_alerts}, f, indent=2)


def main():
    kernel = LexSeismicKernel()
    print("="*60)
    print("KL-081-LEXSEISMIC: Earthquake Early Warning")
    print("="*60)
    print("\n[NORMAL SEISMIC ACTIVITY]")
    sensors_normal = [SeismicSensor(f"SEIS-{i}", f"Station-{i}", 35.0 + np.random.rand()*0.5, -118.0 + np.random.rand()*0.5, 0.05 + np.random.rand()*0.05, 0.08 + np.random.rand()*0.05, 0.5 + np.random.rand()*0.3, 2 + np.random.rand(), datetime.now().timestamp()) for i in range(30)]
    result = kernel.detect_earthquake(sensors_normal)
    print(f"P-Wave: {result['p_wave_amplitude']:.3f}")
    print(f"S-Wave: {result['s_wave_amplitude']:.3f}")
    print(f"Ground Velocity: {result['ground_velocity']:.2f} cm/s")
    print(f"Earthquake: {result['earthquake_detected']}")
    print("\n[MODERATE EARTHQUAKE - M4.5]")
    sensors_moderate = [SeismicSensor(f"SEIS-{i}", f"Station-{i}", 35.0 + np.random.rand()*0.5, -118.0 + np.random.rand()*0.5, 1.2 + np.random.rand()*0.3, 2.5 + np.random.rand()*0.5, 8 + np.random.rand()*2, 5 + np.random.rand(), datetime.now().timestamp()) for i in range(30)]
    result = kernel.detect_earthquake(sensors_moderate)
    print(f"P-Wave: {result['p_wave_amplitude']:.3f}")
    print(f"S-Wave: {result['s_wave_amplitude']:.3f}")
    print(f"Ground Velocity: {result['ground_velocity']:.2f} cm/s")
    print(f"Magnitude: {result['magnitude_estimate']:.1f}")
    print(f"⚠️  Earthquake: {result['earthquake_detected']}")
    print("\n[SEVERE EARTHQUAKE - M6.8]")
    sensors_severe = [SeismicSensor(f"SEIS-{i}", f"Station-{i}", 35.0 + np.random.rand()*0.5, -118.0 + np.random.rand()*0.5, 5.0 + np.random.rand()*2, 12 + np.random.rand()*3, 35 + np.random.rand()*10, 8 + np.random.rand()*2, datetime.now().timestamp()) for i in range(30)]
    result = kernel.detect_earthquake(sensors_severe)
    print(f"P-Wave: {result['p_wave_amplitude']:.3f}")
    print(f"S-Wave: {result['s_wave_amplitude']:.3f}")
    print(f"Ground Velocity: {result['ground_velocity']:.2f} cm/s")
    print(f"Magnitude: {result['magnitude_estimate']:.1f}")
    print(f"🚨 SEVERE EARTHQUAKE: {result['severe_earthquake']}")
    report = kernel.get_report()
    print(f"\n{'='*60}")
    print("SEISMIC REPORT")
    print("="*60)
    print(f"Timesteps: {report['timesteps']}")
    print(f"Readings: {report['readings']}")
    print(f"Earthquakes Detected: {report['earthquakes']}")
    print(f"Severe (M>5.0): {report['severe_count']}")
    print(f"Royalty: ${report['royalty']:.2f}")
    kernel.export_log('kl-081-lexseismic-log.json')


if __name__ == "__main__":
    main()
