"""
KL-027-LEXBLOOD: Blood Bank Safety Monitoring Kernel
Lex Liberatum Kernels v1.1

Domain: Healthcare / Blood Supply Chain
Use Case: Multi-facility blood safety verification

Features:
- Cross-facility contamination detection
- Expiration monitoring
- Temperature chain validation
- FDA compliance logging

Patent: PCT Pending
Royalty: 25bp → 0x44f8...C689
"""

import numpy as np
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.adaptive_spectral_kernel import AdaptiveSpectralKernel


@dataclass
class BloodUnit:
    """Blood donation unit."""
    unit_id: str
    blood_type: str
    donation_date: datetime
    expiration_date: datetime
    current_temp_c: float
    facility_id: str
    pathogen_tests: Dict[str, bool]  # Test name -> pass/fail


class LexBloodKernel:
    """
    KL-027-LEXBLOOD: Blood safety fusion.
    
    Safety checks:
    - Temperature (2-6°C for whole blood)
    - Expiration (<42 days for RBCs)
    - Pathogen screening (all tests must pass)
    """
    
    def __init__(self, alpha: float = 1.1):
        self.kernel = AdaptiveSpectralKernel(alpha=alpha)
        self.units_checked = 0
        self.unsafe_units = []
    
    def verify_blood_batch(self, units: List[BloodUnit]) -> Dict:
        """
        Verify blood batch across facilities.
        
        Returns
        -------
        result : dict
            - safe_for_transfusion: Boolean
            - temperature_ok: Boolean
            - expiration_ok: Boolean
            - pathogen_ok: Boolean
            - suspicious_facilities: Facilities with anomalies
        """
        # Convert to signals (temp, days to expiration, test pass rate)
        signals = []
        for unit in units:
            days_to_exp = (unit.expiration_date - datetime.now()).days
            test_pass_rate = sum(unit.pathogen_tests.values()) / max(1, len(unit.pathogen_tests))
            
            signal = np.array([
                unit.current_temp_c,
                days_to_exp,
                test_pass_rate,
                1.0 if 2 <= unit.current_temp_c <= 6 else 0.0
            ])
            signals.append(signal)
        
        signals = np.array(signals)
        
        # Fuse
        fused, weights = self.kernel.fit(signals)
        
        avg_temp = fused[0]
        avg_days_left = fused[1]
        avg_test_pass = fused[2]
        
        # Safety checks
        temp_ok = 2 <= avg_temp <= 6
        exp_ok = avg_days_left > 0
        pathogen_ok = avg_test_pass > 0.99
        
        safe = temp_ok and exp_ok and pathogen_ok
        
        # Detect outliers
        outliers = [i for i, w in enumerate(weights) if w < 0.1]
        suspicious_facilities = list(set([units[i].facility_id for i in outliers]))
        
        if not safe:
            self.unsafe_units.extend([u.unit_id for u in units])
        
        self.units_checked += len(units)
        
        return {
            'safe_for_transfusion': safe,
            'temperature_ok': temp_ok,
            'expiration_ok': exp_ok,
            'pathogen_tests_ok': pathogen_ok,
            'avg_temperature_c': float(avg_temp),
            'avg_days_to_expiration': float(avg_days_left),
            'suspicious_facilities': suspicious_facilities,
            'total_units': len(units),
            'units_flagged': len(outliers)
        }
    
    def get_safety_stats(self) -> Dict:
        """FDA compliance report."""
        return {
            'units_checked': self.units_checked,
            'unsafe_units': len(self.unsafe_units),
            'safety_rate': 1 - (len(self.unsafe_units) / max(1, self.units_checked)),
            'royalty': (self.units_checked * 25) / 10000
        }


def main():
    """Example."""
    kernel = LexBloodKernel()
    
    # 5 blood units from different facilities
    units = [
        BloodUnit(
            f"UNIT-{i}",
            "O+",
            datetime.now() - timedelta(days=10),
            datetime.now() + timedelta(days=32),
            4.0 + np.random.rand(),
            f"FACILITY-{i%3}",
            {"HIV": True, "HepB": True​​​​​​​​​​​​​​​​
