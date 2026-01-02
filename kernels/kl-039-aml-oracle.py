"""
KL-039-AML-ORACLE: Anti-Money Laundering Fusion Kernel
Lex Liberatum Kernels v1.1

Domain: Financial Services / RegTech
Use Case: Multi-bank transaction monitoring fusion

Features:
- Cross-institutional suspicious activity detection
- Real-time transaction scoring
- Network effect (more banks = better detection)
- FinCEN SAR filing support

Patent: PCT Pending
Royalty: 25bp → 0x44f8...C689
"""

import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.adaptive_spectral_kernel import AdaptiveSpectralKernel
from src.utils import detect_outliers


@dataclass
class Transaction:
    """Financial transaction."""
    txn_id: str
    sender_account: str  # Hashed
    receiver_account: str  # Hashed
    amount: float
    currency: str
    timestamp: float
    location: str
    method: str  # "wire", "ach", "crypto", etc.


@dataclass
class BankRiskScore:
    """Individual bank's risk assessment."""
    bank_id: str
    risk_score: float  # 0-100
    flags: List[str]  # ["structuring", "layering", "velocity"]
    confidence: float


class AMLOracle:
    """
    KL-039-AML-ORACLE: Multi-bank AML fusion.
    
    Aggregates risk scores from multiple banks to detect:
    - Money laundering patterns
    - Structuring (breaking up transactions)
    - Layering (complex transfers)
    - Network-wide suspicious activity
    
    Parameters
    ----------
    alpha : float, default=1.3
        Sensitivity
    sar_threshold : float, default=75.0
        Threshold for SAR filing recommendation
    """
    
    def __init__(self, alpha: float = 1.3, sar_threshold: float = 75.0):
        self.kernel = AdaptiveSpectralKernel(alpha=alpha)
        self.sar_threshold = sar_threshold
        self.transactions_scored = 0
        self.sars_filed = 0
    
    def score_transaction(
        self,
        txn: Transaction,
        bank_scores: List[BankRiskScore]
    ) -> Dict:
        """
        Score transaction with multi-bank fusion.
        
        Returns
        -------
        result : dict
            - final_risk_score: 0-100
            - sar_recommended: Boolean
            - confidence: 0-1
            - contributing_banks: Trusted banks
            - suspicious_banks: Outlier banks (possible false positives)
        """
        if len(bank_scores) < 2:
            return {'error': 'Need at least 2 banks'}
        
        # Convert to signals
        signals = np.array([[score.risk_score, score.confidence] for score in bank_scores])
        
        # Fuse
        fused, weights = self.kernel.fit(signals)
        final_risk = fused[0]
        
        # Detect outliers
        outliers = detect_outliers(weights, 0.1)
        suspicious_banks = [bank_scores[i].bank_id for i in outliers]
        
        # SAR decision
        sar_recommended = final_risk >= self.sar_threshold
        
        if sar_recommended:
            self.sars_filed += 1
        
        self.transactions_scored += 1
        
        return {
            'final_risk_score': float(final_risk),
            'sar_recommended': sar_recommended,
            'confidence': float(np.mean(weights)),
            'contributing_banks': [
                bank_scores[i].bank_id for i in range(len(bank_scores)) if i not in outliers
            ],
            'suspicious_banks': suspicious_banks,
            'flags_consensus': self._aggregate_flags(bank_scores, weights)
        }
    
    def _aggregate_flags(self, scores: List[BankRiskScore], weights: np.ndarray) -> List[str]:
        """Aggregate flags weighted by bank reliability."""
        flag_scores = {}
        for i, score in enumerate(scores):
            for flag in score.flags:
                flag_scores[flag] = flag_scores.get(flag, 0) + weights[i]
        
        return [flag for flag, weight in flag_scores.items() if weight > 0.5]
    
    def get_stats(self) -> Dict:
        """Get AML statistics."""
        return {
            'transactions_scored': self.transactions_scored,
            'sars_filed': self.sars_filed,
            'sar_rate': self.sars_filed / max(1, self.transactions_scored),
            'royalty': (self.transactions_scored * 25) / 10000
        }


def main():
    """Example."""
    oracle = AMLOracle()
    
    txn = Transaction(
        txn_id="TXN_001",
        sender_account="HASH_A",
        receiver_account="HASH_B",
        amount=9500.00,  # Just under $10k reporting threshold
        currency="USD",
        timestamp=datetime.now().timestamp(),
        location="US",
        method="wire"
    )
    
    # 4 banks score it
    scores = [
        BankRiskScore("JPM", 85.0, ["structuring", "velocity"], 0.9),
        BankRiskScore("CITI", 82.0, ["structuring"], 0.85),
        BankRiskScore("WELLS", 78.0, ["velocity"], 0.8),
        BankRiskScore("BOFA", 15.0, [], 0.5),  # Outlier (false negative)
    ]
    
    result = oracle.score_transaction(txn, scores)
    
    print("KL-039-AML-ORACLE: Transaction Risk Fusion")
    print(f"Risk Score: {result['final_risk_score']:.1f}/100")
    print(f"SAR Recommended: {result['sar_recommended']}")
    print(f"Flags: {result['flags_consensus']}")
    print(f"Suspicious Banks: {result['suspicious_banks']}")


if __name__ == "__main__":
    main()
