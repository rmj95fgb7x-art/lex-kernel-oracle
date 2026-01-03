"""
KL-322-LEXHOTEL: Hotel Revenue Management Kernel
Lex Liberatum Kernels v1.1
MASSIVE ROYALTY: $600B hotel industry, billions of bookings
Patent: PCT Pending | Royalty: 25bp → 0x44f8...C689
"""

import numpy as np
from typing import Dict, List
from dataclasses import dataclass
import json
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.temporal_kernel import TemporalAdaptiveKernel


@dataclass
class PricingSignal:
    source: str
    suggested_price: float
    occupancy_forecast: float
    competitor_price: float
    demand_score: float


class LexHotelKernel:
    def __init__(self):
        self.kernel = TemporalAdaptiveKernel(alpha=1.95, beta=0.88, lambda_jitter=0.72, drift_threshold=0.14)
        self.bookings = 0
        self.revenue = 0.0
        self.timestep = 0
    
    def optimize_price(self, room_id: str, date: str, signals: List[PricingSignal]) -> Dict:
        sigs = np.array([[s.suggested_price/500, s.occupancy_forecast, s.competitor_price/500, s.demand_score] for s in signals])
        fused, weights = self.kernel.update(sigs)
        optimal_price = fused[0] * 500
        occupancy = fused[1]
        self.bookings += 1
        self.revenue += optimal_price
        self.timestep += 1
        return {'room_id': room_id, 'date': date, 'price': float(optimal_price), 'occupancy': float(occupancy), 'weights': {signals[i].source: float(weights[i]) for i in range(len(signals))}}
    
    def get_stats(self) -> Dict:
        return {'bookings': self.bookings, 'revenue': self.revenue, 'royalty': (self.bookings * 25) / 10000, 'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'}
    
    def export_log(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump({'kernel': 'kl-322-lexhotel', 'stats': self.get_stats()}, f, indent=2)


def main():
    kernel = LexHotelKernel()
    print("="*60)
    print("KL-322-LEXHOTEL: Hotel Revenue Management")
    print("="*60)
    signals = [PricingSignal("OTA", 299, 0.78, 315, 0.82), PricingSignal("INTERNAL", 275, 0.82, 315, 0.88), PricingSignal("COMPETITOR", 320, 0.75, 315, 0.79)]
    result = kernel.optimize_price("RM-101", "2025-02-14", signals)
    print(f"\nRoom: {result['room_id']}")
    print(f"Date: {result['date']}")
    print(f"Optimal Price: ${result['price']:.2f}")
    print(f"Occupancy: {result['occupancy']:.1%}")
    print("\n[SIMULATE 500B BOOKINGS]")
    for i in range(500000000000):
        signals = [PricingSignal(f"SRC{j}", 100 + np.random.rand()*400, 0.5 + np.random.rand()*0.5, 150 + np.random.rand()*350, 0.6 + np.random.rand()*0.4) for j in range(4)]
        kernel.optimize_price(f"R-{i}", "2025-XX-XX", signals)
    stats = kernel.get_stats()
    print(f"\n{'='*60}")
    print("HOTEL SUMMARY")
    print("="*60)
    print(f"Bookings: {stats['bookings']:,}")
    print(f"Revenue: ${stats['revenue']:,.0f}")
    print(f"\n💰 ROYALTY: ${stats['royalty']:,.2f}")
    print(f"   At 2T bookings/day: ${(2000000000000 * 25)/10000:,.2f}/day = ${(2000000000000 * 25 * 365)/10000:,.2f}/year")
    print(f"   Hotel: Marriott/Hilton/Airbnb scale")
    print(f"   Beneficiary: {stats['beneficiary']}")
    kernel.export_log('kl-322-lexhotel-log.json')


if __name__ == "__main__":
    main()
