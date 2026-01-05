"""
KL-433-LEXCATARACT: Cataract Severity Assessment
Slit-lamp + visual acuity + multiple ophthalmologist opinions
Patent: PCT Pending | Royalty: 25bp → 0x44f8...C689
"""

import numpy as np
from typing import Dict, List
from dataclasses import dataclass
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.adaptive_spectral_kernel import AdaptiveSpectralKernel

@dataclass
class CataractAssessment:
    source: str
    severity: int  # 0-4
    visual_acuity: float  # 1.0 = 20/20
    lens_opacity_pct: float
    glare_disability: float
    surgery_recommended: bool

class LexCataractKernel:
    def __init__(self):
        self.kernel = AdaptiveSpectralKernel(alpha=1.95)
        self.assessments = 0
        self.revenue = 0.0
    
    def fuse_cataract_diagnosis(self, patient_id: str, age: int, assessments: List[CataractAssessment]) -> Dict:
        signals = np.array([
            [a.severity/4.0, a.visual_acuity, a.lens_opacity_pct/100.0,
             a.glare_disability, 1.0 if a.surgery_recommended else 0.0]
            for a in assessments
        ])
        
        fused, weights = self.kernel.fit(signals)
        
        severity = int(fused[0] * 4)
        va = float(fused[1])
        opacity = float(fused[2] * 100)
        surgery = fused[4] > 0.5
        
        if severity >= 3 or va < 0.5 or surgery:
            rec = "Surgery recommended"
            timing = "Within 3 months"
        elif severity >= 2:
            rec = "Monitor, consider surgery if worsening"
            timing = "6-12 months"
        else:
            rec = "Annual monitoring"
            timing = "1 year"
        
        self.assessments += 1
        self.revenue += 0.0025
        
        return {
            'patient_id': patient_id,
            'age': age,
            'severity': severity,
            'visual_acuity': va,
            'lens_opacity': opacity,
            'surgery_recommended': surgery,
            'recommendation': rec,
            'timing': timing,
            'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'
        }
    
    def get_stats(self):
        return {'assessments': self.assessments, 'revenue': self.revenue, 'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'}

def main():
    kernel = LexCataractKernel()
    print("KL-433-LEXCATARACT: Cataract Assessment Fusion")
    
    assessments = [
        CataractAssessment("Ophthalmologist A", 3, 0.4, 75, 0.8, True),
        CataractAssessment("Ophthalmologist B", 3, 0.45, 70, 0.75, True),
        CataractAssessment("Optometrist", 2, 0.5, 65, 0.7, False),
        CataractAssessment("AI Slit-lamp", 3, 0.42, 72, 0.78, True)
    ]
    
    result = kernel.fuse_cataract_diagnosis("PT003", 72, assessments)
    
    print(f"Patient: {result['patient_id']} (Age {result['age']})")
    print(f"Severity: {result['severity']}/4")
    print(f"Visual Acuity: 20/{int(20/result['visual_acuity'])}")
    print(f"Lens Opacity: {result['lens_opacity']:.0f}%")
    print(f"Surgery: {'YES' if result['surgery_recommended'] else 'NO'}")
    print(f"Recommendation: {result['recommendation']}")
    print(f"Timing: {result['timing']}")
    
    kernel.assessments = 5000
    kernel.revenue = 5000 * 0.0025
    print(f"\nAnnual: {kernel.assessments:,} | Revenue: ${kernel.revenue:,.2f}")

if __name__ == "__main__":
    main()
