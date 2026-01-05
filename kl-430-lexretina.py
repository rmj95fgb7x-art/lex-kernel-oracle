"""
KL-430-LEXRETINA: Retinal Disease Detection Fusion
Diabetic retinopathy, macular degeneration, retinal detachment
Patent: PCT Pending | Royalty: 25bp → 0x44f8...C689
"""

import numpy as np
from typing import Dict, List
from dataclasses import dataclass
import json
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.adaptive_spectral_kernel import AdaptiveSpectralKernel

@dataclass
class RetinalScan:
    source: str
    modality: str  # "OCT", "fundus_photo", "fluorescein_angio"
    disease_probability: Dict[str, float]  # {"dr": 0.8, "amd": 0.1}
    severity: int  # 0-4 (none, mild, moderate, severe, proliferative)
    detected_features: List[str]
    image_quality: float

class LexRetinaKernel:
    def __init__(self):
        self.kernel = AdaptiveSpectralKernel(alpha=1.95)
        self.scans = 0
        self.revenue = 0.0
    
    def fuse_retinal_diagnosis(self, patient_id: str, scans: List[RetinalScan]) -> Dict:
        signals = np.array([
            [s.disease_probability.get('dr', 0), s.disease_probability.get('amd', 0),
             s.severity/4.0, s.image_quality, len(s.detected_features)/10.0]
            for s in scans
        ])
        
        fused, weights = self.kernel.fit(signals)
        
        dr_prob = float(fused[0])
        amd_prob = float(fused[1])
        severity = int(fused[2] * 4)
        
        urgency = "URGENT" if severity >= 3 or dr_prob > 0.8 else "ROUTINE"
        
        self.scans += 1
        self.revenue += 0.0025
        
        return {
            'patient_id': patient_id,
            'diabetic_retinopathy_prob': dr_prob,
            'macular_degeneration_prob': amd_prob,
            'severity': severity,
            'urgency': urgency,
            'recommendation': 'Immediate treatment' if urgency == "URGENT" else 'Monitor in 6 months',
            'source_weights': {scans[i].source: float(weights[i]) for i in range(len(scans))},
            'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'
        }
    
    def get_stats(self):
        return {'scans': self.scans, 'revenue': self.revenue, 'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'}

def main():
    kernel = LexRetinaKernel()
    print("="*60)
    print("KL-430-LEXRETINA: Retinal Disease Detection")
    print("="*60)
    
    scans = [
        RetinalScan("Zeiss OCT", "OCT", {"dr": 0.82, "amd": 0.15}, 3, ["microaneurysms", "exudates"], 0.95),
        RetinalScan("Topcon Fundus", "fundus", {"dr": 0.78, "amd": 0.12}, 3, ["hemorrhages"], 0.90),
        RetinalScan("AI Model A", "OCT", {"dr": 0.85, "amd": 0.18}, 3, ["neovascularization"], 0.92),
        RetinalScan("Ophthalmologist", "clinical", {"dr": 0.80, "amd": 0.10}, 3, ["severe_npdr"], 0.88)
    ]
    
    result = kernel.fuse_retinal_diagnosis("PT001", scans)
    
    print(f"\n👁️  Patient: {result['patient_id']}")
    print(f"📊 Diabetic Retinopathy: {result['diabetic_retinopathy_prob']:.1%}")
    print(f"📊 Macular Degeneration: {result['macular_degeneration_prob']:.1%}")
    print(f"📊 Severity: {result['severity']}/4")
    print(f"⚠️  Urgency: {result['urgency']}")
    print(f"💊 Recommendation: {result['recommendation']}")
    
    print("\n[SIMULATE MORAN EYE CENTER - 10K PATIENTS/YEAR]")
    kernel.scans = 10000
    kernel.revenue = 10000 * 0.0025
    stats = kernel.get_stats()
    print(f"Annual scans: {stats['scans']:,}")
    print(f"Revenue: ${stats['revenue']:,.2f}")
    print(f"Beneficiary: {stats['beneficiary']}")

if __name__ == "__main__":
    main()
