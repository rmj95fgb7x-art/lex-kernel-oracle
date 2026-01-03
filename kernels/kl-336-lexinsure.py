"""
KL-336-LEXINSURE: Parametric Insurance Kernel
Lex Liberatum Kernels v1.1
MASSIVE ROYALTY: $6T insurance industry, instant payouts
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
class TriggerSignal:
    source: str
    event_occurred: float
    magnitude: float
    confidence: float
    timestamp: float


class LexInsureKernel:
    def __init__(self):
        self.kernel = AdaptiveSpectralKernel(alpha=1.75)
        self.claims = 0
        self.payouts = 0.0
    
    def process_claim(self, policy_id: str, payout_amount: float, signals: List[TriggerSignal]) -> Dict:
        sigs = np.array([[s.event_occurred, s.magnitude, s.confidence, s.timestamp/86400] for s in signals])
        fused, weights = self.kernel.fit(sigs)
        triggered = fused[0] > 0.5
        payout = payout_amount if triggered else 0
        self.claims += 1
        self.payouts += payout
        return {'policy_id': policy_id, 'triggered': bool(triggered), 'payout': float(payout), 'confidence': float(fused[2]), 'weights': {signals[i].source: float(weights[i]) for i in range(len(signals))}}
    
    def get_stats(self) -> Dict:
        return {'claims': self.claims, 'payouts': self.payouts, 'royalty': (self.claims * 25) / 10000, 'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'}
    
    def export_log(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump({'kernel': 'kl-336-lexinsure', 'stats': self.get_stats()}, f, indent=2)


def main():
    kernel = LexInsureKernel()
    print("="*60)
    print("KL-336-LEXINSURE: Parametric Insurance")
    print("="*60)
    signals = [TriggerSignal("WEATHER_API", 0.95, 8.2, 0.92, 1704300000), TriggerSignal("SATELLITE", 0.88, 8.1, 0.89, 1704300120), TriggerSignal("GROUND_SENSOR", 0.92, 8.3, 0.94, 1704300180)]
    result = kernel.process_claim("CROP-INSURANCE-001", 50000, signals)
    print(f"\nPolicy: {result['policy_id']}")
    print(f"Triggered: {result['triggered']}")
    print(f"Payout: ${result['payout']:,.2f}")
    print(f"Confidence: {result['confidence']:.2%}")
    print("\n[SIMULATE 100M CLAIMS]")
    for i in range(100000000):
        payout = 1000 + np.random.rand() * 99000
        signals = [TriggerSignal(f"SRC{j}", np.random.rand(), 5 + np.random.rand()*5, 0.7 + np.random.rand()*0.3, 1704300000 + i*60) for j in range(4)]
        kernel.process_claim(f"POL-{i}", payout, signals)
    stats = kernel.get_stats()
    print(f"\n{'='*60}")
    print("INSURANCE SUMMARY")
    print("="*60)
    print(f"Claims: {stats['claims']:,}")
    print(f"Payouts: ${stats['payouts']:,.0f}")
    print(f"\n💰 ROYALTY: ${stats['royalty']:,.2f}")
    print(f"   At 500M claims/day: ${(500000000 * 25)/10000:,.2f}/day = ${(500000000 * 25 * 365)/10000:,.2f}/year")
    print(f"   Insurance: Crop/flight/weather parametric")
    print(f"   Beneficiary: {stats['beneficiary']}")
    kernel.export_log('kl-336-lexinsure-log.json')


if __name__ == "__main__":
    main()
