"""
KL-074-LEXFARM: Precision Agriculture Kernel
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
class FarmSensor:
    sensor_id: str
    field_id: str
    soil_moisture_pct: float
    soil_temp_c: float
    ph_level: float
    nitrogen_ppm: float
    phosphorus_ppm: float
    potassium_ppm: float
    timestamp: float


class LexFarmKernel:
    def __init__(self):
        self.kernel = TemporalAdaptiveKernel(alpha=1.2, beta=0.98, lambda_jitter=0.25, drift_threshold=0.06)
        self.irrigation_alerts = []
        self.timestep = 0
        self.readings = 0
    
    def monitor_fields(self, sensors: List[FarmSensor]) -> Dict:
        signals = np.array([[s.soil_moisture_pct, s.soil_temp_c, s.ph_level, s.nitrogen_ppm, s.phosphorus_ppm, s.potassium_ppm] for s in sensors])
        fused, weights = self.kernel.update(signals)
        moisture = fused[0]
        temp = fused[1]
        ph = fused[2]
        n = fused[3]
        p = fused[4]
        k = fused[5]
        dry = moisture < 30
        hot = temp > 35
        ph_low = ph < 6.0
        ph_high = ph > 7.5
        n_low = n < 20
        needs_irrigation = dry or hot
        needs_fertilizer = n_low or p < 15 or k < 100
        if needs_irrigation:
            self.irrigation_alerts.append({'timestamp': datetime.now().isoformat(), 'moisture': float(moisture), 'temp': float(temp), 'reason': 'DRY' if dry else 'HOT'})
        failed = [s.sensor_id for i, s in enumerate(sensors) if weights[i] < 0.06]
        self.timestep += 1
        self.readings += len(sensors)
        return {'soil_moisture': float(moisture), 'soil_temp': float(temp), 'ph': float(ph), 'nitrogen': float(n), 'phosphorus': float(p), 'potassium': float(k), 'needs_irrigation': needs_irrigation, 'needs_fertilizer': needs_fertilizer, 'dry': dry, 'hot': hot, 'ph_ok': not (ph_low or ph_high), 'failed_sensors': failed, 'timestep': self.timestep}
    
    def get_report(self) -> Dict:
        return {'timesteps': self.timestep, 'readings': self.readings, 'irrigation_alerts': len(self.irrigation_alerts), 'alert_rate': len(self.irrigation_alerts)/max(1, self.timestep), 'royalty': (self.readings * 25) / 10000, 'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'}
    
    def export_log(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump({'kernel': 'kl-074-lexfarm', 'report': self.get_report(), 'alerts': self.irrigation_alerts}, f, indent=2)


def main():
    kernel = LexFarmKernel()
    print("="*60)
    print("KL-074-LEXFARM: Precision Agriculture Monitoring")
    print("="*60)
    print("\n[OPTIMAL CONDITIONS]")
    sensors_optimal = [FarmSensor(f"SOIL-{i}", f"Field-{i//5}", 45 + np.random.rand()*10, 22 + np.random.rand()*3, 6.5 + np.random.rand()*0.5, 35 + np.random.rand()*10, 25 + np.random.rand()*5, 150 + np.random.rand()*20, datetime.now().timestamp()) for i in range(25)]
    result = kernel.monitor_fields(sensors_optimal)
    print(f"Soil Moisture: {result['soil_moisture']:.1f}%")
    print(f"Soil Temp: {result['soil_temp']:.1f}°C")
    print(f"pH: {result['ph']:.2f}")
    print(f"NPK: N={result['nitrogen']:.1f} P={result['phosphorus']:.1f} K={result['potassium']:.1f}")
    print(f"Irrigation Needed: {result['needs_irrigation']}")
    print(f"Fertilizer Needed: {result['needs_fertilizer']}")
    print("\n[DRY CONDITIONS]")
    sensors_dry = [FarmSensor(f"SOIL-{i}", f"Field-{i//5}", 15 + np.random.rand()*10, 38 + np.random.rand()*3, 6.8 + np.random.rand()*0.3, 18 + np.random.rand()*5, 12 + np.random.rand()*3, 80 + np.random.rand()*15, datetime.now().timestamp()) for i in range(25)]
    result = kernel.monitor_fields(sensors_dry)
    print(f"Soil Moisture: {result['soil_moisture']:.1f}%")
    print(f"Soil Temp: {result['soil_temp']:.1f}°C")
    print(f"⚠️  Irrigation Needed: {result['needs_irrigation']}")
    print(f"⚠️  Fertilizer Needed: {result['needs_fertilizer']}")
    print(f"Dry: {result['dry']}")
    print(f"Hot: {result['hot']}")
    report = kernel.get_report()
    print(f"\n{'='*60}")
    print("FARM REPORT")
    print("="*60)
    print(f"Timesteps: {report['timesteps']}")
    print(f"Readings: {report['​​​​​​​​​​​​​​​​
