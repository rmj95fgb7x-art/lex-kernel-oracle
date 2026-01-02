"""
KL-012-LEXGRID: Power Grid Stability Kernel
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
class GridSensor:
    sensor_id: str
    location: str
    voltage: float
    frequency_hz: float
    load_mw: float
    temperature_c: float
    timestamp: float


class LexGridKernel:
    def __init__(self):
        self.kernel = TemporalAdaptiveKernel(alpha=1.0, beta=0.95, lambda_jitter=0.2, drift_threshold=0.05)
        self.blackout_alerts = []
        self.timestep = 0
        self.readings = 0
    
    def monitor_grid(self, sensors: List[GridSensor]) -> Dict:
        signals = np.array([[s.voltage, s.frequency_hz, s.load_mw, s.temperature_c] for s in sensors])
        fused, weights = self.kernel.update(signals)
        voltage = fused[0]
        freq = fused[1]
        load = fused[2]
        temp = fused[3]
        voltage_ok = 110 <= voltage <= 130
        freq_ok = 59.95 <= freq <= 60.05
        overload = load > 1000
        blackout_risk = not voltage_ok or not freq_ok or overload
        if blackout_risk:
            self.blackout_alerts.append({'timestamp': datetime.now().isoformat(), 'voltage': float(voltage), 'frequency': float(freq), 'load': float(load), 'reason': 'VOLTAGE' if not voltage_ok else ('FREQUENCY' if not freq_ok else 'OVERLOAD')})
        failed = [s.sensor_id for i, s in enumerate(sensors) if weights[i] < 0.1]
        self.timestep += 1
        self.readings += len(sensors)
        return {'voltage': float(voltage), 'frequency_hz': float(freq), 'load_mw': float(load), 'temperature_c': float(temp), 'voltage_ok': voltage_ok, 'frequency_ok': freq_ok, 'overload': overload, 'blackout_risk': blackout_risk, 'failed_sensors': failed, 'timestep': self.timestep}
    
    def get_report(self) -> Dict:
        return {'timesteps': self.timestep, 'readings': self.readings, 'blackout_events': len(self.blackout_alerts), 'status': 'STABLE' if not self.blackout_alerts else 'UNSTABLE', 'royalty': (self.readings * 25) / 10000, 'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'}
    
    def export_log(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump({'kernel': 'kl-012-lexgrid', 'report': self.get_report(), 'alerts': self.blackout_alerts}, f, indent=2)


def main():
    kernel = LexGridKernel()
    print("="*60)
    print("KL-012-LEXGRID: Power Grid Monitoring")
    print("="*60)
    print("\n[NORMAL OPERATION]")
    sensors_normal = [GridSensor(f"GRID-{i}", f"Station-{i}", 120 + np.random.rand()*2, 60.0 + np.random.rand()*0.02, 500 + np.random.rand()*100, 25 + np.random.rand()*5, datetime.now().timestamp()) for i in range(10)]
    result = kernel.monitor_grid(sensors_normal)
    print(f"Voltage: {result['voltage']:.1f}V (OK: {result['voltage_ok']})")
    print(f"Frequency: {result['frequency_hz']:.3f}Hz (OK: {result['frequency_ok']})")
    print(f"Load: {result['load_mw']:.1f}MW (Overload: {result['overload']})")
    print(f"Blackout Risk: {result['blackout_risk']}")
    print("\n[VOLTAGE DROP]")
    sensors_drop = [GridSensor(f"GRID-{i}", f"Station-{i}", 95 + np.random.rand()*5, 60.0 + np.random.rand()*0.02, 500 + np.random.rand()*100, 25 + np.random.rand()*5, datetime.now().timestamp()) for i in range(10)]
    result = kernel.monitor_grid(sensors_drop)
    print(f"Voltage: {result['voltage']:.1f}V (OK: {result['voltage_ok']})")
    print(f"Frequency: {result['frequency_hz']:.3f}Hz (OK: {result['frequency_ok']})")
    print(f"⚠️  Blackout Risk: {result['blackout_risk']}")
    print("\n[OVERLOAD]")
    sensors_overload = [GridSensor(f"GRID-{i}", f"Station-{i}", 120 + np.random.rand()*2, 60.0 + np.random.rand()*0.02, 1100 + np.random.rand()*50, 35 + np.random.rand()*5, datetime.now().timestamp()) for i in range(10)]
    result = kernel.monitor_grid(sensors_overload)
    print(f"Load: {result['load_mw']:.1f}MW (Overload: {result['overload']})")
    print(f"Temperature: {result['temperature_c']:.1f}°C")
    print(f"⚠️  Blackout Risk: {result['blackout_risk']}")
    report = kernel.get_report()
    print(f"\n{'='*60}")
    print("GRID REPORT")
    print("="*60)
    print(f"Timesteps: {report['timesteps']}")
    print(f"Readings: {report['readings']}")
    print(f"Blackout Events: {report['blackout_events']}")
    print(f"Status: {report['status']}")
    print(f"Royalty: ${report['royalty']:.2f}")
    kernel.export_log('kl-012-lexgrid-log.json')


if __name__ == "__main__":
    main()
