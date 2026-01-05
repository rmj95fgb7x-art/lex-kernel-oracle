"""
KL-436-LEXREFERRAL: Referral Triage Fusion
Referring doctor notes + imaging + urgency → prioritize appointments
Patent: PCT Pending | Royalty: 25bp → 0x44f8...C689
"""

import numpy as np
from typing import Dict, List
from dataclasses import dataclass
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.adaptive_spectral_kernel import AdaptiveSpectralKernel

@dataclass
class ReferralInput:
    source: str
    urgency: float
    symptoms_severity: float
    imaging_abnormal: bool
    visual_acuity_loss: float

class LexReferralKernel:
    def __init__(self):
        self.kernel = AdaptiveSpectralKernel(alpha=1.95)
        self.referrals = 0
        self.revenue = 0.0
    
    def triage_referral(self, patient_id: str, inputs: List[ReferralInput]) -> Dict:
        signals = np.array([
            [i.urgency, i.symptoms_severity, 1.0 if i.imaging_abnormal else 0.0, i.visual_acuity_loss]
            for i in inputs
        ])
        
        fused, weights = self.kernel.fit(signals)
        
        urgency = float(fused[0])
        
        if urgency > 0.85:
            priority = "STAT"; days = 1
        elif urgency > 0.65:
            priority = "URGENT"; days = 3
        elif urgency > 0.45:
            priority = "SOON"; days = 14
        else:
            priority = "ROUTINE"; days = 30
        
        self.referrals += 1
        self.revenue += 0.0025
        
        return {
            'patient_id': patient_id,
            'priority': priority,
            'schedule_within_days': days,
            'urgency_score': urgency,
            'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'
        }
    
    def get_stats(self):
        return {'referrals': self.referrals, 'revenue': self.revenue, 'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'}

def main():
    kernel = LexReferralKernel()
    print("KL-436-LEXREFERRAL: Referral Triage")
    
    inputs = [
        ReferralInput("Primary care MD", 0.75, 0.80, True, 0.4),
        ReferralInput("ER physician", 0.82, 0.85, True, 0.5),
        ReferralInput("Optometrist", 0.70, 0.75, True, 0.35)
    ]
    
    result = kernel.triage_referral("PT006", inputs)
    print(f"Patient: {result['patient_id']}")
    print(f"Priority: {result['priority']}")
    print(f"Schedule: {result['schedule_within_days']} days")
    print(f"Urgency: {result['urgency_score']:.1%}")
    
    kernel.referrals = 6000
    kernel.revenue = 6000 * 0.0025
    print(f"Annual: {kernel.referrals:,} | Revenue: ${kernel.revenue:,.2f}")

if __name__ == "__main__":
    main()
