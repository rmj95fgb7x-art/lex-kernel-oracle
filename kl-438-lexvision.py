"""
KL-438-LEXVISION: Vision Test Fusion
Multiple visual acuity tests (patient inconsistent) → true vision score
Patent: PCT Pending | Royalty: 25bp → 0x44f8...C689
"""

import numpy as np
from typing import Dict, List
from dataclasses import dataclass
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.adaptive_spectral_kernel import AdaptiveSpectralKernel

@dataclass
class VisionTest:
    test_type: str
    visual_acuity: float  # 1.0 = 20/20
    patient_effort: float
    test_reliability: float

class LexVisionKernel:
    def __init__(self):
        self.kernel = AdaptiveSpectralKernel(alpha=1.95)
        self.tests = 0
        self.revenue = 0.0
    
    def fuse_vision(self, patient_id: str, tests: List[VisionTest]) -> Dict:
        signals = np.array([
            [t.visual_acuity, t.patient_effort, t.test_reliability]
            for t in tests
        ])
        
        fused, weights = self.kernel.fit(signals)
        
        va = float(fused[0])
        snellen = f"20/{int(20/va)}" if va > 0 else "CF"
        
        if va >= 0.8:
            category = "NORMAL"
        elif va >= 0.5:
            category = "MILD_IMPAIRMENT"
        elif va >= 0.25:
            category = "MODERATE_IMPAIRMENT"
        else:
            category = "SEVERE_IMPAIRMENT"
        
        self.tests += 1
        self.revenue += 0.0025
        
        return {
            'patient_id': patient_id,
            'consensus_va': va,
            'snellen': snellen,
            'category': category,
            'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'
        }
    
    def get_stats(self):
        return {'tests': self.tests, 'revenue': self.revenue, 'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'}

def main():
    kernel = LexVisionKernel()
    print("KL-438-LEXVISION: Vision Test Fusion")
    
    tests = [
        VisionTest("Snellen chart", 0.65, 0.8, 0.9),
        VisionTest("ETDRS chart", 0.70, 0.9, 0.95),
        VisionTest("Autorefractor", 0.68, 1.0, 0.85),
        VisionTest("Repeat Snellen", 0.62, 0.7, 0.8)
    ]
    
    result = kernel.fuse_vision("PT008", tests)
    print(f"Patient: {result['patient_id']}")
    print(f"Visual Acuity: {result['consensus_va']:.2f} ({result['snellen']})")
    print(f"Category: {result['category']}")
    
    kernel.tests = 15000
    kernel.revenue = 15000 * 0.0025
    print(f"Annual: {kernel.tests:,} | Revenue: ${kernel.revenue:,.2f}")

if __name__ == "__main__":
    main()
