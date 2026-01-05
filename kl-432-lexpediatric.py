"""
KL-432-LEXPEDIATRIC: Pediatric Eye Disease Detection
Amblyopia, strabismus, refractive errors in children
Patent: PCT Pending | Royalty: 25bp → 0x44f8...C689
"""

import numpy as np
from typing import Dict, List
from dataclasses import dataclass
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.adaptive_spectral_kernel import AdaptiveSpectralKernel

@dataclass
class PediatricExam:
    source: str
    exam_type: str  # "vision_test", "cover_test", "refraction", "parent_report"
    amblyopia_risk: float
    strabismus_detected: bool
    visual_acuity_od: float  # Right eye (20/20 = 1.0, 20/40 = 0.5)
    visual_acuity_os: float  # Left eye
    child_cooperation: float  # 0-1 (how well child cooperated)

class LexPediatricKernel:
    def __init__(self):
        self.kernel = AdaptiveSpectralKernel(alpha=1.95)
        self.exams = 0
        self.revenue = 0.0
    
    def fuse_pediatric_diagnosis(self, patient_id: str, age: int, exams: List[PediatricExam]) -> Dict:
        signals = np.array([
            [e.amblyopia_risk, 1.0 if e.strabismus_detected else 0.0,
             e.visual_acuity_od, e.visual_acuity_os, e.child_cooperation]
            for e in exams
        ])
        
        fused, weights = self.kernel.fit(signals)
        
        amblyopia = float(fused[0])
        strabismus = fused[1] > 0.5
        va_od = float(fused[2])
        va_os = float(fused[3])
        
        # Critical period for treatment (age < 8)
        critical_period = age < 8
        
        if amblyopia > 0.6 or strabismus:
            urgency = "URGENT" if critical_period else "HIGH"
            action = "Start patching therapy NOW" if amblyopia > 0.6 else "Refer to pediatric ophthalmologist"
        elif amblyopia > 0.4:
            urgency = "MODERATE"
            action = "Glasses + close monitoring"
        else:
            urgency = "ROUTINE"
            action = "Annual screening"
        
        self.exams += 1
        self.revenue += 0.0025
        
        return {
            'patient_id': patient_id,
            'age': age,
            'amblyopia_risk': amblyopia,
            'strabismus_present': strabismus,
            'visual_acuity_right': va_od,
            'visual_acuity_left': va_os,
            'urgency': urgency,
            'action': action,
            'critical_period': critical_period,
            'window_closing': f"{8-age} years left for optimal treatment" if critical_period else "Past critical period",
            'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'
        }
    
    def get_stats(self):
        return {'exams': self.exams, 'revenue': self.revenue, 'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'}

def main():
    kernel = LexPediatricKernel()
    print("="*60)
    print("KL-432-LEXPEDIATRIC: Pediatric Eye Disease Detection")
    print("="*60)
    
    exams = [
        PediatricExam("Vision Screener", "vision_test", 0.65, True, 0.5, 0.8, 0.7),
        PediatricExam("Ophthalmologist", "clinical", 0.70, True, 0.55, 0.85, 0.9),
        PediatricExam("Autorefractor", "refraction", 0.60, False, 0.50, 0.80, 1.0),
        PediatricExam("Parent Report", "history", 0.75, True, 0.5, 0.8, 0.8)
    ]
    
    result = kernel.fuse_pediatric_diagnosis("CHILD_001", age=5, exams=exams)
    
    print(f"\n👶 Patient: {result['patient_id']} (Age {result['age']})")
    print(f"📊 Amblyopia Risk: {result['amblyopia_risk']:.1%}")
    print(f"📊 Strabismus: {'YES ⚠️' if result['strabismus_present'] else 'NO'}")
    print(f"📊 Visual Acuity Right: {result['visual_acuity_right']:.2f} (20/{int(20/result['visual_acuity_right'])})")
    print(f"📊 Visual Acuity Left: {result['visual_acuity_left']:.2f} (20/{int(20/result['visual_acuity_left'])})")
    print(f"⏰ Critical Period: {'YES - {}'.format(result['window_closing']) if result['critical_period'] else 'NO'}")
    print(f"⚠️  Urgency: {result['urgency']}")
    print(f"💊 Action: {result['action']}")
    
    print("\n[SIMULATE MORAN PEDIATRIC CLINIC]")
    kernel.exams = 3000
    kernel.revenue = 3000 * 0.0025
    stats = kernel.get_stats()
    print(f"Annual pediatric exams: {stats['exams']:,}")
    print(f"Revenue: ${stats['revenue']:,.2f}")

if __name__ == "__main__":
    main()
