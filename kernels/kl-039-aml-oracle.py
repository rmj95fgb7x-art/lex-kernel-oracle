"""
KL-039-AML-ORACLE: Anti-Money Laundering Fusion Kernel
Lex Liberatum Kernels v1.1

Domain: Financial Services / RegTech
Use Case: Multi-bank transaction monitoring fusion

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
class Transaction:
    txn_id: str
    sender_account: str
    receiver_account: str
    amount: float
    currency: str
    timestamp: float
    location: str
    method: str


@dataclass
class BankRiskScore:
    bank_id: str
    risk_score: float
    flags: List[str]
    confidence: float


class AMLOracle:
    def __init__(self, alpha: float = 1.3, sar_threshold: float = 75.0):
        self.kernel = AdaptiveSpectralKernel(alpha=alpha)
        self.sar_threshold = sar_threshold
        self.transactions_scored = 0
        self.sars_filed = 0
        self.alerts = []
    
    def score_transaction(self, txn: Transaction, bank_scores: List[BankRiskScore]) -> Dict:
        if len(bank_scores) < 2:
            return {'error': 'Need at least 2 banks'}
        
        signals = np.array([[score.risk_score, score.confidence] for score in bank_scores])
        fused, weights = self.kernel.fit(signals)
        final_risk = fused[0]
        
        outliers = detect_outliers(weights, 0.1)
        suspicious_banks = [bank_scores[i].bank_id for i in outliers]
        
        sar_recommended = final_risk >= self.sar_threshold
        
        if sar_recommended:
            self.sars_filed += 1
            alert = {'txn_id': txn.txn_id, 'risk': float(final_risk), 'timestamp': datetime.now().isoformat(), 'amount': txn.amount}
            self.alerts.append(alert)
        
        self.transactions_scored += 1
        
        flag_scores = {}
        for i, score in enumerate(bank_scores):
            for flag in score.flags:
                flag_scores[flag] = flag_scores.get(flag, 0) + weights[i]
        consensus_flags = [flag for flag, weight in flag_scores.items() if weight > 0.5]
        
        return {
            'txn_id': txn.txn_id,
            'final_risk_score': float(final_risk),
            'sar_recommended': sar_recommended,
            'confidence': float(np.mean(weights)),
            'contributing_banks': [bank_scores[i].bank_id for i in range(len(bank_scores)) if i not in outliers],
            'suspicious_banks': suspicious_banks,
            'flags_consensus': consensus_flags
        }
    
    def get_stats(self) -> Dict:
        return {'transactions': self.transactions_scored, 'sars_filed': self.sars_filed, 'sar_rate': self.sars_filed / max(1, self.transactions_scored), 'royalty': (self.transactions_scored * 25) / 10000, 'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'}
    
    def export_log(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump({'kernel': 'kl-039-aml-oracle', 'stats': self.get_stats(), 'alerts': self.alerts}, f, indent=2)


def main():
    oracle = AMLOracle()
    
    transactions = [
        Transaction("TXN_001", "HASH_A", "HASH_B", 9500.00, "USD", datetime.now().timestamp(), "US", "wire"),
        Transaction("TXN_002", "HASH_C", "HASH_D", 9800.00, "USD", datetime.now().timestamp(), "US", "wire"),
        Transaction("TXN_003", "HASH_E", "HASH_F", 15000.00, "USD", datetime.now().timestamp(), "US", "crypto"),
    ]
    
    print("="*60)
    print("KL-039-AML-ORACLE: Transaction Risk Fusion")
    print("="*60)
    
    for txn in transactions:
        scores = [
            BankRiskScore("JPM", 85.0 if txn.amount < 10000 else 65.0, ["structuring", "velocity"] if txn.amount < 10000 else ["velocity"], 0.9),
            BankRiskScore("CITI", 82.0 if txn.amount < 10000 else 60.0, ["structuring"] if txn.amount < 10000 else [], 0.85),
            BankRiskScore("WELLS", 78.0, ["velocity"], 0.8),
            BankRiskScore("BOFA", 15.0, [], 0.5),
        ]
        
        result = oracle.score_transaction(txn, scores)
        print(f"\nTransaction: {result['txn_id']}")
        print(f"  Amount: ${txn.amount:,.2f}")
        print(f"  Risk Score: {result['final_risk_score']:.1f}/100")
        print(f"  SAR Filed: {'YES ⚠️' if result['sar_recommended'] else 'No'}")
        print(f"  Flags: {result['flags_consensus']}")
        if result['suspicious_banks']:
            print(f"  Suspicious Banks: {result['suspicious_banks']}")
    
    stats = oracle.get_stats()
    print(f"\n{'='*60}")
    print("SUMMARY STATISTICS")
    print("="*60)
    print(f"Transactions Scored: {stats['transactions']}")
    print(f"SARs Filed: {stats['sars_filed']}")
    print(f"SAR Rate: {stats['sar_rate']:.1%}")
    print(f"Royalty: ${stats['royalty']:.2f}")
    print(f"Beneficiary: {stats['beneficiary']}")
    
    oracle.export_log('kl-039-aml-oracle-log.json')
    print(f"\nLog exported to: kl-039-aml-oracle-log.json")


if __name__ == "__main__":
    main()
