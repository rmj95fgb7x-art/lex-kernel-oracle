"""
KL-095-LEXMINE: Mining Safety Kernel
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
class MineSensor:
    sensor_id: str
    location_depth_m: float
    methane_ppm: float
    co_ppm: float
    oxygen_pct: float
    temperature_c: float
    humidity_pct: float
    roof_stress_mpa: float
    timestamp: float


class LexMineKernel:
    def __init__(self):
        self.kernel = TemporalAdaptiveKernel(alpha=0.85, beta=0.97, lambda_jitter=0.18, drift_threshold=0.04)
        self.evacuate_alerts = []
        self.timestep = 0
        self.readings = 0
    
    def monitor_mine(self, sensors: List[MineSensor]) -> Dict:
        signals = np.array([[s.methane_ppm, s.co_ppm, s.oxygen_pct, s.temperature_c, s.humidity_pct, s.roof_stress_mpa] for s in sensors])
        fused, weights = self.kernel.update(signals)
        methane = fused[0]
        co = fused[1]
        o2 = fused[2]
        temp = fused[3]
        humidity = fused[4]
        stress = fused[5]
        methane_danger = methane > 10000
        co_danger = co > 50
        o2_low = o2 < 19.5
        collapse_risk = stress > 25
        evacuate = methane_danger or co_danger or o2_low or collapse_risk
        if evacuate:
            self.evacuate_alerts.append({'timestamp': datetime.now().isoformat(), 'methane': float(methane), 'co': float(co), 'oxygen': float(o2), 'stress': float(stress), 'reason': 'METHANE' if methane_danger else ('CO' if co_danger else ('OXYGEN' if o2_low else 'COLLAPSE'))})
        failed = [s.sensor_id for i, s in enumerate(sensors) if weights[i] < 0.04]
        self.timestep += 1
        self.readings += len(sensors)
        return {'methane_ppm': float(methane), 'co_ppm': float(co), 'oxygen_pct': float(o2), 'temperature_c': float(temp), 'humidity_pct': float(humidity), 'roof_stress_mpa': float(stress), 'methane_danger': methane_danger, 'co_danger': co_danger, 'oxygen_low': o2_low, 'collapse_risk': collapse_risk, 'evacuate_now': evacuate, 'failed_sensors': failed, 'timestep': self.timestep}
    
    def get_report(self) -> Dict:
        return {'timesteps': self.timestep, 'readings': self.readings, 'evacuations': len(self.evacuate_alerts), 'evac_rate': len(self.evacuate_alerts)/max(1, self.timestep), 'royalty': (self.readings * 25) / 10000, 'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'}
    
    def export_log(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump({'kernel': 'kl-095-lexmine', 'report': self.get_report(), 'alerts': self.evacuate_alerts}, f, indent=2)


def main():
    kernel = LexMineKernel()
    print("="*60)
    print("KL-095-LEXMINE: Mining Safety Monitoring")
    print("="*60)
    print("\n[SAFE CONDITIONS]")
    sensors_safe = [MineSensor(f"MINE-{i}", 500 + i*50, 1000 + np.random.rand()*500, 10 + np.random.rand()*5, 20.5 + np.random.rand()*0.5, 18 + np.random.rand()*3, 65 + np.random.rand()*10, 15 + np.random.rand()*3, datetime.now().timestamp()) for i in range(20)]
    result = kernel.monitor_mine(sensors_safe)
    print(f"Methane: {result['methane_ppm']:.0f} ppm")
    print(f"CO: {result['co_ppm']:.1f} ppm")
    print(f"Oxygen: {result['oxygen_pct']:.1f}%")
    print(f"Roof Stress: {result['roof_stress_mpa']:.1f} MPa")
    print(f"Evacuate: {result['evacuate_now']}")
    print("\n[METHANE BUILDUP]")
    sensors_methane = [MineSensor(f"MINE-{i}", 500 + i*50, 12000 + np.random.rand()*2000, 10 + np.random.rand()*5, 20.5 + np.random.rand()*0.5, 18 + np.random.rand()*3, 65 + np.random.rand()*10, 15 + np.random.rand()*3, datetime.now().timestamp()) for i in range(20)]
    result = kernel.monitor_mine(sensors_methane)
    print(f"Methane: {result['methane_ppm']:.0f} ppm")
    print(f"🚨 Methane Danger: {result['methane_danger']}")
    print(f"🚨 EVACUATE: {result['evacuate_now']}")
    print("\n[ROOF COLLAPSE RISK]")
    sensors_collapse = [MineSensor(f"MINE-{i}", 500 + i*50, 1000 + np.random.rand()*500, 10 + np.random.rand()*5, 20.5 + np.random.rand()*0.5, 18 + np.random.rand()*3, 65 + np.random.rand()*10, 28 + np.random.rand()*3, datetime.now().timestamp()) for i in range(20)]
    result = kernel.monitor_mine(sensors_collapse)
    print(f"Roof Stress: {result['roof_stress_mpa']:.1f} MPa")
    print(f"🚨 Collapse Risk: {result['collapse_risk']}")
    print(f"🚨 EVACUATE: {result['evacuate_now']}")
    print("\n[LOW OXYGEN]")
    sensors_o2 = [MineSensor(f"MINE-{i}", 500 + i*50, 1000 + np.random.rand()*500, 10 + np.random.rand()*5, 18.0 + np.random.rand()*0.5, 18 + np.random.rand()*3, 65 + np.random.rand()*10, 15 + np.random.rand()*3, datetime.now().timestamp()) for i in range(20)]
    result = kernel.​​​​​​​​​​​​​​​​
