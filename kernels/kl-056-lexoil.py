"""
KL-056-LEXOIL: Oil Pipeline Safety Kernel
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
class PipelineSensor:
    sensor_id: str
    location_km: float
    pressure_psi: float
    flow_rate_bbl_day: float
    temperature_c: float
    vibration_hz: float
    leak_detected: bool
    timestamp: float


class LexOilKernel:
    def __init__(self):
        self.kernel = TemporalAdaptiveKernel(alpha=0.9, beta=0.97, lambda_jitter=0.2, drift_threshold=0.05)
        self.leak_alerts = []
        self.timestep = 0
        self.sensors_read = 0
    
    def monitor_pipeline(self, sensors: List[PipelineSensor]) -> Dict:
        signals = np.array([[s.pressure_psi, s.flow_rate_bbl_day, s.temperature_c, s.vibration_hz, 1.0 if s.leak_detected else 0.0] for s in sensors])
        fused, weights = self.kernel.update(signals)
        pressure = fused[0]
        flow = fused[1]
        temp = fused[2]
        vibration = fused[3]
        leak_prob = fused[4]
        pressure_ok = 500 <= pressure <= 1500
        flow_ok = flow > 10000
        temp_ok = temp < 80
        vibration_ok = vibration < 50
        leak_risk = leak_prob > 0.3 or not pressure_ok or vibration > 60
        if leak_risk:
            self.leak_alerts.append({'timestamp': datetime.now().isoformat(), 'pressure': float(pressure), 'flow': float(flow), 'leak_prob': float(leak_prob), 'reason': 'LEAK_DETECTED' if leak_prob > 0.3 else ('PRESSURE' if not pressure_ok else 'VIBRATION')})
        failed = [s.sensor_id for i, s in enumerate(sensors) if weights[i] < 0.05]
        self.timestep += 1
        self.sensors_read += len(sensors)
        return {'pressure_psi': float(pressure), 'flow_bbl_day': float(flow), 'temperature_c': float(temp), 'vibration_hz': float(vibration), 'leak_probability': float(leak_prob), 'leak_risk': leak_risk, 'pressure_ok': pressure_ok, 'flow_ok': flow_ok, 'failed_sensors': failed, 'timestep': self.timestep}
    
    def get_report(self) -> Dict:
        return {'timesteps': self.timestep, 'sensors': self.sensors_read, 'leak_events': len(self.leak_alerts), 'safety_rate': 1 - (len(self.leak_alerts)/max(1, self.timestep)), 'royalty': (self.sensors_read * 25) / 10000, 'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'}
    
    def export_log(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump({'kernel': 'kl-056-lexoil', 'report': self.get_report(), 'alerts': self.leak_alerts}, f, indent=2)


def main():
    kernel = LexOilKernel()
    print("="*60)
    print("KL-056-LEXOIL: Pipeline Safety Monitoring")
    print("="*60)
    print("\n[NORMAL OPERATION]")
    sensors_normal = [PipelineSensor(f"SENSOR-{i}", i*10.0, 1000 + np.random.rand()*100, 50000 + np.random.rand()*5000, 45 + np.random.rand()*5, 20 + np.random.rand()*5, False, datetime.now().timestamp()) for i in range(15)]
    result = kernel.monitor_pipeline(sensors_normal)
    print(f"Pressure: {result['pressure_psi']:.1f} psi (OK: {result['pressure_ok']})")
    print(f"Flow: {result['flow_bbl_day']:.0f} bbl/day (OK: {result['flow_ok']})")
    print(f"Temperature: {result['temperature_c']:.1f}°C")
    print(f"Leak Risk: {result['leak_risk']}")
    print("\n[PRESSURE DROP - LEAK SUSPECTED]")
    sensors_leak = [PipelineSensor(f"SENSOR-{i}", i*10.0, 400 + np.random.rand()*50 if i > 7 else 1000 + np.random.rand()*100, 30000 + np.random.rand()*5000 if i > 7 else 50000 + np.random.rand()*5000, 45 + np.random.rand()*5, 20 + np.random.rand()*5, i == 8, datetime.now().timestamp()) for i in range(15)]
    result = kernel.monitor_pipeline(sensors_leak)
    print(f"Pressure: {result['pressure_psi']:.1f} psi (OK: {result['pressure_ok']})")
    print(f"Flow: {result['flow_bbl_day']:.0f} bbl/day (OK: {result['flow_ok']})")
    print(f"Leak Probability: {result['leak_probability']:.2f}")
    print(f"⚠️  Leak Risk: {result['leak_risk']}")
    if result['failed_sensors']:
        print(f"Failed Sensors: {result['failed_sensors']}")
    report = kernel.get_report()
    print(f"\n{'='*60}")
    print("PIPELINE SAFETY REPORT")
    print("="*60)
    print(f"Timesteps: {report['timesteps']}")
    print(f"Sensors: {report['sensors']}")
    print(f"Leak Events: {report['leak_events']}")
    print(f"Safety Rate: {report['safety_rate']:.1%}")
    print(f"Royalty: ${report['royalty']:.2f}")
    kernel.export_log('kl-056-lexoil-log.json')


if __name__ == "__main__":
    main()
