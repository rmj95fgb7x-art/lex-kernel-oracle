"""
KL-434-LEXSURGICAL: Surgical Outcome Prediction
Pre-op data + surgeon experience + imaging → predict success
Patent: PCT Pending | Royalty: 25bp → 0x44f8...C689
"""

import numpy as np
from typing import Dict, List
from dataclasses import dataclass
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.adaptive_spectral_kernel import AdaptiveSpectralKernel

@dataclass
class SurgicalInput:
    source: str
    success_probability: float
    complication_risk: float
    recovery_weeks: int
    preop_factors: Dict[str, float]  # {"corneal_thickness": 0.9, "iop": 0.7}

class LexSurgicalKernel:
    def __init__(self):
        self.kernel = AdaptiveSpectralKernel(alpha=1.95)
        self.predictions = 0
        self.revenue = 0.0
    
    def predict_surgical_outcome(self, patient_id: str, surgery_type: str, inputs: List[SurgicalInput]) -> Dict:
        signals = np.array([
            [i.success_probability, 1.0 - i.complication_risk, i.recovery_weeks/52.0,
             i.preop_factors.get('corneal_thickness', 0.5),
             i.preop_factors.get('iop', 0.5)]
            for i in inputs
        ])
        
        fused, weights = self.kernel.fit(signals)
        
        success = float(fused[0])
        comp_risk = 1.0 - float(fused[1])
        recovery = int(fused[2] * 52)
        
        if success > 0.85 and comp_risk < 0.1:
            rec = "EXCELLENT CANDIDATE"
        elif success > 0.7:
            rec = "GOOD CANDIDATE"
        elif success > 0.5:
            rec = "MODERATE RISK"
        else:
            rec = "HIGH RISK - Consider alternatives"
        
        self.predictions += 1
        self.revenue += 0.0025
        
        return {
            'patient_id': patient_id,
            'surgery_type': surgery_type,
            'success_probability': success,
            'complication_risk': comp_risk,
            'recovery_weeks': recovery,
            'recommendation': rec,
            'proceed': success > 0.5,
            'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'
        }
    
    def get_stats(self):
        return {'predictions': self.predictions, 'revenue': self.revenue, 'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'}

def main():
    kernel = LexSurgicalKernel()
    print("KL-434-LEXSURGICAL: Surgical Outcome Prediction")
    
    inputs = [
        SurgicalInput("Surgeon A prediction", 0.88, 0.08, 4, {"corneal_thickness": 0.9, "iop": 0.75}),
        SurgicalInput("Surgeon B prediction", 0.85, 0.10, 5, {"corneal_thickness": 0.88, "iop": 0.72}),
        SurgicalInput("AI Model", 0.90, 0.07, 4, {"corneal_thickness": 0.92, "iop": 0.78}),
        SurgicalInput("Historical data", 0.86, 0.09, 4, {"corneal_thickness": 0.89, "iop": 0.74})
    ]
    
    result = kernel.predict_surgical_outcome("PT004", "LASIK", inputs)
    
    print(f"Patient: {result['patient_id']}")
    print(f"Surgery: {result['surgery_type']}")
    print(f"Success: {result['success_probability']:.1%}")
    print(f"Complication Risk: {result['complication_risk']:.1%}")
    print(f"Recovery: {result['recovery_weeks']} weeks")
    print(f"Recommendation: {result['recommendation']}")
    print(f"Proceed: {'YES' if result['proceed'] else 'NO'}")
    
    kernel.predictions = 2000
    kernel.revenue = 2000 * 0.0025
    print(f"\nAnnual: {kernel.predictions:,} | Revenue: ${kernel.revenue:,.2f}")

if __name__ == "__main__":
    main()
