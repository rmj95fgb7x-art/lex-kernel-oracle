"""
KL-130-LEXDAM: Dam Safety Monitoring Kernel
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
class DamSensor:
    sensor_id: str
    location: str
    water_level_m: float
    flow_rate_m3_s: float
    structural_stress_mpa: float
    seepage_rate_l_min: float
    vibration_hz: float
    gate_position_pct: float
    downstream_level_m: float
    timestamp: float


class LexDamKernel:
    def __init__(self):
        self.kernel = TemporalAdaptiveKernel(alpha=0.85, beta=0.98, lambda_jitter=0.15, drift_threshold=0.04)
        self.failure_alerts = []
        self.timestep = 0
        self.readings = 0
    
    def monitor_dam(self, sensors: List[DamSensor]) -> Dict:
        signals = np.array([[s.water_level_m, s.flow_rate_m3_s, s.structural_stress_mpa, s.seepage_rate_l_min, s.vibration_hz, s.gate_position_pct, s.downstream_level_m] for s in sensors])
        fused, weights = self.kernel.update(signals)
        level = fused[0]
        flow = fused[1]
        stress = fused[2]
        seepage = fused[3]
        vib = fused[4]
        gate = fused[5]
        downstream = fused[6]
        overflow = level > 95
        high_stress = stress > 30
        excessive_seepage = seepage > 50
        high_vibration = vib > 5
        gate_failure = abs(gate - 50) < 5 and flow > 500
        downstream_flood = downstream > 80
        catastrophic = (overflow and high_stress) or excessive_seepage or (gate_failure and downstream_flood)
        if catastrophic:
            self.failure_alerts.append({'timestamp': datetime.now().isoformat(), 'level': float(level), 'stress': float(stress), 'seepage': float(seepage), 'flow': float(flow), 'reason': 'OVERFLOW' if overflow else ('SEEPAGE' if excessive_seepage else 'GATE_FAILURE')})
        failed = [s.sensor_id for i, s in enumerate(sensors) if weights[i] < 0.04]
        self.timestep += 1
        self.readings += len(sensors)
        return {'water_level_m': float(level), 'flow_rate_m3_s': float(flow), 'structural_stress_mpa': float(stress), 'seepage_rate_l_min': float(seepage), 'vibration_hz': float(vib), 'gate_position_pct': float(gate), 'downstream_level_m': float(downstream), 'overflow_risk': overflow, 'high_stress': high_stress, 'excessive_seepage': excessive_seepage, 'gate_failure': gate_failure, 'downstream_flood': downstream_flood, 'catastrophic_failure': catastrophic, 'failed_sensors': failed, 'timestep': self.timestep}
    
    def get_report(self) -> Dict:
        return {'timesteps': self.timestep, 'readings': self.readings, 'failure_events': len(self.failure_alerts), 'event_rate': len(self.failure_alerts)/max(1, self.timestep), 'royalty': (self.readings * 25) / 10000, 'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'}
    
    def export_log(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump({'kernel': 'kl-130-lexdam', 'report': self.get_report(), 'alerts': self.failure_alerts}, f, indent=2)


def main():
    kernel = LexDamKernel()
    print("="*60)
    print("KL-130-LEXDAM: Dam Safety Monitoring")
    print("="*60)
    print("\n[NORMAL OPERATION]")
    sensors_normal = [DamSensor(f"DAM-{i}", f"Section-{i//4}", 70 + np.random.rand()*10, 300 + np.random.rand()*50, 18 + np.random.rand()*3, 12 + np.random.rand()*5, 1.5 + np.random.rand()*0.5, 60 + np.random.rand()*10, 40 + np.random.rand()*10, datetime.now().timestamp()) for i in range(16)]
    result = kernel.monitor_dam(sensors_normal)
    print(f"Water Level: {result['water_level_m']:.1f}m")
    print(f"Flow Rate: {result['flow_rate_m3_s']:.1f} m³/s")
    print(f"Structural Stress: {result['structural_stress_mpa']:.1f} MPa")
    print(f"Seepage: {result['seepage_rate_l_min']:.1f} L/min")
    print(f"Catastrophic Failure: {result['catastrophic_failure']}")
    print("\n[HIGH WATER - OVERFLOW RISK]")
    sensors_overflow = [DamSensor(f"DAM-{i}", f"Section-{i//4}", 98 + np.random.rand()*2, 800​​​​​​​​​​​​​​​​
