"""
KL-062-LEXTRAFFIC: Smart City Traffic Fusion Kernel
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
class TrafficSensor:
    sensor_id: str
    intersection: str
    vehicle_count: int
    avg_speed_mph: float
    congestion_level: float
    accident_detected: bool
    air_quality_aqi: float
    timestamp: float


class LexTrafficKernel:
    def __init__(self):
        self.kernel = TemporalAdaptiveKernel(alpha=1.3, beta=0.94, lambda_jitter=0.35, drift_threshold=0.07)
        self.incidents = []
        self.timestep = 0
        self.readings = 0
    
    def monitor_traffic(self, sensors: List[TrafficSensor]) -> Dict:
        signals = np.array([[s.vehicle_count, s.avg_speed_mph, s.congestion_level, 1.0 if s.accident_detected else 0.0, s.air_quality_aqi] for s in sensors])
        fused, weights = self.kernel.update(signals)
        vehicles = fused[0]
        speed = fused[1]
        congestion = fused[2]
        accident_prob = fused[3]
        aqi = fused[4]
        severe_congestion = congestion > 0.8
        accident_likely = accident_prob > 0.2
        poor_air = aqi > 150
        incident = severe_congestion or accident_likely or poor_air
        if incident:
            self.incidents.append({'timestamp': datetime.now().isoformat(), 'vehicles': float(vehicles), 'speed': float(speed), 'congestion': float(congestion), 'accident_prob': float(accident_prob), 'aqi': float(aqi)})
        failed = [s.sensor_id for i, s in enumerate(sensors) if weights[i] < 0.07]
        self.timestep += 1
        self.readings += len(sensors)
        return {'vehicle_count': float(vehicles), 'avg_speed_mph': float(speed), 'congestion_level': float(congestion), 'accident_probability': float(accident_prob), 'aqi': float(aqi), 'severe_congestion': severe_congestion, 'accident_likely': accident_likely, 'poor_air_quality': poor_air, 'incident_detected': incident, 'failed_sensors': failed, 'timestep': self.timestep}
    
    def get_report(self) -> Dict:
        return {'timesteps': self.timestep, 'readings': self.readings, 'incidents': len(self.incidents), 'incident_rate': len(self.incidents)/max(1, self.timestep), 'royalty': (self.readings * 25) / 10000, 'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'}
    
    def export_log(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump({'kernel': 'kl-062-lextraffic', 'report': self.get_report(), 'incidents': self.incidents}, f, indent=2)


def main():
    kernel = LexTrafficKernel()
    print("="*60)
    print("KL-062-LEXTRAFFIC: Smart City Traffic Monitoring")
    print("="*60)
    print("\n[NORMAL TRAFFIC]")
    sensors_normal = [TrafficSensor(f"CAM-{i}", f"Int-{i}", int(150 + np.random.rand()*50), 35 + np.random.rand()*10, 0.3 + np.random.rand()*0.2, False, 50 + np.random.rand()*20, datetime.now().timestamp()) for i in range(20)]
    result = kernel.monitor_traffic(sensors_normal)
    print(f"Vehicles: {result['vehicle_count']:.0f}")
    print(f"Avg Speed: {result['avg_speed_mph']:.1f} mph")
    print(f"Congestion: {result['congestion_level']:.2f}")
    print(f"Incident: {result['incident_detected']}")
    print("\n[HEAVY CONGESTION]")
    sensors_congested = [TrafficSensor(f"CAM-{i}", f"Int-{i}", int(400 + np.random.rand()*100), 5 + np.random.rand()*3, 0.85 + np.random.rand()*0.1, False, 120 + np.random.rand()*30, datetime.now().timestamp()) for i in range(20)]
    result = kernel.monitor_traffic(sensors_congested)
    print(f"Vehicles: {result['vehicle_count']:.0f}")
    print(f"Avg Speed: {result['avg_speed_mph']:.1f} mph")
    print(f"Congestion: {result['congestion_level']:.2f}")
    print(f"AQI: {result['aqi']:.0f}")
    print(f"⚠️  Severe Congestion: {result['severe_congestion']}")
    print(f"⚠️  Poor Air Quality: {result['poor_air_quality']}")
    print("\n[ACCIDENT]")
    sensors_accident = [TrafficSensor(f"CAM-{i}", f"Int-{i}", int(300 + np.random.rand()*50), 8 + np.random.rand()*5, 0.7 + np.random.rand()*0.1, i == 10, 80 + np.random.rand()*20, datetime.now().timestamp()) for i in range(20)]
    result = kernel.monitor_traffic(sensors_accident)
    print(f"Accident Probability: {result['accident_probability']:.2f}")
    print(f"⚠️  Accident Likely: {result['accident_likely']}")
    report = kernel.get_report()
    print(f"\n{'='*60}")
    print("TRAFFIC REPORT")
    print("="*60)
    print(f"Timesteps: {report['timesteps']}")
    print(f"Readings: {report['readings']}")
    print(f"Incidents: {report['incidents']}")
    print(f"Incident Rate: {report['incident_rate']:.1%}")
    print(f"Royalty: ${report['royalty']:.2f}")
    kernel.export_log('kl-062-lextraffic-log.json')


if __name__ == "__main__":
    main()
