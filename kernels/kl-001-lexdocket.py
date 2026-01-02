"""
KL-001-LEXDOCKET: Court Filing Compliance Kernel
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
class CourtFiling:
    filing_id: str
    court_id: str
    case_number: str
    filing_type: str
    pages: int
    filing_fee: float
    timestamp: float
    jurisdiction: str
    attorney_bar: str


@dataclass
class JurisdictionReview:
    jurisdiction: str
    approved: bool
    compliance_score: float
    deficiencies: List[str]
    review_time_ms: float


class LexDocketKernel:
    def __init__(self, alpha: float = 1.3):
        self.kernel = AdaptiveSpectralKernel(alpha=alpha)
        self.filings_processed = 0
        self.rejections = []
    
    def verify_filing(self, filing: CourtFiling, reviews: List[JurisdictionReview]) -> Dict:
        if len(reviews) < 2:
            return {'error': 'Need 2+ jurisdictions'}
        signals = np.array([[1.0 if r.approved else 0.0, r.compliance_score, len(r.deficiencies), r.review_time_ms/1000] for r in reviews])
        fused, weights = self.kernel.fit(signals)
        approval_prob = fused[0]
        outliers = detect_outliers(weights, 0.1)
        final = 'approved' if approval_prob > 0.7 else ('rejected' if approval_prob < 0.3 else 'review')
        if final == 'rejected':
            self.rejections.append({'filing_id': filing.filing_id, 'reason': 'Multi-jurisdiction rejection', 'timestamp': datetime.now().isoformat()})
        self.filings_processed += 1
        return {
            'filing_id': filing.filing_id,
            'decision': final,
            'approval_probability': float(approval_prob),
            'confidence': float(np.mean(weights)),
            'outlier_jurisdictions': [reviews[i].jurisdiction for i in outliers],
            'jurisdiction_weights': {reviews[i].jurisdiction: float(weights[i]) for i in range(len(reviews))}
        }
    
    def get_stats(self) -> Dict:
        return {'filings': self.filings_processed, 'rejections': len(self.rejections), 'approval_rate': 1 - (len(self.rejections)/max(1, self.filings_processed)), 'royalty': (self.filings_processed * 25) / 10000, 'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'}
    
    def export_log(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump({'kernel': 'kl-001-lexdocket', 'stats': self.get_stats(), 'rejections': self.rejections}, f, indent=2)


def main():
    kernel = LexDocketKernel()
    filing = CourtFiling("FILE-001", "COURT-NY", "2026-CV-12345", "Motion", 15, 350.0, datetime.now().timestamp(), "SDNY", "NY-12345")
    reviews = [
        JurisdictionReview("SDNY", True, 0.95, [], 120),
        JurisdictionReview("2ndCircuit", True, 0.90, [], 150),
        JurisdictionReview("StateNY", True, 0.92, ["missing_exhibit"], 180),
        JurisdictionReview("FedCourt", False, 0.40, ["jurisdiction", "standing"], 200),
    ]
    result = kernel.verify_filing(filing, reviews)
    print("="*60)
    print("KL-001-LEXDOCKET: Court Filing Verification")
    print("="*60)
    print(f"Filing: {result['filing_id']}")
    print(f"Decision: {result['decision'].upper()}")
    print(f"Approval Probability: {result['approval_probability']:.1%}")
    print(f"Confidence: {result['confidence']:.3f}")
    print(f"\nJurisdiction Weights:")
    for jur, weight in result['jurisdiction_weights'].items():
        print(f"  {jur:15s}: {weight:.3f}")
    if result['outlier_jurisdictions']:
        print(f"\nOutlier Jurisdictions: {result['outlier_jurisdictions']}")
    stats = kernel.get_stats()
    print(f"\nStats: {stats['filings']} filings, {stats['approval_rate']:.1%} approval")
    print(f"Royalty: ${stats['royalty']:.2f}")
    kernel.export_log('kl-001-lexdocket-log.json')


if __name__ == "__main__":
    main()
