"""
KL-431-LEXGLAUCOMA: Glaucoma Detection Fusion
IOP + visual field + optic nerve imaging
Patent: PCT Pending | Royalty: 25bp → 0x44f8...C689
"""

import numpy as np
from typing import Dict, List
from dataclasses import dataclass
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.adaptive_spectral_kernel import AdaptiveSpectralKernel

@dataclass
class GlaucomaTest:
    source: str
    test_type: str  # "IOP", "visual_field", "OCT_rnfl", "clinical_exam"
    glaucoma_probability: float
    iop_mmhg: float
    cup_to_disc_ratio: float
    visual_field_loss_pct: float

class LexGlaucomaKernel:
    def __init__(self):
        self.kernel = AdaptiveSpectralKernel(alpha=1.95)
        self.tests = 0
        self.revenue = 0.0
    
    def fuse_glaucoma_diagnosis(self, patient_id: str, tests: List[GlaucomaTest]) -> Dict:
        signals = np.array([
            [t.glaucoma_probability, t.iop_mmhg/40.0, t.cup_to_disc_ratio, 
             t.visual_field_loss_pct/100.0]
            for t in tests
        ])
        
        fused, weights = self.kernel.fit(signals)
        
        prob = float(fused[0])
        iop = float(fused[1] * 40.0)
        cdr = float(fused[2])
        vf_loss = float(fused[3] * 100.0)
        
        if prob > 0.7 or iop > 24:
            stage = "URGENT"
            action = "Start IOP-lowering drops immediately"
        elif prob > 0.5 or iop > 21:
            stage = "HIGH_RISK"
            action = "Consider prophylactic treatment"
        else:
            stage = "MONITOR"
            action = "Annual screening"
        
        self.tests += 1
        self.revenue += 0.0025
        
        return {
            'patient_id': patient_id,
            'glaucoma_probability': prob,
            'consensus_iop': iop,
            'cup_disc_ratio': cdr,
            'visual_field_loss': vf_loss,
            'stage': stage,
            'action': action,
            'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'
        }
    
    def get_stats(self):
        return {'tests': self.tests, 'revenue': self.revenue, 'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'}

def main():
    kernel = LexGlaucomaKernel()
    print("="*60)
    print("KL-431-LEXGLAUCOMA: Glaucoma Detection Fusion")
    print("="*60)
    
    tests = [
        GlaucomaTest("Goldman IOP", "IOP", 0.65, 23.5, 0.6, 8.0),
        GlaucomaTest("iCare IOP", "IOP", 0.62, 24.0, 0.6, 8.0),
        GlaucomaTest("OCT RNFL", "OCT", 0.70, 23.5, 0.65, 10.0),
        GlaucomaTest("Visual Field", "vf", 0.68, 23.5, 0.6, 9.0),
        GlaucomaTest("Ophthalmologist", "clinical", 0.72, 23.5, 0.62, 8.5)
    ]
    
    result = kernel.fuse_glaucoma_diagnosis("PT002", tests)
    
    print(f"\n👁️  Patient: {result['patient_id']}")
    print(f"📊 Glaucoma Probability: {result['glaucoma_probability']:.1%}")
    print(f"📊 Consensus IOP: {result['consensus_iop']:.1f} mmHg")
    print(f"📊 Cup/Disc Ratio: {result['cup_disc_ratio']:.2f}")
    print(f"📊 Visual Field Loss: {result['visual_field_loss']:.1f}%")
    print(f"⚠️  Stage: {result['stage']}")
    print(f"💊 Action: {result['action']}")
    
    print("\n[SIMULATE MORAN EYE CENTER]")
    kernel.tests = 8000
    kernel.revenue = 8000 * 0.0025
    stats = kernel.get_stats()
    print(f"Annual tests: {stats['tests']:,}")
    print(f"Revenue: ${stats['revenue']:,.2f}")

if __name__ == "__main__":
    main()
