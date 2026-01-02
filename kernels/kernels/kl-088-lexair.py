"""
KL-088-LEXAIR: Aviation Safety Kernel
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
class AircraftSensor:
    sensor_id: str
    aircraft_id: str
    altitude_ft: float
    airspeed_knots: float
    vertical_speed_fpm: float
    engine_temp_c: float
    fuel_flow_gph: float
    hydraulic_pressure_psi: float
    timestamp: float


class LexAirKernel:
    def __init__(self):
        self.kernel = TemporalAdaptiveKernel(alpha=0.9, beta=0.96, lambda_jitter=0.2, drift_threshold=0.05)
        self.alerts = []
        self.timestep = 0
        self.readings = 0
    
    def monitor_aircraft(self, sensors: List[AircraftSensor]) -> Dict:
        signals = np.array([[s.altitude_ft, s.airspeed_knots, s.vertical_speed_fpm, s.engine_temp_c, s.fuel_flow_gph, s.hydraulic_pressure_psi] for s in sensors])
        fused, weights = self.kernel.update(signals)
        alt = fused[0]
        speed = fused[1]
        vspeed = fused[2]
        temp = fused[3]
        fuel = fused[4]
        hydraulic = fused[5]
        stall = speed < 120
        overspeed = speed > 250
        engine_hot = temp > 850
        low_fuel = fuel < 50
        hydraulic_fail = hydraulic < 1500
        critical = stall or engine_hot or hydraulic_fail
        if critical:
            self.alerts.append({'timestamp': datetime.now().isoformat(), 'altitude': float(alt), 'speed': float(speed), 'temp': float(temp), 'hydraulic': float(hydraulic), 'reason': 'STALL' if stall else ('ENGINE_TEMP' if engine_hot else 'HYDRAULIC')})
        failed = [s.sensor_id for i, s in enumerate(sensors) if weights[i] < 0.05]
        self.timestep += 1
        self.readings += len(sensors)
        return {'altitude_ft': float(alt), 'airspeed_knots': float(speed), 'vertical_speed_fpm': float(vspeed), 'engine_temp_c': float(temp), 'fuel_flow_gph': float(fuel), 'hydraulic_psi': float(hydraulic), 'stall_warning': stall, 'overspeed': overspeed, 'engine_hot': engine_hot, 'low_fuel': low_fuel, 'hydraulic_failure': hydraulic_fail, 'critical_alert': critical, 'failed_sensors': failed, 'timestep': self.timestep}
    
    def get_report(self) -> Dict:
        return {'timesteps': self.timestep, 'readings': self.readings, 'critical_alerts': len(self.alerts), 'alert_rate': len(self.alerts)/max(1, self.timestep), 'royalty': (self.readings * 25) / 10000, 'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'}
    
    def export_log(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump({'kernel': 'kl-088-lexair', 'report': self.get_report(), 'alerts': self.alerts}, f, indent=2)


def main():
    kernel = LexAirKernel()
    print("="*60)
    print("KL-088-LEXAIR: Aviation Safety Monitoring")
    print("="*60)
    print("\n[CRUISE FLIGHT]")
    sensors_cruise = [AircraftSensor(f"AVION-{i}", "N12345", 35000 + np.random.rand()*500, 450 + np.random.rand()*20, -50 + np.random.rand()*100, 650 + np.random.rand()*50, 350 + np.random.rand()*30, 3000 + np.random.rand()*100, datetime.now().timestamp()) for i in range(12)]
    result = kernel.monitor_aircraft(sensors_cruise)
    print(f"Altitude: {result['altitude_ft']:.0f} ft")
    print(f"Airspeed: {result['airspeed_knots']:.0f} knots")
    print(f"Engine Temp: {result['engine_temp_c']:.0f}°C")
    print(f"Critical Alert: {result['critical_alert']}")
    print("\n[ENGINE OVERHEAT]")
    sensors_hot = [AircraftSensor(f"AVION-{i}", "N12345", 35000 + np.random.rand()*500, 450 + np.random.rand()*20, -50 + np.random.rand()*100, 880 + np.random.rand()*30, 350 + np.random.rand()*30, 3000 + np.random.rand()*100, datetime.now().timestamp()) for i in range(12)]
    result = kernel.monitor_aircraft(sensors_hot)
    print(f"Engine Temp: {result['engine_temp_c']:.0f}°C")
    print(f"🚨 Engine Hot: {result['engine_hot']}")
    print(f"🚨 Critical Alert: {result['critical_alert']}")
    print("\n[HYDRAULIC FAILURE]")
    sensors_hydraulic = [AircraftSensor(f"AVION-{i}", "N12345", 35000 + np.random.rand()*500, 450 + np.random.rand()*20, -50 + np.random.rand()*100, 650 + np.random.rand()*50, 350 + np.random.rand()*30, 800 + np.random.rand()*200, datetime.now().timestamp()) for i in range(12)]
    result = kernel.monitor_aircraft(sensors_hydraulic)
    print(f"Hydraulic Pressure: {result['hydraulic_psi']:.0f} psi")
    print(f"🚨 Hydraulic Failure: {result['hydraulic_failure']}")
    print(f"🚨 Critical Alert: {result['critical_alert']}")
    report = kernel.get_report()
    print(f"\n{'='*60}")
    print("AVIATION SAFETY REPORT")
    print("="*60)
    print(f"Timesteps: {report['timesteps']}")
    print(f"Readings: {report['readings']}")
    print(f"Critical Alerts: {report['critical_alerts']}")
    print(f"Alert Rate: {report['alert_rate']:.1%}")
    print(f"Royalty: ${report['royalty']:.2f}")
    kernel.export_log('kl-088-lexair-log.json')


if __name__ == "__main__":
    main()
