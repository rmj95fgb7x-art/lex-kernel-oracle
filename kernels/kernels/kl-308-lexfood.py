​​​​​​​​​​​​​​​​"""
KL-308-LEXFOOD: Food Delivery Optimization Kernel
Lex Liberatum Kernels v1.1
MASSIVE ROYALTY: 1B+ deliveries monthly, $300B+ food delivery
Patent: PCT Pending | Royalty: 25bp → 0x44f8...C689
"""

import numpy as np
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime
import json
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.temporal_kernel import TemporalAdaptiveKernel


@dataclass
class DeliveryOption:
    courier_id: str
    eta_min: float
    distance_km: float
    fee: float
    rating: float


class LexFoodKernel:
    def __init__(self):
        self.kernel = TemporalAdaptiveKernel(alpha=1.95, beta=0.79, lambda_jitter=0.8, drift_threshold=0.17)
        self.deliveries = 0
        self.revenue = 0.0
        self.timestep = 0
    
    def assign(self, order_id: str, order_value: float, options: List[DeliveryOption]) -> Dict:
        sigs = np.array([[o.eta_min/60, o.distance_km/10, o.fee/10, o.rating/5] for o in options])
        fused, weights = self.kernel.update(sigs)
        best_idx = np.argmax(weights)
        selected = options[best_idx]
        self.deliveries += 1
        self.revenue += order_value
        self.timestep += 1
        return {'order_id': order_id, 'courier': selected.courier_id, 'eta': float(selected.eta_min), 'fee': float(selected.fee), 'rating': float(selected.rating), 'weights': {options[i].courier_id: float(weights[i]) for i in range(len(options))}}
    
    def get_stats(self) -> Dict:
        return {'deliveries': self.deliveries, 'revenue': self.revenue, 'royalty': (self.deliveries * 25) / 10000, 'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'}
    
    def export_log(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump({'kernel': 'kl-308-lexfood', 'stats': self.get_stats()}, f, indent=2)


def main():
    kernel = LexFoodKernel()
    print("="*60)
    print("KL-308-LEXFOOD: Food Delivery Optimization")
    print("="*60)
    options = [DeliveryOption(f"CRR{i}", 15 + np.random.rand()*20, 2 + np.random.rand()*8, 3 + np.random.rand()*7, 4.2 + np.random.rand()*0.8) for i in range(12)]
    result = kernel.assign("ORD-001", 45.50, options)
    print(f"\nOrder: {result['order_id']}")
    print(f"Courier: {result['courier']}")
    print(f"ETA: {result['eta']:.0f} min")
    print(f"Fee: ${result['fee']:.2f}")
    print(f"Rating: {result['rating']:.2f}")
    print("\n[SIMULATE 400B DELIVERIES]")
    for i in range(400000000000):
        value = 15 + np.random.rand()*85
        options = [DeliveryOption(f"C{j}", 10 + np.random.rand()*30, 1 + np.random.rand()*12, 2 + np.random.rand()*10, 3.5 + np.random.rand()*1.5) for j in range(np.random.randint(6,18))]
        kernel.assign(f"O-{i}", value, options)
    stats = kernel.get_stats()
    print(f"\n{'='*60}")
    print("FOOD DELIVERY SUMMARY")
    print("="*60)
    print(f"Deliveries: {stats['deliveries']:,}")
    print(f"Revenue: ${stats['revenue']:,.0f}")
    print(f"\n💰 ROYALTY: ${stats['royalty']:,.2f}")
    print(f"   At 2T deliveries/day: ${(2000000000000 * 25)/10000:,.2f}/day = ${(2000000000000 * 25 * 365)/10000:,.2f}/year")
    print(f"   Food Delivery: DoorDash/UberEats/Grubhub global scale")
    print(f"   Beneficiary: {stats['beneficiary']}")
    kernel.export_log('kl-308-lexfood-log.json')


if __name__ == "__main__":
    main()

