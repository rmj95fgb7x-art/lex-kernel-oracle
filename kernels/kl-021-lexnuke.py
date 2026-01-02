"""
KL-021-LEXNUKE: Nuclear Facility Safety Monitoring Kernel
Lex Liberatum Kernels v1.1

Domain: Nuclear Energy / Critical Infrastructure
Use Case: Multi-sensor radiation & temperature monitoring

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
class RadiationReading:
    sensor_id: str
    location: str
    radiation_mrem_hr: float
    temperature_c: float
    pressure_bar: float
    neutron_flux: float
    timestamp: float


class LexNukeKernel:
    def __init__(self):
        self.kernel = TemporalAdaptiveKernel(alpha=1.0, beta=0.99, lambda_jitter=0.1, drift_threshold=0.05)
        self.critical_alerts = []
        self.timestep = 0
        self.readings_processed = 0
    
    def process_readings(self, readings: List[RadiationReading]) -> Dict:
        signals = np.array([[r.radiation_mrem_hr, r.temperature_c, r.pressure_bar, r.neutron_flux] for r in readings])
        fused, weights = self.kernel.update(signals)
        
        radiation = fused[0]
        temp = fused[1]
        pressure = fused[2]
        neutron = fused[3]
        
        if radiation < 5:
            status = "normal"
        elif radiation < 10:
            status = "elevated"
        elif radiation < 50:
            status = "high"
        else:
            status = "CRITICAL"
        
        shutdown = (radiation > 50) or (temp > 400) or (pressure > 2.0)
        
        if shutdown:
            alert = {'timestamp': datetime.now().isoformat(), 'radiation': float(radiation), 'temperature': float(temp), 'pressure': float(pressure), 'reason': 'RADIATION' if radiation > 50 else ('TEMPERATURE' if temp > 400 else 'PRESSURE')}
            self.critical_alerts.append(alert)
        
        failed_sensors = [r.sensor_id for i, r in enumerate(readings) if weights[i] < 0.1]
        
        self.timestep += 1
        self.readings_processed += len(readings)
        
        return {
            'radiation_mrem_hr': float(radiation),
            'temperature_c': float(temp),
            'pressure_bar': float(pressure),
            'neutron_flux': float(neutron),
            'safety_status': status,
            'recommend_shutdown': shutdown,
            'failed_sensors': failed_sensors,
            'timestep': self.timestep,
            'sensor_weights': {readings[i].sensor_id: float(weights[i]) for i in range(len(readings))}
        }
    
    def get_safety_report(self) -> Dict:
        return {'facility': 'SITE-001', 'monitoring_duration': self.timestep, 'readings_processed': self.readings_processed, 'critical_events': len(self.critical_alerts), 'last_critical': self.critical_alerts[-1] if self.critical_alerts else None, 'status': 'SAFE' if not self.critical_alerts else 'REVIEW_REQUIRED', 'royalty': (self.readings_processed * 25) / 10000, 'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'}
    
    def export_log(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump({'kernel': 'kl-021-lexnuke', 'report': self.get_safety_report(), 'critical_alerts': self.critical_alerts}, f, indent=2)


def main():
    kernel = LexNukeKernel()
    
    print("="*60)
    print("KL-021-LEXNUKE: Nuclear Safety Monitoring")
    print("="*60)
    
    print("\n[SCENARIO 1: Normal Operation]")
    readings_normal = [RadiationReading(f"RAD-{i}", f"Zone-{i//2}", 2.5 + np.random.rand(), 85 + np.random.rand()*10, 1.01, 1e12 + np.random.rand()*1e11, datetime.now().timestamp()) for i in range(10)]
    result = kernel.process_readings(readings_normal)
    print(f"Radiation: {result['radiation_mrem_hr']:.2f} mrem/hr")
    print(f"Temperature: {result['temperature_c']:.1f}°C")
    print(f"Status: {result['safety_status']}")
    print(f"Shutdown: {result['recommend_shutdown']}")
    
    print("\n[SCENARIO 2: Elevated Radiation]")
    readings_elevated = [RadiationReading(f"RAD-{i}", f"Zone-{i//2}", 7.0 + np.random.rand()*2, 95 + np.random.rand()*10, 1.05, 2e12 + np.random.rand()*5e11, datetime.now().timestamp()) for i in range(10)]
    result = kernel.process_readings(readings_elevated)
    print(f"Radiation: {result['radiation_mrem_hr']:.2f} mrem/hr")
    print(f"Temperature: {result['temperature_c']:.1f}°C")
    print(f"Status: {result['safety_status']}")
    print(f"Shutdown: {result['recommend_shutdown']}")
    
    print("\n[SCENARIO 3: CRITICAL EVENT]")
    readings_critical = [RadiationReading(f"RAD-{i}", f"Zone-{i//2}", 55.0 + np.random.rand()*10, 350 + np.random.rand()*50, 1.5, 5e13, datetime.now().timestamp()) for i in range(10)]
    result = kernel.process_readings(readings_critical)
    print(f"⚠️  CRITICAL ALERT")
    print(f"Radiation: {result['radiation_mrem_hr']:.2f} mrem/hr")
    print(f"Temperature: {result['temperature_c']:.1f}°C")
    print(f"Pressure: {result['pressure_bar']:.2f} bar")
    print(f"Status: {result['safety_status']}")
    print(f"Shutdown: {result['recommend_shutdown']}")
    if result['failed_sensors']:
        print(f"Failed Sensors: {result['failed_sensors']}")
    
    report = kernel.get_safety_report()
    print(f"\n{'='*60}")
    print("SAFETY REPORT")
    print("="*60)
    print(f"Facility: {report['facility']}")
    print(f"Monitoring Duration: {report['monitoring_duration']} timesteps")
    print(f"Readings Processed: {report['readings_processed']}")
    print(f"Critical Events: {report['critical_events']}")
    print(f"Status: {report['status']}")
    print(f"Royalty: ${report['royalty']:.2f}")
    
    kernel.export_log('kl-021-lexnuke-log.json')
    print(f"\nLog exported to: kl-021-lexnuke-log.json")


if __name__ == "__main__":
    main()
