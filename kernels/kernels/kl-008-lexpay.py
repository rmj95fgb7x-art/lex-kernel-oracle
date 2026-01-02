"""
KL-008-LEXPAY: Payment Routing Compliance Kernel
Lex Liberatum Kernels v1.1
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
from src.utils import detect_outliers


@dataclass
class PaymentRoute:
    route_id: str
    sender: str
    receiver: str
    amount: float
    currency: str
    fee_pct: float
    latency_ms: float
    compliance_score: float
    timestamp: float


class LexPayKernel:
    def __init__(self, alpha: float = 1.4):
        self.kernel = AdaptiveSpectralKernel(alpha=alpha)
        self.routes_evaluated = 0
        self.total_volume = 0.0
    
    def select_optimal_route(self, routes: List[PaymentRoute]) -> Dict:
        signals = np.array([[r.fee_pct, r.latency_ms, r.compliance_score, r.amount] for r in routes])
        fused, weights = self.kernel.fit(signals)
        best_idx = np.argmax(weights)
        outliers = detect_outliers(weights, 0.1)
        self.routes_evaluated += len(routes)
        self.total_volume += routes[best_idx].amount
        return {
            'selected_route': routes[best_idx].route_id,
            'fee': routes[best_idx].fee_pct,
            'latency': routes[best_idx].latency_ms,
            'compliance': routes[best_idx].compliance_score,
            'confidence': float(weights[best_idx]),
            'rejected_routes': [routes[i].route_id for i in outliers],
            'all_weights': {routes[i].route_id: float(weights[i]) for i in range(len(routes))}
        }
    
    def get_stats(self) -> Dict:
        return {'routes_evaluated': self.routes_evaluated, 'volume': self.total_volume, 'royalty': (self.routes_evaluated * 25) / 10000, 'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'}
    
    def export_log(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump({'kernel': 'kl-008-lexpay', 'stats': self.get_stats()}, f, indent=2)


def main():
    kernel = LexPayKernel()
    routes = [
        PaymentRoute("SWIFT", "SENDER_A", "RECEIVER_B", 10000.0, "USD", 0.5, 2000, 0.95, datetime.now().timestamp()),
        PaymentRoute("ACH", "SENDER_A", "RECEIVER_B", 10000.0, "USD", 0.1, 86400000, 0.98, datetime.now().timestamp()),
        PaymentRoute("CRYPTO", "SENDER_A", "RECEIVER_B", 10000.0, "USDC", 0.05, 300, 0.85, datetime.now().timestamp()),
        PaymentRoute("WIRE", "SENDER_A", "RECEIVER_B", 10000.0, "USD", 1.0, 1500, 0.99, datetime.now().timestamp()),
    ]
    result = kernel.select_optimal_route(routes)
    print("="*60)
    print("KL-008-LEXPAY: Payment Routing Optimization")
    print("="*60)
    print(f"Selected: {result['selected_route']}")
    print(f"Fee: {result['fee']:.2f}%")
    print(f"Latency: {result['latency']:.0f}ms")
    print(f"Compliance: {result['compliance']:.2f}")
    print(f"Confidence: {result['confidence']:.3f}")
    print(f"\nAll Route Weights:")
    for route, weight in result['all_weights'].items():
        print(f"  {route:10s}: {weight:.3f}")
    stats = kernel.get_stats()
    print(f"\nRoyalty: ${stats['royalty']:.2f}")
    kernel.export_log('kl-008-lexpay-log.json')


if __name__ == "__main__":
    main()
