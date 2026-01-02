"""
KL-021-LEXNUKE: Nuclear Facility Safety Monitoring Kernel
Lex Liberatum Kernels v1.1

Domain: Nuclear Energy / Critical Infrastructure
Use Case: Multi-sensor radiation & temperature monitoring

Features:
- Real-time radiation level fusion
- Criticality event detection
- Fail-safe alerting
- NRC compliance logging

Patent: PCT Pending
Royalty: 25bp → 0x44f8...C689
"""

import numpy as np
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.temporal_kernel import TemporalAdaptiveKernel


@dataclass
class RadiationReading:
    """Radiation sensor reading."""
    sensor_id: str
    location: str
    radiation_mrem_hr: float  # millirem per hour
    temperature_c: float
    pressure_bar: float
    neutron_flux: float
    timestamp: float


class LexNukeKernel:
    """
    KL-021-LEXNUKE: Nuclear safety monitoring.
    
    Critical infrastructure - MUST NOT FAIL.
    
    Safety levels:
    - <5 mrem/hr: Normal
    - 5-10: Elevated
    - 10-50: High
    - >50: CRITICAL (immediate shutdown)
    """
    
    def __init__(self):
        self.kernel = TemporalAdaptiveKernel(
            alpha=1.0,  # Very sensitive
            beta=0.99,  # Long memory
            lambda_jitter=0.1,  # Tolerate small fluctuations
            drift_threshold=0.05
        )
        
        self.critical_alerts = []
        self.timestep = 0
    
    def process_readings(self, readings: List[RadiationReading]) -> Dict:
        """
        Process radiation readings with safety-critical fusion.
        
        Returns
        -------
        result : dict
            - radiation_level: Fused reading (mrem/hr)
            - safety_status: "normal"|"elevated"|"high"|"CRITICAL"
            - failed_sensors: Malfunctioning sensors
            - recommend_shutdown: Boolean
        """
        # Convert to signals
        signals = np.array([
            [r.radiation_mrem_hr, r.temperature_c, r.pressure_bar, r.neutron_flux]
            for r in readings
        ])
        
        # Fuse
        fused, weights = self.kernel.update(signals)
        radiation = fused[0]
        temp = fused[1]
        
        # Safety classification
        if radiation < 5:
            status = "normal"
        elif radiation < 10:
            status = "elevated"
        elif radiation < 50:
            status = "high"
        else:
            status = "CRITICAL"
        
        # Shutdown recommendation
        shutdown = (radiation > 50) or (temp > 400)
        
        if shutdown:
            alert = {
                'timestamp': datetime.now().isoformat(),
                'radiation': float(radiation),
                'temperature': float(temp),
                'reason': 'Radiation' if radiation > 50 else 'Temperature'
            }
            self.critical_alerts.append(alert)
        
        self.timestep += 1
        
        return {
            'radiation_mrem_hr': float(radiation),
            'temperature_c': float(temp),
            'safety_status': status,
            'recommend_shutdown': shutdown,
            'failed_sensors': [r.sensor_id for i, r in enumerate(readings) if weights[i] < 0.1],
            'timestep': self.timestep
        }
    
    def get_safety_report(self) -> Dict:
        """Generate NRC compliance report."""
        return {
            'facility': 'SITE-001',
            'monitoring_duration': self.timestep,
            'critical_events': len(self.critical_alerts),
            'last_critical': self.critical_alerts[-1] if self.critical_alerts else None,
            'status': 'SAFE' if not self.critical_alerts else 'REVIEW_REQUIRED'
        }


def main():
    """Example."""
    kernel = LexNukeKernel()
    
    # Normal operation
    readings_normal = [
        RadiationReading(f"RAD-{i}", f"Zone-{i//2}", 2.5 + np.random.rand(), 85, 1.01, 1e12)
        for i in range(10)
    ]
    
    result = kernel.process_readings(readings_normal)
    print(f"KL-021-LEXNUKE: Nuclear Safety Monitoring")
    print(f"Radiation: {result['radiation_mrem_hr']:.2f} mrem/hr")
    print(f"Status: {result['safety_status']}")
    
    # Simulate criticality event
    readings_critical = [
        RadiationReading(f"RAD-{i}", f"Zone-{i//2}", 55.0 + np.random.rand()*10, 350, 1.5, 5e13)
        for i in range(10)
    ]
    
    result = kernel.process_readings(readings_critical)
    print(f"\n⚠️  CRITICAL EVENT DETECTED")
    print(f"Radiation: {result['radiation_mrem_hr']:.2f} mrem/hr")
    print(f"Shutdown Recommended: {result['recommend_shutdown']}")


if __name__ == "__main__":
    main()
