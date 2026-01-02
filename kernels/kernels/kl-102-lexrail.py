"""
KL-102-LEXRAIL: Railway Safety Kernel
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
class RailSensor:
    sensor_id: str
    track_id: str
    rail_temp_c: float
    vibration_mm_s: float
    track_gauge_mm: float
    rail_wear_mm: float
    train_speed_kph: float
    brake_pressure_bar: float
    timestamp: float


class LexRailKernel:
    def __init__(self):
        self.kernel = TemporalAdaptiveKernel(alpha=1.0, beta=0.95, lambda_jitter=0.25, drift_threshold=0.05)
        self.derail_alerts = []
        self.timestep = 0
        self.readings = 0
    
    def monitor_railway(self, sensors: List[RailSensor]) -> Dict:
        signals = np.array([[s.rail_temp_c, s.vibration_mm_s, s.track_gauge_mm, s.rail_wear_mm, s.train_speed_kph, s.brake_pressure_bar] for s in sensors])
        fused, weights = self.kernel.update(signals)
        temp = fused[0]
        vib = fused[1]
        gauge = fused[2]
        wear = fused[3]
        speed = fused[4]
        brake = fused[5]
        temp_buckle = temp > 55
        high_vib = vib > 15
        gauge_wide = gauge > 1440
        gauge_narrow = gauge < 1430
        excess_wear = wear > 12
        overspeed = speed > 120
        brake_fail = brake < 3.5
        derail_risk = temp_buckle or high_vib or gauge_wide or gauge_narrow or (overspeed and brake_fail)
        if derail_risk:
            self.derail_alerts.append({'timestamp': datetime.now().isoformat(), 'temp': float(temp), 'vibration': float(vib), 'gauge': float(gauge), 'speed': float(speed), 'brake': float(brake), 'reason': 'BUCKLE' if temp_buckle else ('VIBRATION' if high_vib else ('GAUGE' if (gauge_wide or gauge_narrow) else 'BRAKE'))})
        failed = [s.sensor_id for i, s in enumerate(sensors) if weights[i] < 0.05]
        self.timestep += 1
        self.readings += len(sensors)
        return {'rail_temp_c': float(temp), 'vibration_mm_s': float(vib), 'track_gauge_mm': float(gauge), 'rail_wear_mm': float(wear), 'train_speed_kph': float(speed), 'brake_pressure_bar': float(brake), 'temp_buckle': temp_buckle, 'high_vibration': high_vib, 'gauge_deviation': gauge_wide or gauge_narrow, 'excess_wear': excess_wear, 'overspeed': overspeed, 'brake_failure': brake_fail, 'derailment_risk': derail_risk, 'failed_sensors': failed, 'timestep': self.timestep}
    
    def get_report(self) -> Dict:
        return {'timesteps': self.timestep, 'readings': self.readings, 'derail_alerts': len(self.derail_alerts), 'alert_rate': len(self.derail_alerts)/max(1, self.timestep), 'royalty': (self.readings * 25) / 10000, 'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'}
    
    def export_log(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump({'kernel': 'kl-102-lexrail', 'report': self.get_report(), 'alerts': self.derail_alerts}, f, indent=2)


def main():
    kernel = LexRailKernel()
    print("="*60)
    print("KL-102-LEXRAIL: Railway Safety Monitoring")
    print("="*60)
    print("\n[NORMAL OPERATION]")
    sensors_normal = [RailSensor(f"RAIL-{i}", f"Track-{i//5}", 35 + np.random.rand()*5, 8 + np.random.rand()*2, 1435 + np.random.rand()*2, 5 + np.random.rand()*2, 80 + np.random.rand()*20, 5.5 + np.random.rand()*0.5, datetime.now().timestamp()) for i in range(25)]
    result = kernel.monitor_railway(sensors_normal)
    print(f"Rail Temp: {result['rail_temp_c']:.1f}°C")
    print(f"Vibration: {result['vibration_mm_s']:.1f} mm/s")
    print(f"Track Gauge: {result['track_gauge_mm']:.1f} mm")
    print(f"Speed: {result['train_speed_kph']:.0f} kph")
    print(f"Derailment Risk: {result['derailment_risk']}")
    print("\n[HEAT BUCKLE RISK]")
    sensors_hot = [RailSensor(f"RAIL-{i}", f"Track-{i//5}", 58 + np.random.rand()*3, 8 + np.random.rand()*2, 1435 + np.random.rand()*2, 5 + np.random.rand()*2, 80 + np.random.rand()*20, 5.5 + np.random.rand()*0.5, datetime.now().timestamp()) for i in range(25)]
    result = kernel.monitor_railway(sensors_hot)
    print(f"Rail Temp: {result['rail_temp_c']:.1f}°C")
    print(f"🚨 Temp Buckle Risk: {result['temp_buckle']}")
    print(f"🚨 Derailment Risk: {result['derailment_risk']}")
    print("\n[TRACK GAUGE DEVIATION]")
    sensors_gauge = [RailSensor(f"RAIL-{i}", f"Track-{i//5}", 35 + np.random.rand()*5, 8 + np.random.rand()*2, 1445 + np.random.rand()*3, 5 + np.random.rand()*2, 80 + np.random.rand()*20, 5.5 + np.random.rand()*0.5, datetime.now().timestamp()) for i in range(25)]
    result = kernel.monitor_railway(sensors_gauge)
    print(f"Track Gauge: {result['track_gauge_mm']:.1f} mm")
    print(f"🚨 Gauge Deviation: {result['gauge_deviation']}")
    print(f"🚨 Derailment Risk: {result['derailment_risk']}")
    print("\n[BRAKE FAILURE + OVERSPEED]")
    sensors_brake = [RailSensor(f"RAIL-{i}", f"Track-{i//5}", 35 + np.random.rand()*5, 8 + np.random.rand()*2, 1435 + np.random.rand()*2, 5 + np.random.rand()*2, 135 + np.random.rand()*10​​​​​​​​​​​​​​​​
