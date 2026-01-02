"""
KL-045-LEXCRYPTO: DeFi Compliance Kernel
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
class DeFiTransaction:
    txn_hash: str
    protocol: str
    sender: str
    receiver: str
    amount_usd: float
    gas_fee: float
    slippage_pct: float
    liquidity_depth: float
    timestamp: float


@dataclass
class OraclePrice:
    oracle_id: str
    price_usd: float
    confidence: float
    data_sources: int
    last_update: float


class LexCryptoKernel:
    def __init__(self, alpha: float = 1.2):
        self.kernel = AdaptiveSpectralKernel(alpha=alpha)
        self.txns_validated = 0
        self.manipulation_alerts = []
    
    def validate_price(self, txn: DeFiTransaction, oracles: List[OraclePrice]) -> Dict:
        if len(oracles) < 3:
            return {'error': 'Need 3+ oracles'}
        signals = np.array([[o.price_usd, o.confidence, o.data_sources, datetime.now().timestamp() - o.last_update] for o in oracles])
        fused, weights = self.kernel.fit(signals)
        consensus_price = fused[0]
        outliers = detect_outliers(weights, 0.1)
        manipulated_oracles = [oracles[i].oracle_id for i in outliers]
        price_deviation = abs(consensus_price - txn.amount_usd) / consensus_price if consensus_price > 0 else 0
        manipulation_detected = price_deviation > 0.05 or len(manipulated_oracles) > len(oracles) * 0.3
        if manipulation_detected:
            self.manipulation_alerts.append({'txn': txn.txn_hash, 'deviation': price_deviation, 'oracles': manipulated_oracles, 'timestamp': datetime.now().isoformat()})
        self.txns_validated += 1
        return {
            'txn_hash': txn.txn_hash,
            'consensus_price': float(consensus_price),
            'reported_amount': txn.amount_usd,
            'price_deviation': float(price_deviation),
            'manipulation_detected': manipulation_detected,
            'manipulated_oracles': manipulated_oracles,
            'confidence': float(np.mean(weights)),
            'oracle_weights': {oracles[i].oracle_id: float(weights[i]) for i in range(len(oracles))},
            'valid': not manipulation_detected
        }
    
    def get_stats(self) -> Dict:
        return {'txns': self.txns_validated, 'alerts': len(self.manipulation_alerts), 'manipulation_rate': len(self.manipulation_alerts)/max(1, self.txns_validated), 'royalty': (self.txns_validated * 25) / 10000, 'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'}
    
    def export_log(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump({'kernel': 'kl-045-lexcrypto', 'stats': self.get_stats(), 'alerts': self.manipulation_alerts}, f, indent=2)


def main():
    kernel = LexCryptoKernel()
    txn = DeFiTransaction("0xabc123", "Uniswap", "0xsender", "0xreceiver", 50000.0, 25.0, 0.5, 1e6, datetime.now().timestamp())
    oracles = [
        OraclePrice("Chainlink", 49800.0, 0.98, 12, datetime.now().timestamp() - 10),
        OraclePrice("Band", 49900.0, 0.95, 8, datetime.now().timestamp() - 15),
        OraclePrice("API3", 50100.0, 0.97, 10, datetime.now().timestamp() - 5),
        OraclePrice("Tellor", 52000.0, 0.60, 3, datetime.now().timestamp() - 300),
    ]
    result = kernel.validate_price(txn, oracles)
    print("="*60)
    print("KL-045-LEXCRYPTO: DeFi Price Validation")
    print("="*60)
    print(f"Transaction: {result['txn_hash'][:10]}...")
    print(f"Consensus Price: ${result['consensus_price']:,.2f}")
    print(f"Reported Amount: ${result['reported_amount']:,.2f}")
    print(f"Deviation: {result['price_deviation']:.2%}")
    print(f"Valid: {result['valid']}")
    print(f"\nOracle Weights:")
    for oracle, weight in result['oracle_weights'].items():
        print(f"  {oracle:15s}: {weight:.3f}")
    if result['manipulated_oracles']:
        print(f"\n⚠️  Manipulated Oracles: {result['manipulated_oracles']}")
    stats = kernel.get_stats​​​​​​​​​​​​​​​​
