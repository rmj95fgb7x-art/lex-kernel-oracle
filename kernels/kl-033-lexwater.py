"""
KL-033-LEXWATER: Water Quality Monitoring Kernel
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
class WaterSample:
    sample_id: str
    location: str
    ph_level: float
    turbidity_ntu: float
    dissolved_oxygen_mg_l: float
    chlorine_mg_l: float
    bacteria_cfu_100ml: int
    temperature_c: float
    timestamp: float


class LexWaterKernel:
    def __init__(self):
        self.kernel = TemporalAdaptiveKernel(alpha=1.1, beta=0.96, lambda_jitter=0.3, drift_threshold=0.06)
        self.contamination_alerts = []
        self.timestep = 0
        self.samples = 0
    
    def monitor_water(self, samples: List[WaterSample]) -> Dict:
        signals = np.array([[s.ph_level, s.turbidity_ntu, s.dissolved_oxygen_mg_l, s.chlorine_mg_l, s.bacteria_cfu_100ml, s.temperature_c] for s in samples])
        fused, weights = self.kernel.update(signals)
        ph = fused[0]
        turbidity = fused[1]
        oxygen = fused[2]
        chlorine = fused[3]
        bacteria = fused[4]
        temp = fused[5]
        ph_ok = 6.5 <= ph <= 8.5
        turbidity_ok = turbidity < 5.0
        oxygen_ok = oxygen > 5.0
        chlorine_ok = 0.2 <= chlorine <= 4.0
        bacteria_ok = bacteria < 100
        safe = ph_ok and turbidity_ok and oxygen_ok and chlorine_ok and bacteria_ok
        if not safe:
            self.contamination_alerts.append({'timestamp': datetime.now().isoformat(), 'ph': float(ph), 'turbidity': float(turbidity), 'bacteria': float(bacteria), 'safe': safe})
        failed = [s.sample_id for i, s in enumerate(samples) if weights[i] < 0.06]
        self.timestep += 1
        self.samples += len(samples)
        return {'ph': float(ph), 'turbidity': float(turbidity), 'oxygen': float(oxygen), 'chlorine': float(chlorine), 'bacteria': float(bacteria), 'temperature': float(temp), 'safe': safe, 'ph_ok': ph_ok, 'turbidity_ok': turbidity_ok, 'oxygen_ok': oxygen_ok, 'chlorine_ok': chlorine_ok, 'bacteria_ok': bacteria_ok, 'failed_samples': failed, 'timestep': self.timestep}
    
    def get_report(self) -> Dict:
        return {'timesteps': self.timestep, 'samples': self.samples, 'contamination_events': len(self.contamination_alerts), 'safety_rate': 1 - (len(self.contamination_alerts)/max(1, self.timestep)), 'royalty': (self.samples * 25) / 10000, 'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'}
    
    def export_log(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump({'kernel': 'kl-033-lexwater', 'report': self.get_report(), 'alerts': self.contamination_alerts}, f, indent=2)


def main():
    kernel = LexWaterKernel()
    print("="*60)
    print("KL-033-LEXWATER: Water Quality Monitoring")
    print("="*60)
    print("\n[SAFE WATER]")
    samples_safe = [WaterSample(f"SAMPLE-{i}", f"Station-{i}", 7.2 + np.random.rand()*0.5, 1.5 + np.random.rand()*0.5, 8.0 + np.random.rand(), 1.0 + np.random.rand()*0.5, int(20 + np.random.rand()*30), 18 + np.random.rand()*2, datetime.now().timestamp()) for i in range(10)]
    result = kernel.monitor_water(samples_safe)
    print(f"pH: {result['ph']:.2f} (OK: {result['ph_ok']})")
    print(f"Turbidity: {result['turbidity']:.2f} NTU (OK: {result['turbidity_ok']})")
    print(f"Bacteria: {result['bacteria']:.0f} CFU/100ml (OK: {result['bacteria_ok']})")
    print(f"Safe: {result['safe']}")
    print("\n[CONTAMINATION]")
    samples_contaminated = [WaterSample(f"SAMPLE-{i}", f"Station-{i}", 5.5 + np.random.rand()*0.5, 8.0 + np.random.rand()*2, 3.0 + np.random.rand(), 0.5 + np.random.rand()*0.3, int(200 + np.random.rand()*100), 18 + np.random.rand()*2, datetime.now().timestamp()) for i in range(10)]
    result = kernel.monitor_water(samples_contaminated)
    print(f"pH: {result['ph']:.2f} (OK: {result['ph_ok']})")
    print(f"Turbidity: {result['turbidity']:.2f} NTU (OK: {result['turbidity_ok']})")
    print(f"Oxygen: {result['oxygen']:.2f} mg/L (OK: {result['oxygen_ok']})")
    print(f"Bacteria: {result['bacteria']:.0f} CFU/100ml (OK: {result['bacteria_ok']})")
    print(f"⚠️  Safe: {result['safe']}")
    report = kernel.get_report()
    print(f"\n{'='*60}")
    print("WATER QUALITY REPORT")
    print("="*60)
    print(f"Timesteps: {report['timesteps']}")
    print(f"Samples: {report['samples']}")
    print(f"Contamination Events: {report['contamination_events']}")
    print(f"Safety Rate: {report['safety_rate']:.1%}")
    print(f"Royalty: ${report['royalty']:.2f}")
    kernel.export_log('kl-033-lexwater-log.json')


if __name__ == "__main__":
    main()
