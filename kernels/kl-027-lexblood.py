"""
KL-027-LEXBLOOD: Blood Bank Safety Monitoring Kernel
Lex Liberatum Kernels v1.1

Domain: Healthcare / Blood Supply Chain
Use Case: Multi-facility blood safety verification

Patent: PCT Pending | Royalty: 25bp → 0x44f8...C689
"""

import numpy as np
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.adaptive_spectral_kernel import AdaptiveSpectralKernel


@dataclass
class BloodUnit:
    unit_id: str
    blood_type: str
    donation_date: datetime
    expiration_date: datetime
    current_temp_c: float
    facility_id: str
    pathogen_tests: Dict[str, bool]


class LexBloodKernel:
    def __init__(self, alpha: float = 1.1):
        self.kernel = AdaptiveSpectralKernel(alpha=alpha)
        self.units_checked = 0
        self.unsafe_units = []
        self.batches_processed = 0
    
    def verify_blood_batch(self, units: List[BloodUnit]) -> Dict:
        signals = []
        for unit in units:
            days_to_exp = (unit.expiration_date - datetime.now()).days
            test_pass_rate = sum(unit.pathogen_tests.values()) / max(1, len(unit.pathogen_tests))
            signal = np.array([unit.current_temp_c, days_to_exp, test_pass_rate, 1.0 if 2 <= unit.current_temp_c <= 6 else 0.0])
            signals.append(signal)
        
        signals = np.array(signals)
        fused, weights = self.kernel.fit(signals)
        
        avg_temp = fused[0]
        avg_days_left = fused[1]
        avg_test_pass = fused[2]
        
        temp_ok = 2 <= avg_temp <= 6
        exp_ok = avg_days_left > 0
        pathogen_ok = avg_test_pass > 0.99
        safe = temp_ok and exp_ok and pathogen_ok
        
        outliers = [i for i, w in enumerate(weights) if w < 0.1]
        suspicious_facilities = list(set([units[i].facility_id for i in outliers]))
        unsafe_unit_ids = [units[i].unit_id for i in outliers]
        
        if not safe:
            self.unsafe_units.extend(unsafe_unit_ids)
        
        self.units_checked += len(units)
        self.batches_processed += 1
        
        reasons = []
        if not temp_ok:
            reasons.append(f"Temperature out of range: {avg_temp:.1f}°C (safe: 2-6°C)")
        if not exp_ok:
            reasons.append(f"Expired units detected: {avg_days_left:.1f} days remaining")
        if not path​​​​​​​​​​​​​​​​
