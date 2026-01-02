"""
KL-073-LEXCREDIT: Credit Decisioning Kernel
Lex Liberatum Kernels v1.1
HIGH ROYALTY POTENTIAL: 200M+ credit decisions annually in US alone
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
class CreditApplication:
    app_id: str
    applicant_id: str
    requested_amount: float
    requested_term_months: int
    annual_income: float
    employment_length_months: int
    debt_to_income: float
    num_accounts: int
    num_delinquencies: int
    num_inquiries_6mo: int
    housing_status: str
    purpose: str
    timestamp: float


@dataclass
class BureauScore:
    bureau_id: str
    credit_score: int
    approve_recommendation: bool
    max_approved_amount: float
    suggested_apr: float
    risk_tier: str


class LexCreditKernel:
    def __init__(self):
        self.kernel = AdaptiveSpectralKernel(alpha=1.18)
        self.apps_processed = 0
        self.approvals = 0
        self.denials = 0
        self.total_approved_amount = 0.0
    
    def evaluate_application(self, app: CreditApplication, bureau_scores: List[BureauScore]) -> Dict:
        if len(bureau_scores) < 3:
            return {'error': 'Need 3+ bureaus'}
        signals = np.array([[b.credit_score/850, 1.0 if b.approve_recommendation else 0.0, b.max_approved_amount/app.requested_amount, b.suggested_apr/100] for b in bureau_scores])
        fused, weights = self.kernel.fit(signals)
        consensus_score = fused[0] * 850
        approval_rate = fused[1]
        amount_factor = fused[2]
        consensus_apr = fused[3] * 100
        high_dti = app.debt_to_income > 0.43
        excessive_inquiries = app.num_inquiries_6mo > 6
        delinquent = app.num_delinquencies > 0
        unstable_employment = app.employment_length_months < 12
        thin_file = app.num_accounts < 3
        approve = approval_rate > 0.6 and consensus_score > 620 and not (high_dti and delinquent)
        approved_amount = min(app.requested_amount, app.requested_amount * amount_factor) if approve else 0
        final_apr = consensus_apr if approve else 0
        if consensus_score < 580:
            risk = "high"
        elif consensus_score < 670:
            risk = "medium"
        elif consensus_score < 740:
            risk = "low"
        else:
            risk = "prime"
        if approve:
            self.approvals += 1
            self.total_approved_amount += approved_amount
        else:
            self.denials += 1
        self.apps_processed += 1
        outliers = [i for i, w in enumerate(weights) if w < 0.1]
        return {'app_id': app.app_id, 'consensus_credit_score': int(consensus_score), 'approve': approve, 'approved_amount': float(approved_amount), 'apr': float(final_apr), 'risk_tier': risk, 'high_dti': high_dti, 'excessive_inquiries': excessive_inquiries, 'delinquent': delinquent, 'thin_file': thin_file, 'outlier_bureaus': [bureau_scores[i].bureau_id for i in outliers], 'bureau_weights': {bureau_scores[i].bureau_id: float(weights[i]) for i in range(len(bureau_scores))}}
    
    def get_stats(self) -> Dict:
        return {'apps_processed': self.apps_processed, 'approvals': self.approvals, 'denials': self.denials, 'approval_rate': self.approvals/max(1, self.apps_processed), 'total_approved': self.total_approved_amount, 'avg_approved': self.total_approved_amount/max(1, self.approvals), 'royalty': (self.apps_processed * 25) / 10000, 'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'}
    
    def export_log(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump({'kernel': 'kl-073-lexcredit', 'stats': self.get_stats()}, f, indent=2)


def main():
    kernel = LexCreditKernel()
    print("="*60)
    print("KL-073-LEXCREDIT: Credit Decisioning System")
    print("="*60)
    print("\n[PRIME BORROWER - APPROVED]")
    app_prime = CreditApplication("APP-001", "USR-12345", 25000.0, 60, 95000.0, 84, 0.28, 12, 0, 1, "own", "debt_consolidation", datetime.now().timestamp())
    scores_prime = [BureauScore("EXPERIAN", 780, True, 25000.0, 6.5, "prime"), BureauScore("EQUIFAX", 775, True, 25000.0, 6.8, "prime"), BureauScore("TRANSUNION", 782, True, 25000.0, 6.3, "prime")]
    result = kernel.evaluate_application(app_prime, scores_prime)
    print(f"Application: {result['app_id']}")
    print(f"Requested: ${app_prime.requested_amount:,.2f}")
    print(f"Consensus Score: {result['consensus_credit_score']}")
    print(f"✅ APPROVED: ${result['approved_amount']:,.2f} @ {result['apr']:.2f}% APR")
    print(f"Risk Tier: {result['risk_tier']}")
    print("\n[SUBPRIME - CONDITIONAL APPROVAL]")
    app_sub = CreditApplication("APP-002", "USR-67890", 15000.0, 48, 48000.0, 36, 0.38, 8, 1, 3, "rent", "home_improvement", datetime.now().timestamp())
    scores_sub = [BureauScore("EXPERIAN", 640, True, 10000.0, 18.5, "medium"), BureauScore("EQUIFAX", 635, True, 9500.0, 19.2, "medium"), BureauScore("TRANSUNION", 645, True, 10500.0, 17.8, "medium")]
    result = kernel.evaluate_application(app_sub, scores_sub)
    print(f"Application: {result['app_id']}")
    print(f"Requested: ${app_sub.requested_amount:,.2f}")
    print(f"Consensus Score: {result['consensus_credit_score']}")
    print(f"⚠️  APPROVED: ${result['approved_amount']:,.2f} @ {result['apr']:.2f}% APR")
    print(f"Risk Tier: {result['risk_tier']}")
    print(f"Delinquencies: {result['delinquent']}")
    print("\n[HIGH RISK - DENIED]")
    app_deny = CreditApplication("APP-003", "USR-11111", 20000.0, 60, 32000.0, 8, 0.52, 4, 3,
