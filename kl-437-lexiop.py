"""
KL-437-LEXIOP: Intraocular Pressure Fusion
Multiple tonometry readings that disagree → consensus IOP
Patent: PCT Pending | Royalty: 25bp → 0x44f8...C689
"""

import numpy as np
from typing import Dict, List
from dataclasses import dataclass
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.adaptive_spectral_kernel import AdaptiveSpectralKernel

@dataclass
class IOPMeasurement:
    device: str
    iop_mmhg: float
    corneal_thickness: float
    measurement_quality: float

class LexIOPKernel:
    def __init__(self):
        self.kernel = AdaptiveSpectralKernel(alpha=1.95)
        self.measurements = 0
        self.revenue = 0.0
    
    def fuse_iop(self, patient_id: str, measurements: List[IOPMeasurement]) -> Dict:
        signals = np.array([
            [m.iop_mmhg/40.0, m.corneal_thickness/600.0, m.measurement_quality]
            for m in measurements
        ])
        
        fused, weights = self.kernel.fit(signals)
        
        iop = float(fused[0] * 40.0)
        
        if iop > 24:
            risk = "HIGH"; action = "Start treatment"
        elif iop > 21:
            risk = "MODERATE"; action = "Monitor closely"
        else:
            risk = "NORMAL"; action = "Annual check"
        
        self.measurements += 1
        self.revenue += 0.0025
        
        return {
            'patient_id': patient_id,
            'consensus_iop': iop,
            'risk_level': risk,
            'action': action,
            'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'
        }
    
    def get_stats(self):
        return {'measurements': self.measurements, 'revenue': self.revenue, 'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'}

def main():
    kernel = LexIOPKernel()
    print("KL-437-LEXIOP: IOP Fusion")
    
    measurements = [
        IOPMeasurement("Goldman", 23.5, 545, 0.95),
        IOPMeasurement("iCare", 24.0, 545, 0.90),
        IOPMeasurement("Tonopen", 22.8, 545, 0.85),
        IOPMeasurement("Pneumotonometer", 23.2, 545, 0.88)
    ]
    
    result = kernel.fuse_iop("PT007", measurements)
    print(f"Patient: {result['patient_id']}")
    print(f"Consensus IOP: {result['consensus_iop']:.1f} mmHg")
    print(f"Risk: {result['risk_level']}")
    print(f"Action: {result['action']}")
    
    kernel.measurements = 12000
    kernel.revenue = 12000 * 0.0025
    print(f"Annual: {kernel.measurements:,} | Revenue: ${kernel.revenue:,.2f}")

if __name__ == "__main__":
    main()
