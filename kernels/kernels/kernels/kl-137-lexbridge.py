"""
KL-137-LEXBRIDGE: Bridge Structural Health Kernel
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
class BridgeSensor:
    sensor_id: str
    location: str
    strain_microstrain: float
    vibration_hz: float
    deflection_mm: float
    cable_tension_kn: float
    crack_width_mm: float
    temperature_c: float
    traffic_load_tons: float
    timestamp: float


class LexBridgeKernel:
    def __init__(self):
        self.kernel = TemporalAdaptiveKernel(alpha=0.9, beta=0.97, lambda_jitter=0.2, drift_threshold=0.05)
        self.collapse_alerts = []
        self.timestep = 0
        self.readings = 0
    
    def monitor_bridge(self, sensors: List[BridgeSensor]) -> Dict:
        signals = np.array([[s.strain_microstrain, s.vibration_hz, s.deflection_mm, s.cable_tension_kn, s.crack_width_mm, s.temperature_c, s.traffic_load_tons] for s in sensors])
        fused, weights = self.kernel.update(signals)
        strain = fused[0]
        vib = fused[1]
        defl = fused[2]
        tension = fused[3]
        crack = fused[4]
        temp = fused[5]
        load = fused[6]
        high_strain = strain > 2000
        resonance = 2.5 < vib < 4.5
        excess_deflection = defl > 150
        cable_failure = tension < 800
        critical_crack = crack > 5.0
        overload = load > 500
        collapse_risk = (high_strain and excess_deflection) or cable_failure or (critical_crack and overload)
        if collapse_risk:
            self.collapse_alerts.append({'timestamp': datetime.now().isoformat(), 'strain': float(strain), 'deflection': float(defl), 'tension': float(tension), 'crack': float(crack), 'load': float(load), 'reason': 'STRAIN' if high_strain else ('CABLE' if cable_failure else 'CRACK')})
        failed = [s.sensor_id for i, s in enumerate(sensors) if weights[i] < 0.05]
        self.timestep += 1
        self.readings += len(sensors)
        return {'strain_microstrain': float(strain), 'vibration_hz': float(vib), 'deflection_mm': float(defl), 'cable_tension_kn': float(tension), 'crack_width_mm': float(crack), 'temperature_c': float(temp), 'traffic_load_tons': float(load), 'high_strain': high_strain, 'resonance': resonance, 'excess_deflection': excess_deflection, 'cable_failure': cable_failure, 'critical_crack': critical_crack, 'overload': overload, 'collapse_risk': collapse_risk, 'failed_sensors': failed, 'timestep': self.timestep}
    
    def get_report(self) -> Dict:
        return {'timesteps': self.timestep, 'readings': self.readings, 'collapse_alerts': len(self.collapse_alerts), 'alert_rate': len(self.collapse_alerts)/max(1, self.timestep), 'royalty': (self.readings * 25) / 10000, 'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'}
    
    def export_log(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump({'kernel': 'kl-137-lexbridge', 'report': self.get_report(), 'alerts': self.collapse_alerts}, f, indent=2)


def main():
    kernel = LexBridgeKernel()
    print("="*60)
    print("KL-137-LEXBRIDGE: Bridge Structural Health")
    print("="*60)
    print("\n[NORMAL TRAFFIC]")
    sensors_normal = [BridgeSensor(f"BRIDGE-{i}", f"Span-{i//6}", 800 + np.random.rand()*200, 1.5 + np.random.rand()*0.5, 45 + np.random.rand()*15, 1200 + np.random.rand()*100, 1.2 + np.random.rand()*0.5, 22 + np.random.rand()*5, 150 + np.random.rand()*50, datetime.now().timestamp()) for i in range(18)]
    result = kernel.monitor_bridge(sensors_normal)
    print(f"Strain: {result['strain_microstrain']:.0f} µε")
    print(f"Deflection: {result['deflection_mm']:.1f} mm")
    print(f"Cable Tension: {result['cable_tension_kn']:.0f} kN")
    print(f"Crack Width: {result['crack_width_mm']:.2f} mm")
    print(f"Collapse Risk: {result['collapse_risk']}")
    print("\n[HIGH STRAIN + DEFLECTION]")
    sensors_strain = [BridgeSensor(f"BRIDGE-{i}", f"Span-{i//6}", 2200 + np.random.rand()*300, 2.0 + np.random.rand()*0.5, 165 + np.random.rand()*20, 1100 + np.random.rand()*100, 2.5 + np.random.rand()*1, 24 + np.random.rand()*5, 400 + np.random.rand()*50, datetime.now().timestamp()) for i in range(18)]
    result = kernel.monitor_bridge(sensors_strain)
    print(f"Strain: {result['strain_microstrain']:.0f} µε")
    print(f"Deflection: {result['deflection_mm']:.1f} mm")
    print(f"🚨 High Strain: {result['high_strain']}")
    print(f"🚨​​​​​​​​​​​​​​​​
