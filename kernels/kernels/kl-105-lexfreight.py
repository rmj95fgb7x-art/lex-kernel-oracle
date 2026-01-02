"""
KL-105-LEXFREIGHT: Logistics Route Optimization Kernel
Lex Liberatum Kernels v1.1
MASSIVE ROYALTY: $5T global logistics, millions of shipments daily
Patent: PCT Pending | Royalty: 25bp → 0x44f8...C689
"""

import numpy as np
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime
import json
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.adaptive_spectral_kernel import AdaptiveSpectralKernel


@dataclass
class Shipment:
    shipment_id: str
    origin: str
    destination: str
    weight_kg: float
    value_usd: float
    priority: str
    timestamp: float


@dataclass
class CarrierQuote:
    carrier_id: str
    price_usd: float
    transit_days: int
    reliability_pct: float
    insurance_included: bool
    tracking_quality: float


class LexFreightKernel:
    def __init__(self):
        self.kernel = AdaptiveSpectralKernel(alpha=1.3)
        self.shipments = 0
        self.total_value = 0.0
    
    def route_shipment(self, shipment: Shipment, quotes: List[CarrierQuote]) -> Dict:
        signals = np.array([[q.price_usd/100, q.transit_days, q.reliability_pct/100, 1.0 if q.insurance_included else 0.0, q.tracking_quality] for q in quotes])
        fused, weights = self.kernel.fit(signals)
        best_idx = np.argmax(weights)
        selected = quotes[best_idx]
        cost_per_kg = selected.price_usd / shipment.weight_kg
        self.shipments += 1
        self.total_value += shipment.value_usd
        return {'shipment_id': shipment.shipment_id, 'carrier': selected.carrier_id, 'price': float(selected.price_usd), 'transit_days': selected.transit_days, 'reliability': float(selected.reliability_pct), 'cost_per_kg': float(cost_per_kg), 'carrier_weights': {quotes[i].carrier_id: float(weights[i]) for i in range(len(quotes))}}
    
    def get_stats(self) -> Dict:
        return {'shipments': self.shipments, 'total_value': self.total_value, 'royalty': (self.shipments * 25) / 10000, 'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'}
    
    def export_log(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump({'kernel': 'kl-105-lexfreight', 'stats': self.get_stats()}, f, indent=2)


def main():
    kernel = LexFreightKernel()
    print("="*60)
    print("KL-105-LEXFREIGHT: Logistics Route Optimization")
    print("="*60)
    ship = Shipment("SHIP-001", "LA", "NYC", 500.0, 50000.0, "standard", datetime.now().timestamp())
    quotes = [CarrierQuote("FEDEX", 850.0, 3, 98.5, True, 0.95), CarrierQuote("UPS", 820.0, 4, 97.8, True, 0.93), CarrierQuote("DHL", 900.0, 2, 99.2, True, 0.98), CarrierQuote("USPS", 650.0, 7, 92.0, False, 0.75)]
    result = kernel.route_shipment(ship, quotes)
    print(f"\nShipment: {result['shipment_id']}")
    print(f"Carrier: {result['carrier']}")
    print(f"Price: ${result['price']:.2f}")
    print(f"Transit: {result['transit_days']} days")
    print(f"Reliability: {result['reliability']:.1f}%")
    print("\n[SIMULATE 5M SHIPMENTS]")
    for i in range(5000000):
        ship = Shipment(f"S-{i}", "ORIG", "DEST", 100 + np.random.rand()*900, 1000 + np.random.rand()*99000, "std", datetime.now().timestamp())
        quotes = [CarrierQuote(f"CAR{j}", 200 + np.random.rand()*800, np.random.randint(2, 10), 90 + np.random.rand()*10, True, 0.8 + np.random.rand()*0.2) for j in range(6)]
        kernel.route_shipment(ship, quotes)
    stats = kernel.get_stats()
    print(f"\n{'='*60}")
    print("LOGISTICS SUMMARY")
    print("="*60)
    print(f"Shipments: {stats['shipments']:,}")
    print(f"Total Value: ${stats['total_value']:,.0f}")
    print(f"\n💰 ROYALTY: ${stats['royalty']:,.2f}")
    print(f"   At 100M shipments/year: ${(100000000 * 25)/10000:,.2f}/year")
    print(f"   Global logistics: $5T market")
    print(f"   Beneficiary: {stats['beneficiary']}")
    kernel.export_log('kl-105-lexfreight-log.json')


if __name__ == "__main__":
    main()
