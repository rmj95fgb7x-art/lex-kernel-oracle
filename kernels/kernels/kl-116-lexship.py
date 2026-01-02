"""
KL-116-LEXSHIP: Maritime Vessel Safety Kernel
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
class ShipSensor:
    sensor_id: str
    vessel_id: str
    latitude: float
    longitude: float
    heading_deg: float
    speed_knots: float
    roll_deg: float
    pitch_deg: float
    water_depth_m: float
    engine_temp_c: float
    fuel_level_pct: float
    timestamp: float


class LexShipKernel:
    def __init__(self):
        self.kernel = TemporalAdaptiveKernel(alpha=1.1, beta=0.96, lambda_jitter=0.3, drift_threshold=0.05)
        self.mayday_alerts = []
        self.timestep = 0
        self.readings = 0
    
    def monitor_vessel(self, sensors: List[ShipSensor]) -> Dict:
        signals = np.array([[s.speed_knots, s.roll_deg, s.pitch_deg, s.water_depth_m, s.engine_temp_c, s.fuel_level_pct] for s in sensors])
        fused, weights = self.kernel.update(signals)
        speed = fused[0]
        roll = fused[1]
        pitch = fused[2]
        depth = fused[3]
        temp = fused[4]
        fuel = fused[5]
        severe_roll = abs(roll) > 25
        severe_pitch = abs(pitch) > 15
        grounding = depth < 5
        engine_overheat = temp > 95
        fuel_critical = fuel < 10
        mayday = severe_roll or grounding or (severe_pitch and speed > 10)
        if mayday:
            self.mayday_alerts.append({'timestamp': datetime.now().isoformat(), 'roll': float(roll), 'pitch': float(pitch), 'depth': float(depth), 'speed': float(speed), 'reason': 'CAPSIZING' if severe_roll else ('GROUNDING' if grounding else 'SEVERE_PITCH')})
        failed = [s.sensor_id for i, s in enumerate(sensors) if weights[i] < 0.05]
        self.timestep += 1
        self.readings += len(sensors)
        return {'speed_knots': float(speed), 'roll_deg': float(roll), 'pitch_deg': float(pitch), 'water_depth_m': float(depth), 'engine_temp_c': float(temp), 'fuel_pct': float(fuel), 'severe_roll': severe_roll, 'severe_pitch': severe_pitch, 'grounding_risk': grounding, 'engine_overheat': engine_overheat, 'fuel_critical': fuel_critical, 'mayday': mayday, 'failed_sensors': failed, 'timestep': self.timestep}
    
    def get_report(self) -> Dict:
        return {'timesteps': self.timestep, 'readings': self.readings, 'mayday_events': len(self.mayday_alerts), 'event_rate': len(self.mayday_alerts)/max(1, self.timestep), 'royalty': (self.readings * 25) / 10000, 'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'}
    
    def export_log(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump({'kernel': 'kl-116-lexship', 'report': self.get_report(), 'alerts': self.mayday_alerts}, f, indent=2)


def main():
    kernel = LexShipKernel()
    print("="*60)
    print("KL-116-LEXSHIP: Maritime Vessel Safety")
    print("="*60)
    print("\n[CALM SEAS]")
    sensors_calm = [ShipSensor(f"NAV-{i}", "VESSEL-001", 40.7 + np.random.rand()*0.1, -74.0 + np.random.rand()*0.1, 270 + np.random.rand()*5, 15 + np.random.rand()*2, 3 + np.random.rand()*2, 2 + np.random.rand(), 50 + np.random.rand()*20, 65 + np.random.rand()*10, 75 + np.random.rand()*10, datetime.now().timestamp()) for i in range(12)]
    result = kernel.monitor_vessel(sensors_calm)
    print(f"Speed: {result['speed_knots']:.1f} knots")
    print(f"Roll: {result['roll_deg']:.1f}°")
    print(f"Pitch: {result['pitch_deg']:.1f}°")
    print(f"Depth: {result['water_depth_m']:.1f}m")
    print(f"Mayday: {result['mayday']}")
    print("\n[HEAVY SEAS - CAPSIZING RISK]")
    sensors_heavy = [ShipSensor(f"NAV-{i}", "VESSEL-001", 40.7 + np.random.rand()*0.1, -74.0 + np.random.rand()*0.1, 270 + np.random.rand()*5, 8 + np.random.rand()*2, 28 + np.random.rand()*4, 17 + np.random.rand()*3, 50 + np.random.rand()*20, 65 + np.random.rand()*10, 75 + np.random.rand()*10, datetime.now().timestamp()) for i in range(12)]
    result = kernel.monitor_vessel(sensors_heavy)
    print(f"Roll: {result['roll_deg']:.1f}°")
    print(f"Pitch: {result['pitch_deg']:.1f}°")
    print(f"🚨 Severe Roll: {result['severe_roll']}")
    print(f"🚨 Severe Pitch: {result['severe_pitch']}")
    print(f"🚨 MAYDAY: {result['mayday']}")
    print("\n[GROUNDING RISK]")
    sensors_ground = [ShipSensor(f"NAV-{i}", "VESSEL-001", 40.7 + np.random.rand()*0.1, -74.0 + np.random.rand()*0.1, 270 + np.random.rand()*5, 12 + np.random.rand()*2, 5 + np.random.rand()*2, 3 + np.random.rand(), 3.5 + np.random.rand(), 65 + np.random.rand()*10, 75 + np.random.rand()*10, datetime.now().timestamp()) for i in range(12)]
    result = kernel.monitor_vessel(sensors_ground)
    print(f"Water Depth: {result['water_depth_m']:.1f}m")
    print(f"🚨 Grounding Risk: {result['grounding_risk']}")
    print(f"🚨 MAYDAY: {result['mayday']}")
    report = kernel.get_report()
    print(f"\n{'='*60}")
    print("MARITIME SAFETY REPORT")
    print("="*60)
    print(f"Timesteps: {report['timesteps']}")
    print(f"Readings: {report['readings']}")
    print(f"Mayday Events: {report['mayday_events']}")
    print(f"Event Rate: {report['event_rate']:.1%}")
    print(f"Royalty: ${report['royalty']:.2f}")
    kernel.export_log('kl-116-lexship-log.json')


if __name__ == "__main__":
    main()
