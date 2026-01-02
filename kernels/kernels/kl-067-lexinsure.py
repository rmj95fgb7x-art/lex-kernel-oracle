"""
KL-067-LEXINSURE: Insurance Claims Fraud Detection Kernel
Lex Liberatum Kernels v1.1
HIGH ROYALTY POTENTIAL: $80B annual insurance fraud in US alone
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
class InsuranceClaim:
    claim_id: str
    policy_id: str
    claimant_id: str
    claim_amount: float
    incident_type: str
    incident_date: float
    report_delay_days: int
    previous_claims: int
    policy_age_days: int
    witness_count: int
    police_report: bool
    medical_records: bool
    timestamp: float


@dataclass
class InsurerAssessment:
    insurer_id: str
    fraud_score: float
    approve: bool
    red_flags: List[str]
    investigation_recommended: bool


class LexInsureKernel:
    def __init__(self):
        self.kernel = AdaptiveSpectralKernel(alpha=1.15)
        self.claims_processed = 0
        self.fraud_detected = []
        self.total_claim_value = 0.0
        self.blocked_amount = 0.0
    
    def assess_claim(self, claim: InsuranceClaim, assessments: List[InsurerAssessment]) -> Dict:
        if len(assessments) < 3:
            return {'error': 'Need 3+ insurers'}
        signals = np.array([[a.fraud_score, 1.0 if a.approve else 0.0, len(a.red_flags), 1.0 if a.investigation_recommended else 0.0] for a in assessments])
        fused, weights = self.kernel.fit(signals)
        fraud_score = fused[0]
        approval_rate = fused[1]
        late_report = claim.report_delay_days > 30
        suspicious_history = claim.previous_claims > 5 and claim.policy_age_days < 730
        new_policy_large_claim = claim.policy_age_days < 90 and claim.claim_amount > 50000
        no_evidence = not claim.police_report and not claim.medical_records and claim.witness_count == 0
        deny = fraud_score > 0.7 or (fraud_score > 0.5 and (late_report or new_policy_large_claim or no_evidence))
        investigate = fraud_score > 0.4 or suspicious_history
        if deny:
            self.fraud_detected.append({'claim_id': claim.claim_id, 'amount': claim.claim_amount, 'fraud_score': float(fraud_score), 'timestamp': datetime.now().isoformat()})
            self.blocked_amount += claim.claim_amount
        self.claims_processed += 1
        self.total_claim_value += claim.claim_amount
        outliers = [i for i, w in enumerate(weights) if w < 0.1]
        return {'claim_id': claim.claim_id, 'fraud_score': float(fraud_score), 'approval_rate': float(approval_rate), 'deny_claim': deny, 'investigate': investigate, 'late_report': late_report, 'suspicious_history': suspicious_history, 'new_policy_large': new_policy_large_claim, 'no_evidence': no_evidence, 'outlier_insurers': [assessments[i].insurer_id for i in outliers], 'insurer_weights': {assessments[i].insurer_id: float(weights[i]) for i in range(len(assessments))}}
    
    def get_stats(self) -> Dict:
        return {'claims_processed': self.claims_processed, 'total_claim_value': self.total_claim_value, 'fraud_detected': len(self.fraud_detected), 'fraud_rate': len(self.fraud_detected)/max(1, self.claims_processed), 'blocked_amount': self.blocked_amount, 'savings': self.blocked_amount, 'royalty': (self.claims_processed * 25) / 10000, 'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'}
    
    def export_log(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump({'kernel': 'kl-067-lexinsure', 'stats': self.get_stats(),​​​​​​​​​​​​​​​​
