"""
KL-052-LEXBANK: Real-Time Payment Fraud Detection Kernel
Lex Liberatum Kernels v1.1
HIGH ROYALTY POTENTIAL: Financial institutions process millions of transactions daily
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
class Transaction:
    txn_id: str
    account_id: str
    merchant_id: str
    amount: float
    location: str
    device_id: str
    ip_address: str
    velocity_1hr: int
    velocity_24hr: int
    avg_transaction_amount: float
    account_age_days: int
    timestamp: float


@dataclass
class FraudScore:
    bank_id: str
    fraud_probability: float
    risk_factors: List[str]
    ml_confidence: float
    rule_triggered: bool


class LexBankKernel:
    def __init__(self):
        self.kernel = TemporalAdaptiveKernel(alpha=1.25, beta=0.92, lambda_jitter=0.4, drift_threshold=0.08)
        self.fraud_blocks = []
        self.timestep = 0
        self.txns_processed = 0
        self.total_volume = 0.0
    
    def score_transaction(self, txn: Transaction, bank_scores: List[FraudScore]) -> Dict:
        if len(bank_scores) < 3:
            return {'error': 'Need 3+ banks'}
        signals = np.array([[s.fraud_probability, s.ml_confidence, 1.0 if s.rule_triggered else 0.0, len(s.risk_factors)] for s in bank_scores])
        fused, weights = self.kernel.update(signals)
        fraud_prob = fused[0]
        confidence = fused[1]
        velocity_anomaly = txn.velocity_1hr > 10 or txn.velocity_24hr > 50
        amount_anomaly = txn.amount > txn.avg_transaction_amount * 5
        new_device = txn.account_age_days > 30 and len(txn.device_id) < 10
        block = fraud_prob > 0.75 or (fraud_prob > 0.6 and (velocity_anomaly or amount_anomaly))
        if block:
            self.fraud_blocks.append({'txn_id': txn.txn_id, 'amount': txn.amount, 'fraud_prob': float(fraud_prob), 'timestamp': datetime.now().isoformat(), 'reason': 'HIGH_FRAUD' if fraud_prob > 0.75 else 'VELOCITY'})
        self.txns_processed += 1
        self.total_volume += txn.amount
        failed = [bank_scores[i].bank_id for i, w in enumerate(weights) if w < 0.08]
        return {'txn_id': txn.txn_id, 'fraud_probability': float(fraud_prob), 'confidence': float(confidence), 'block_transaction': block, 'velocity_anomaly': velocity_anomaly, 'amount_anomaly': amount_anomaly, 'suspicious_banks': failed, 'bank_weights': {bank_scores[i].bank_id: float(weights[i]) for i in range(len(bank_scores))}}
    
    def get_stats(self) -> Dict:
        return {'txns_processed': self.txns_processed, 'total_volume': self.total_volume, 'fraud_blocks': len(self.fraud_blocks), 'fraud_rate': len(self.fraud_blocks)/max(1, self.txns_processed), 'blocked_amount': sum(f['amount'] for f in self.fraud_blocks), 'royalty': (self.txns_processed * 25) / 10000, 'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'}
    
    def export_log(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump({'kernel': 'kl-052-lexbank', 'stats': self.get_stats(), 'fraud_blocks': self.fraud_blocks}, f, indent=2)


def main():
    kernel = LexBankKernel()
    print("="*60)
    print("KL-052-LEXBANK: Real-Time Payment Fraud Detection")
    print("="*60)
    print("\n[LEGITIMATE TRANSACTION]")
    txn_legit = Transaction("TXN-001", "ACCT-12345", "MERCH-999", 85.50, "NYC", "DEV-ABC123", "192.168.1.1", 2, 8, 75.0, 365, datetime.now().timestamp())
    scores_legit = [FraudScore("CHASE", 0.15, ["new_merchant"], 0.92, False), FraudScore("BOFA", 0.12, [], 0.95, False), FraudScore("WELLS", 0.18, ["new_merchant"], 0.88, False), FraudScore("CITI", 0.10, [], 0.94, False)]
    result = kernel.score_transaction(txn_legit, scores_legit)
    print(f"Transaction: {result['txn_id']}")
    print(f"Amount: ${txn_legit.amount:.2f}")
    print(f"Fraud Probability: {result['fraud_probability']:.1%}")
    print(f"Block: {result['block_transaction']}")
    print("\n[HIGH FRAUD - VELOCITY ATTACK]")
    txn_fraud = Transaction("TXN-002", "ACCT-67890", "MERCH-888", 2500.00, "Tokyo", "DEV-UNKNOWN", "45.33.2.155", 25, 80, 120.0, 7, datetime.now().timestamp())
    scores_fraud = [FraudScore("CHASE", 0.85, ["velocity", "new_device", "foreign"], 0.95, True), FraudScore("BOFA", 0.82, ["velocity", "amount"], 0.93, True), FraudScore("WELLS", 0.79, ["velocity", "location"], 0.91, True), FraudScore("CITI", 0.20, [], 0.60, False)]
    result = kernel.score_transaction(txn_fraud, scores_fraud)
    print(f"Transaction: {result['txn_id']}")
    print(f"Amount: ${txn_fraud.amount:.2f}")
    print(f"Fraud Probability: {result['fraud_probability']:.1%}")
    print(f"Velocity 1hr: {txn_fraud.velocity_1hr} txns")
    print(f"🚨 Block: {result['block_transaction']}")
    print(f"🚨 Velocity Anomaly: {result['velocity_anomaly']}")
    if result['suspicious_banks']:
        print(f"Suspicious Banks: {result['suspicious_banks']}")
    print("\n[SIMULATE 10K TRANSACTIONS]")
    for i in range(10000):
        is_fraud = np.random.rand() < 0.02
        if is_fraud:
            txn = Transaction(f"TXN-{i}", f"ACCT-{np.random.randint(10000)}", f"MERCH-{np.random.randint(1000)}", np.random.rand()*5000 + 1000, "Foreign", "DEV-UNK", "1.1.1.1", np.random.randint(15, 30), np.random.randint(50, 100), 100.0, 10, datetime.now().timestamp())
            scores = [FraudScore(f"BANK{j}", 0.7 + np.random.rand()*0.25, ["velocity"], 0.9, True) for j in range(4)]
        else:
            txn = Transaction(f"TXN-{i}", f"ACCT-{np.random.randint(10000)}", f"MERCH-{np.random.randint(1000)}", np.random.rand()*200 + 20, "USA", "DEV-REG", "192.168.1.1", np.random.randint(1, 5), np.random.randint(5, 15), 100.0, 200, datetime.now().timestamp())
            scores = [FraudScore(f"BANK{j}", np.random.rand()*0.3, [], 0.9, False) for j in range(4)]
        kernel.score_transaction(txn, scores)
    stats = kernel.get_stats()
    print(f"\n{'='*60}")
    print("FRAUD DETECTION SUMMARY")
    print("="*60)
    print(f"Transactions Processed: {stats['txns_processed']:,}")
    print(f"Total Volume: ${stats['total_volume']:,.2f}")
    print(f"Fraud Blocks: {stats['fraud_blocks']:,}")
    print(f"Fraud Rate: {stats['fraud_rate']:.2%}")
    print(f"Blocked Amount: ${stats['blocked_amount']:,.2f}")
    print(f"\n💰 ROYALTY: ${stats['royalty']:,.2f}")
    print(f"   At 1M txns/day: ${(1000000 * 25)/10000:,.2f}/day = ${(1000000 * 25 * 365)/10000:,.2f}/year")
    print(f"   Beneficiary: {stats['beneficiary']}")
    kernel.export_log('kl-052-lexbank-log.json')


if __name__ == "__main__":
    main()
