"""
KL-123-LEXFIRE: Wildfire Detection Kernel
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
class FireSensor:
    sensor_id: str
    location: str
    latitude: float
    longitude: float
    temperature_c: float
    smoke_ppm: float
    co_ppm: float
    humidity_pct: float
    wind_speed_kph: float
    infrared_intensity: float
    timestamp: float


class LexFireKernel:
    def __init__(self):
        self.kernel = TemporalAdaptiveKernel(alpha=0.95, beta=0.94, lambda_jitter=0.25, drift_threshold=0.06)
        self.fire_alerts = []
        self.timestep = 0
        self.readings = 0
    
    def detect_fire(self, sensors: List[FireSensor]) -> Dict:
        signals = np.array([[s.temperature_c, s.smoke_ppm, s.co_ppm, s.humidity_pct, s.wind_speed_kph, s.infrared_intensity] for s in sensors])
        fused, weights = self.kernel.update(signals)
        temp = fused[0]
        smoke = fused[1]
        co = fused[2]
        humidity = fused[3]
        wind = fused[4]
        ir = fused[5]
        high_temp = temp > 60
        smoke_detected = smoke > 100
        co_elevated = co > 50
        dry_conditions = humidity < 30
        high_wind = wind > 40
        ir_hotspot = ir > 500
        fire_detected = (high_temp and smoke_detected) or (ir_hotspot and smoke_detected)
        severe = fire_detected and (high_wind or dry_conditions)
        if fire_detected:
            fire_lat = np.average([s.latitude for s in sensors], weights=weights)
            fire_lon = np.average([s.longitude for s in sensors], weights=weights)
            self.fire_alerts.append({'timestamp': datetime.now().isoformat(), 'location': [float(fire_lat), float(fire_lon)], 'temp': float(temp), 'smoke': float(smoke), 'wind': float(wind), 'severe': severe})
        failed = [s.sensor_id for i, s in enumerate(sensors) if weights[i] < 0.06]
        self.timestep += 1
        self.readings += len(sensors)
        return {'temperature_c': float(temp), 'smoke_ppm': float(smoke), 'co_ppm': float(co), 'humidity_pct': float(humidity), 'wind_speed_kph': float(wind), 'ir_intensity': float(ir), 'high_temp': high_temp, 'smoke_detected': smoke_detected, 'dry_conditions': dry_conditions, 'high_wind': high_wind, 'fire_detected': fire_detected, 'severe_fire': severe, 'failed_sensors': failed, 'timestep': self.timestep}
    
    def get_report(self) -> Dict:
        return {'timesteps': self.timestep, 'readings': self.readings, 'fires_detected': len(self.fire_alerts), 'severe_fires': sum(1 for a in self.fire_alerts if a['severe']), 'royalty': (self.readings * 25) / 10000, 'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'}
    
    def export_log(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump({'kernel': 'kl-123-lexfire', 'report': self.get_report(), 'alerts': self.fire_alerts}, f, indent=2)


def main():
    kernel = LexFireKernel()
    print("="*60)
    print("KL-123-LEXFIRE: Wildfire Detection System")
    print("="*60)
    print("\n[NORMAL CONDITIONS]")
    sensors_normal = [FireSensor(f"FIRE-{i}", f"Zone-{i//5}", 34.0 + np.random.rand()*0.5, -118.0 + np.random.rand()*0.5, 28 + np.random.rand()*5, 10 + np.random.rand()*5, 5 + np.random.rand()*2, 55 + np.random.rand()*10, 15 + np.random.rand()*5, 100 + np.random.rand()*50, datetime.now().timestamp()) for i in range(20)]
    result = kernel.detect_fire(sensors_normal)
    print(f"Temperature: {result['temperature_c']:.1f}°C")
    print(f"Smoke: {result['smoke_ppm']:.1f} ppm")
    print(f"Humidity: {result['humidity_pct']:.1f}%")
    print(f"Wind: {result['wind_speed_kph']:.1f} kph")
    print(f"Fire Detected: {result['fire_detected']}")
    print("\n[FIRE DETECTED]")
    sensors_fire = [FireSensor(f"FIRE-{i}", f"Zone-{i//5}", 34.0 + np.random.rand()*0.5, -118.0 + np.random.rand()*0.5, 75 + np.random.rand()*15, 250 + np.random.rand()*100, 80 + np.random.rand()*20, 25 + np.random.rand()*10, 20 + np.random.rand()*10, 800 + np.random.rand()*200, datetime.now().timestamp()) for i in range(20)]
    result = kernel.detect_fire(sensors_fire)
    print(f"Temperature: {result['temperature_c']:.1f}°C")
    print(f"Smoke: {result['smoke_ppm']:.1f} ppm")
    print(f"IR Intensity: {result['ir_intensity']:.0f}")
    print(f"🔥 Fire Detected: {result['fire_detected']}")
    print("\n[SEVERE FIRE - HIGH WIND]")
    sensors_severe = [FireSensor(f"FIRE-{i}", f"Zone-{i//5}", 34.0 + np.random.rand()*0.5, -118.0 + np.random.rand()*0.5, 95 + np.random.rand()*20, 400 + np.random.rand()*150, 120 + np.random.rand()*30, 15 + np.random.rand()*5, 55 + np.random.rand()*15, 1200 + np.random.rand()*300, datetime.now().timestamp()) for i in range(20)]
    result = kernel.detect_fire(sensors_severe)
    print(f"Temperature: {result['temperature_c']:.1f}°C")
    print(f"Smoke: {result['smoke_ppm']:.1f} ppm")
    print(f"Wind: {result['wind_speed_kph']:.1f} kph")
    print(f"Humidity: {result['humidity_pct']:.1f}%")
    print(f"🔥 Fire Detected: {result['fire_detected']}")
    print(f"🚨 SEVERE FIRE: {result['severe_fire']}")
    report = kernel.get_report()
    print(f"\n{'='*60}")
    print("WILDFIRE DETECTION REPORT")
    print("="*60)
    print(f"Timesteps: {report['timesteps']}")
    print(f"Readings: {report['readings']}")
    print(f"Fires Detected: {report['fires_detected']}")
    print(f"Severe Fires: {report['severe_fires']}")
    print(f"Royalty: ${report['royalty']:.2f}")
    kernel.export_log('kl-123-lexfire-log.json')


if __name__ == "__main__":
    main()
