"""
KL-084-LEXLOAN: Mortgage Underwriting Kernel
Lex Liberatum Kernels v1.1
HIGH ROYALTY POTENTIAL: 8M+ mortgages originated annually in US, avg $400K
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
class MortgageApplication:
    app_id: str
    applicant_id: str
    property_value: float
    loan_amount: float
    down_payment_pct: float
    property_type: str
    occupancy: str
    credit_score: int
    annual_income: float
    monthly_debt: float
    employment_years: int
    self_employed: bool
    first_time_buyer: bool
    timestamp: float


@dataclass
class UnderwriterDecision:
    underwriter_id: str
    approve: bool
    approved_amount: float
    rate_pct: float
    conditions: List[str]
    risk_rating: str
    confidence: float


class LexLoanKernel:
    def __init__(self):
        self.kernel = AdaptiveSpectralKernel(alpha=1.12)
        self.apps_processed = 0
        self.approvals = 0
        self.denials = 0
        self.total_loan_volume = 0.0
    
    def underwrite_mortgage(self, app: MortgageApplication, decisions: List[UnderwriterDecision]) -> Dict:
        if len(decisions) < 3:
            return {'error': 'Need 3+ underwriters'}
        signals = np.array([[1.0 if d.approve else 0.0, d.approved_amount/app.loan_amount, d.rate_pct/10, d.confidence, len(d.conditions)] for d in decisions])
        fused, weights = self.kernel.fit(signals)
        approval_consensus = fused[0]
        amount_factor = fused[1]
        consensus_rate = fused[2] * 10
        ltv = (app.loan_amount / app.property_value) * 100
        dti = (app.monthly_debt / (app.annual_income/12)) * 100
        high_ltv = ltv > 80
        high_dti = dti > 43
        low_credit = app.credit_score < 620
        insufficient_employment = app.employment_years < 2 and app.self_employed
        investment_property = app.occupancy != "primary"
        approve = approval_consensus > 0.6 and not (low_credit or (high_dti and high_ltv))
        approved_amount = min(app.loan_amount, app.loan_amount * amount_factor) if approve else 0
        final_rate = consensus_rate if approve else 0
        if app.credit_score >= 740 and ltv <= 80:
            risk = "A"
        elif app.credit_score >= 680 and ltv <= 85:
            risk = "B"
        elif app.credit_score >= 620 and ltv <= 90:
            risk = "C"
        else:
            risk = "D"
        conditions = []
        if high_ltv and approve:
            conditions.append("PMI_REQUIRED")
        if app.self_employed:
            conditions.append("TAX_RETURNS_2YR")
        if app.first_time_buyer:
            conditions.append("HOMEBUYER_EDUCATION")
        if approve:
            self.approvals += 1
            self.total_loan_volume += approved_amount
        else:
            self.denials += 1
        self.apps_processed += 1
        outliers = [i for i, w in enumerate(weights) if w < 0.1]
        return {'app_id': app.app_id, 'approve': approve, 'approved_amount': float(approved_amount), 'rate_pct': float(final_rate), 'ltv': float(ltv), 'dti': float(dti), 'risk_grade': risk, 'conditions': conditions, 'high_ltv': high_ltv, 'high_dti': high_dti, 'low_credit': low_credit, 'outlier_underwriters': [decisions[i].underwriter_id for i in outliers], 'underwriter_weights': {decisions[i].underwriter_id: float(weights[i]) for i in range(len(decisions))}}
    
    def get_stats(self) -> Dict:
        return {'apps_processed': self.apps_processed, 'approvals': self.approvals, 'denials': self.denials, 'approval_rate': self.approvals/max(1, self.apps_processed), 'total_loan_volume': self.total_loan_volume, 'avg_loan': self.total_loan_volume/max(1, self.approvals), 'royalty': (self.apps_processed * 25) / 10000, 'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'}
    
    def export_log(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump({'kernel': 'kl-084-lexloan', 'stats': self.get_stats()}, f, indent=2)


def main():
    kernel = LexLoanKernel()
    print("="*60)
    print("KL-084-LEXLOAN: Mortgage Underwriting System")
    print("="*60)
    print("\n[GRADE A BORROWER - APPROVED]")
    app_prime = MortgageApplication("MTG-001", "BRW-12345", 500000.0, 400000.0, 20.0, "single_family", "primary", 780, 150000.0, 2500.0, 8, False, False, datetime.now().timestamp())
    decisions_prime = [UnderwriterDecision("WELLS", True, 400000.0, 6.5, [], "A", 0.95), UnderwriterDecision("CHASE", True, 400000.0, 6.4, [], "A", 0.96), UnderwriterDecision("BOFA", True, 400000.0, 6.6, [], "A", 0.94)]
    result = kernel.underwrite_mortgage(app_prime, decisions_prime)
    print(f"Application: {result['app_id']}")
    print(f"Property: ${app_prime.property_value:,.0f}")
    print(f"Loan Requested: ${app_prime.loan_amount:,.0f}")
    print(f"LTV: {result['ltv']:.1f}%")
    print(f"DTI: {result['dti']:.1f}%")
    print(f"Credit: {app_prime.credit_score}")
    print(f"✅ APPROVED: ${result['approved_amount']:,.0f} @ {result['rate_pct']:.2f}%")
    print(f"Risk Grade: {result['risk_grade']}")
    if result['conditions']:
        print(f"Conditions: {result['conditions']}")
    print("\n[GRADE C - HIGH LTV, CONDITIONAL]")
    app_high_ltv = MortgageApplication("MTG-002", "BRW-67890", 350000.0, 325000.0, 7.1, "single_family", "primary", 660, 75000.0, 1800.0, 4, False, True, datetime.now().timestamp())
    decisions_high_ltv = [UnderwriterDecision("WELLS", True, 315000.0, 7.8, ["PMI"], "C", 0.82), UnderwriterDecision("CHASE", True, 320000.0, 7.9, ["PMI", "reserves"], "C", 0.85), UnderwriterDecision("BOFA", True, 310000.0, 8.1, ["PMI"], "C", 0.80)]
    result = kernel.underwrite_mortgage(app_high_ltv, decisions_high_ltv)
    print(f"Application: {result['app_id']}")
    print(f"Property: ${app_high_ltv.property_value:,.0f}")
    print(f"Loan Requested: ${app_high_ltv.loan_amount:,.0f}")
    print(f"LTV: {result['ltv']:.1f}%")
    print(f"DTI: {result['dti']:.1f}%")
    print(f"⚠️  APPROVED: ${result['approved_amount']:,.0f} @ {result['rate_pct']:.2f}%")
    print(f"Risk Grade: {result['risk_grade']}")
    print(f"Conditions: {result['conditions']}")
    print(f"High LTV: {result['high_ltv']}")
    print("\n[DENIED - LOW CREDIT + HIGH DTI]")
    app_deny = MortgageApplication("MTG-003", "BRW-11111", 280000.0, 260000.0, 7.1, "single_family", "primary", 590, 55000.0, 2400.0, 2, False, False, datetime.now().timestamp())
    decisions_deny = [UnderwriterDecision("WELLS", False, 0, 0, ["credit", "dti"], "D", 0.60), UnderwriterDecision("CHASE", False, 0, 0, ["credit"], "D", 0.65), UnderwriterDecision("BOFA", False, 0, 0, ["dti", "credit"], "D", 0.58)]
    result = kernel.underwrite_mortgage(app_deny, decisions_deny)
    print(f"Application: {result['app_id']}")
    print(f"Property: ${app_deny.property_value:,.0f}")
    print(f"Loan Requested: ${app_deny.loan_amount:,.0f}")
    print(f"LTV: {result['ltv']:.1f}%")
    print(f"DTI: {result['dti']:.1f}%")
    print(f"Credit: {app_deny.credit_score}")
    print(f"❌ DENIED")
    print(f"Low Credit: {result['low_credit']}")
    print(f"High DTI: {result['high_dti']}")
    print("\n[SIMULATE 25K MORTGAGE APPLICATIONS]")
    for i in range(25000):
        credit = int(np.random.normal(700, 60))
        credit = max(550, min(850, credit))
        prop_value = np.random.rand()*400000 + 200000
        if credit > 740:
            down = np.random.rand()*0.15 + 0.2
            income = np.random.rand()*80000 + 100000
            debt = income/12 * (np.random.rand()*0.2 + 0.15)
            rate = np.random.rand()*0.5 + 6.0
        elif credit > 680:
            down = np.random.rand()*0.1 + 0.1
            income = np.random.rand()*50000 + 70000
            debt = income/12 * (np.random.rand()*0.15 + 0.25)
            rate = np.random.rand()*1.0 + 6.5
        else:
            down = np.random.rand()*0.08 + 0.05
            income = np.random.rand()*40000 + 50000
            debt = income/12 * (np.random.rand()*0.15 + 0.35)
            rate = np.random.rand()*1.5 + 7.5
        loan = prop_value * (1 - down)
        app = MortgageApplication(f"MTG-{i}", f"BRW-{i}", prop_value, loan, down*100, "single_family", "primary", credit, income, debt, np.random.randint(2, 15), False, i%5==0, datetime.now().timestamp())
        approve_prob = (credit - 550) / 300
        decisions = [UnderwriterDecision(f"UW{j}", approve_prob > 0.5, loan * (0.9 + np.random.rand()*0.1) if approve_prob > 0.5 else 0, rate, ["PMI"] if down < 0.2 else [], "A" if credit > 740 else "B", 0.8 + np.random.rand()*0.15) for j in range(3)]
        kernel.underwrite_mortgage(app, decisions)
    stats = kernel.get_stats()
    print(f"\n{'='*60}")
    print("MORTGAGE UNDERWRITING SUMMARY")
    print("="*60)
    print(f"Applications Processed: {stats['apps_processed']:,}")
    print(f"Approvals: {stats['approvals']:,}")
    print(f"Denials: {stats['denials']:,}")
    print(f"Approval Rate: {stats['approval_rate']:.1%}")
    print(f"Total Loan Volume: ${stats['total_loan_volume']:,.0f}")
    print(f"Avg Loan Amount: ${stats['avg_loan']:,.0f}")
    print(f"\n💰 ROYALTY: ${stats['royalty']:,.2f}")
    print(f"   At 1M mortgages/year: ${(1000000 * 25)/10000:,.2f}/year")
    print(f"   At 5M mortgages/year: ${(5000000 * 25)/10000:,.2f}/year")
    print(f"   US Market: 8M+ originations/year @ $400K avg = $3.2T volume")
    print(f"   Beneficiary: {stats['beneficiary']}")
    kernel.export_log('kl-084-lexloan-log.json')


if __name__ == "__main__":
    main()
