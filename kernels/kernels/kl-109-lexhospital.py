"""
KL-109-LEXHOSPITAL: ICU Patient Monitoring Kernel
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
class VitalSigns:
    sensor_id: str
    patient_id: str
    heart_rate_bpm: float
    bp_systolic: float
    bp_diastolic: float
    oxygen_sat_pct: float
    respiratory_rate: float
    temperature_c: float
    timestamp: float


class LexHospitalKernel:
    def __init__(self):
        self.kernel = TemporalAdaptiveKernel(alpha=0.9, beta=0.93, lambda_jitter=0.3, drift_threshold=0.06)
        self.code_blue_alerts = []
        self.timestep = 0
        self.readings = 0
    
    def monitor_patient(self, vitals: List[VitalSigns]) -> Dict:
        signals = np.array([[v.heart_rate_bpm, v.bp_systolic, v.bp_diastolic, v.oxygen_sat_pct, v.respiratory_rate, v.temperature_c] for v in vitals])
        fused, weights = self.kernel.update(signals)
        hr = fused[0]
        sys_bp = fused[1]
        dia_bp = fused[2]
        o2 = fused[3]
        rr = fused[4]
        temp = fused[5]
        bradycardia = hr < 50
        tachycardia = hr > 120
        hypotension = sys_bp < 90
        hypertension = sys_bp > 180
        hypoxia = o2 < 90
        tachypnea = rr > 25
        fever = temp > 38.5
        code_blue = bradycardia or hypotension or hypoxia or (hr < 40)
        if code_blue:
            self.code_blue_alerts.append({'timestamp': datetime.now().isoformat(), 'hr': float(hr), 'bp_sys': float(sys_bp), 'o2': float(o2), 'reason': 'BRADYCARDIA' if bradycardia else ('HYPOTENSION' if hypotension else 'HYPOXIA')})
        failed = [v.sensor_id for i, v in enumerate(vitals) if weights[i] < 0.06]
        self.timestep += 1
        self.readings += len(vitals)
        return {'heart_rate': float(hr), 'bp_systolic': float(sys_bp), 'bp_diastolic': float(dia_bp), 'oxygen_sat': float(o2), 'respiratory_rate': float(rr), 'temperature': float(temp), 'bradycardia': bradycardia, 'tachycardia': tachycardia, 'hypotension': hypotension, 'hypoxia': hypoxia, 'fever': fever, 'code_blue': code_blue, 'failed_sensors': failed, 'timestep': self.timestep}
    
    def get_report(self) -> Dict:
        return {'timesteps': self.timestep, 'readings': self.readings, 'code_blue_events': len(self.code_blue_alerts), 'event_rate': len(self.code_blue_alerts)/max(1, self.timestep), 'royalty': (self.readings * 25) / 10000, 'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'}
    
    def export_log(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump({'kernel': 'kl-109-lexhospital', 'report': self.get_report(), 'alerts': self.code_blue_alerts}, f, indent=2)


def main():
    kernel = LexHospitalKernel()
    print("="*60)
    print("KL-109-LEXHOSPITAL: ICU Patient Monitoring")
    print("="*60)
    print("\n[STABLE PATIENT]")
    vitals_stable = [VitalSigns(f"MON-{i}", "PT-12345", 75 + np.random.rand()*10, 120 + np.random.rand()*10, 80 + np.random.rand()*5, 97 + np.random.rand()*2, 16 + np.random.rand()*2, 37.0 + np.random.rand()*0.5, datetime.now().timestamp()) for i in range(8)]
    result = kernel.monitor_patient(vitals_stable)
    print(f"Heart Rate: {result['heart_rate']:.0f} bpm")
    print(f"BP: {result['bp_systolic']:.0f}/{result['bp_diastolic']:.0f}")
    print(f"O2 Sat: {result['oxygen_sat']:.1f}%")
    print(f"Temp: {result['temperature']:.1f}°C")
    print(f"Code Blue: {result['code_blue']}")
    print("\n[HYPOTENSIVE CRISIS]")
    vitals_hypo = [VitalSigns(f"MON-{i}", "PT-12345", 110 + np.random.rand()*10, 70 + np.random.rand()*10, 50 + np.random.rand()*5, 92 + np.random.rand()*3, 22 + np.random.rand()*3, 37.0 + np.random.rand()*0.5, datetime.now().timestamp()) for i in range(8)]
    result = kernel.monitor_patient(vitals_hypo)
    print(f"Heart Rate: {result['heart_rate']:.0f} bpm")
    print(f"BP: {result['bp_systolic']:.0f}/{result['bp_diastolic']:.0f}")
    print(f"🚨 Hypotension: {result['hypotension']}")
    print(f"🚨 CODE BLUE: {result['code_blue']}")
    print("\n[SEVERE HYPOXIA]")
    vitals_hypox = [VitalSigns(f"MON-{i}", "PT-12345", 115 + np.random.rand()*10, 110 + np.random.rand()*10, 70 + np.random.rand()*5, 85 + np.random.rand()*3, 28 + np.random.rand()*3, 37.5 + np.random.rand()*0.5, datetime.now().timestamp()) for i in range(8)]
    result = kernel.monitor_patient(vitals_hypox)
    print(f"O2 Sat: {result['oxygen_sat']:.1f}%")
    print(f"Respiratory Rate: {result['respiratory_rate']:.0f}")
    print(f"🚨 Hypoxia: {result['hypoxia']}")
    print(f"🚨 CODE BLUE: {result['code_blue']}")
    print("\n[BRADYCARDIA]")
    vitals_brady = [VitalSigns(f"MON-{i}", "PT-12345", 42 + np.random.rand()*5, 95 + np.random.rand()*10, 65 + np.random.rand()*5, 94 + np.random.rand()*2, 18 + np.random.rand()*2, 37.0 + np.random.rand()*0.5, datetime.now().timestamp()) for i in range(8)]
    result = kernel.monitor_patient(vitals_brady)
    print(f"Heart Rate: {result['heart_rate']:.0f} bpm")
    print(f"🚨 Bradycardia: {result['bradycardia']}")
    print(f"🚨 CODE BLUE: {result['code_blue']}")
    report = kernel.get_report()
    print(f"\n{'='*60}")
    print("ICU MONITORING REPORT")
    print("="​​​​​​​​​​​​​​​​
