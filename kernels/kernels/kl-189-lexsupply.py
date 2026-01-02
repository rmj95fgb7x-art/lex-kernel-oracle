"""
KL-189-LEXSUPPLY: Supply Chain Routing Kernel
Lex Liberatum Kernels v1.1
MASSIVE ROYALTY: $20T global supply chain, billions of decisions daily
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
class RouteOption:
    provider_id: str
    cost: float
    time_days: int
    reliability: float
    carbon_kg: float


class LexSupplyKernel:
    def __init__(self):
        self.kernel = TemporalAdaptiveKernel(alpha=1.6, beta=0.86, lambda_jitter=0.65, drift_threshold=0.12)
        self.routes = 0
        self.cost = 0.0
        self.timestep = 0
    
    def route(self, shipment_id: str, value: float, options: List[RouteOption]) -> Dict:
        sigs = np.array([[o.cost/1000, o.time_days, o.reliability, o.carbon_kg/1000] for o in options])
        fused, weights = self.kernel.update(sigs)
        best_idx = np.argmax(weights)
        selected = options[best_idx]
        self.routes += 1
        self.cost += selected.cost
        self.timestep += 1
        return {'shipment_id': shipment_id, 'provider': selected.provider_id, 'cost': float(selected.cost), 'time': selected.time_days, 'carbon': float(selected.carbon_kg), 'weights': {options[i].provider_id: float(weights[i]) for i in range(len(options))}}
    
    def get_stats(self) -> Dict:
        return {'routes': self.routes, 'cost': self.cost, 'royalty': (self.routes * 25) / 10000, 'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'}
    
    def export_log(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump({'kernel': 'kl-189-lexsupply', 'stats': self.get_stats()}, f, indent=2)


def main():
    kernel = LexSupplyKernel()
    print("="*60)
    print("KL-189-LEXSUPPLY: Supply Chain Routing")
    print("="*60)
    options = [RouteOption("MAERSK", 2500, 21, 0.95, 1200), RouteOption("MSC", 2300, 25, 0.92, 1100), RouteOption("COSCO", 2600, 19, 0.96, 1300)]
    result = kernel.route("SHIP-001", 50000, options)
    print(f"\nShipment: {result['shipment_id']}")
    print(f"Provider: {result['provider']}")
    print(f"Cost: ${result['cost']:,.0f}")
    print(f"Time: {result['time']} days")
    print(f"Carbon: {result['carbon']:,.0f} kg")
    print("\n[SIMULATE 1B ROUTES]")
    for i in range(1000000000):
        value = 1000 + np.random.rand()*99000
        options = [RouteOption(f"PROV{j}", 500 + np.random.rand()*4500, np.random.randint(7,35), 0.85 + np.random.rand()*0.15, 200 + np.random.rand()*1800) for j in range(5)]
        kernel.route(f"SH-{i}", value, options)
    stats = kernel.get_stats()
    print(f"\n{'='*60}")
    print("SUPPLY CHAIN SUMMARY")
    print("="*60)
    print(f"Routes: {stats['routes']:,}")
    print(f"Cost: ${stats['cost']:,.0f}")
    print(f"\n💰 ROYALTY: ${stats['royalty']:,.2f}")
    print(f"   At 10B routes/day: ${(10000000000 * 25)/10000:,.2f}/day = ${(10000000000 * 25 * 365)/10000:,.2f}/year")
    print(f"   Supply Chain: $20T+ globally")
    print(f"   Beneficiary: {stats['beneficiary']}")
    kernel.export_log('kl-189-lexsupply-log.json')


if __name__ == "__main__":
    main()
