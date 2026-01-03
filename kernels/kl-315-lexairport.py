"""
KL-315-LEXAIRPORT: Airport Slot Allocation Kernel
Lex Liberatum Kernels v1.1
MASSIVE ROYALTY: 40,000+ airports, billions of flights
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
class SlotRequest:
    airline: str
    flight_number: str
    requested_time: float
    aircraft_size: str
    priority_score: float
    delay_cost: float


class LexAirportKernel:
    def __init__(self):
        self.kernel = AdaptiveSpectralKernel(alpha=1.85)
        self.allocations = 0
        self.revenue = 0.0
    
    def allocate_slot(self, slot_id: str, requests: List[SlotRequest]) -> Dict:
        sigs = np.array([[r.requested_time/3600, r.priority_score, r.delay_cost/10000, len(r.aircraft_size)] for r in requests])
        fused, weights = self.kernel.fit(sigs)
        best_idx = np.argmax(weights)
        selected = requests[best_idx]
        self.allocations += 1
        self.revenue += selected.delay_cost * 0.1
        return {'slot_id': slot_id, 'airline': selected.airline, 'flight': selected.flight_number, 'time': float(fused[0] * 3600), 'weights': {requests[i].airline: float(weights[i]) for i in range(len(requests))}}
    
    def get_stats(self) -> Dict:
        return {'allocations': self.allocations, 'revenue': self.revenue, 'royalty': (self.allocations * 25) / 10000, 'beneficiary': '0x44f8219cBABad92​​​​​​​​​​​​​​​​
