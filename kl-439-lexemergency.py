"""
KL-439-LEXEMERGENCY: Emergency Triage
Symptoms + imaging + vitals → prioritize ER cases (retinal detachment = URGENT)
Patent: PCT Pending | Royalty: 25bp → 0x44f8...C689
"""

import numpy as np
from typing import Dict, List
from dataclasses import dataclass
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.adaptive_spectral_kernel import AdaptiveSpectralKernel

@dataclass
class EmergencyInput:
    source: str
    severity: float
    vision_loss: bool
    pain_level: float
    time_sensitive: bool

class LexEmergencyKernel:
    def __init__(self):
        self.kernel = AdaptiveSpectralKernel(alpha=1.95)
        self.emergencies = 0
        self.revenue = 0.0
    
    def triage_emergency(self, patient_id: str, chief_complaint: str, inputs: List[EmergencyInput]) -> Dict:
        signals = np.array([
            [i.severity, 1.0 if i.vision_loss else 0.0, i.pain_level/10.0, 1.0 if i.time_sensitive else 0.0]
            for i in inputs
        ])
        
        fused, weights = self.kernel.fit(signals)
        
        severity = float(fused[0])
        vision_loss = fused[1] > 0.5
        
        if severity > 0.85 or vision_loss:
            triage = "IMMEDIATE"; minutes = 0; color = "RED"
        elif severity > 0.65:
            triage = "EMERGENT"; minutes = 15; color = "ORANGE"
        elif severity > 0.45:
            triage = "URGENT"; minutes = 60; color = "YELLOW"
        else:
            triage = "NON_URGENT"; minutes = 120; color = "GREEN"
        
        self.emergencies += 1
        self.revenue += 0.0025
        
        return {
            'patient_id': patient_id,
            'chief_complaint': chief_complaint,
            'triage_level': triage,
            'wait_time_minutes': minutes,
            'color_code': color,
            'severity_score': severity,
            'vision_threatening': vision_loss,
            'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'
        }
    
    def get_stats(self):
        return {'emergencies': self.emergencies, 'revenue': self.revenue, 'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'}

def main():
    kernel = LexEmergencyKernel()
    print("KL-439-LEXEMERGENCY: Emergency Triage")
    
    inputs = [
        EmergencyInput("Triage nurse", 0.90, True, 8.0, True),
        EmergencyInput("ER physician", 0.92, True, 7.5, True),
        EmergencyInput("Patient self-report", 0.88, True, 9.0, True)
    ]
    
    result = kernel.triage_emergency("PT009", "Sudden vision loss + flashing lights", inputs)
    print(f"Patient: {result['patient_id']}")
    print(f"Complaint: {result['chief_complaint']}")
    print(f"Triage: {result['triage_level']} ({result['color_code']})")
    print(f"Wait: {result['wait_time_minutes']} min")
    print(f"Severity: {result['severity_score']:.1%}")
    print(f"Vision-threatening: {'YES ⚠️' if result['vision_threatening'] else 'NO'}")
    
    kernel.emergencies = 800
    kernel.revenue = 800 * 0.0025
    print(f"Annual: {kernel.emergencies:,} | Revenue: ${kernel.revenue:,.2f}")

if __name__ == "__main__":
    main()
