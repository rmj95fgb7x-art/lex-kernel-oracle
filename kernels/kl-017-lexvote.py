"""
KL-017-LEXVOTE: Election Integrity Monitoring Kernel
Lex Liberatum Kernels v1.1

Domain: Civic Technology / Election Security
Use Case: Multi-precinct vote count verification

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
class PrecinctResult:
    precinct_id: str
    registered_voters: int
    ballots_cast: int
    candidate_a_votes: int
    candidate_b_votes: int
    candidate_c_votes: int
    timestamp: float


class LexVoteKernel:
    def __init__(self, alpha: float = 1.4):
        self.kernel = AdaptiveSpectralKernel(alpha=alpha)
        self.anomalies = []
        self.verifications_performed = 0
    
    def verify_results(self, results: List[PrecinctResult]) -> Dict:
        signals = []
        for r in results:
            turnout = r.ballots_cast / max(1, r.registered_voters)
            total_votes = r.candidate_a_votes + r.candidate_b_votes + r.candidate_c_votes
            signal = np.array([turnout, r.candidate_a_votes / max(1, total_votes), r.candidate_b_votes / max(1, total_votes), r.candidate_c_votes / max(1, total_votes)])
            signals.append(signal)
        
        signals = np.array(signals)
        fused, weights = self.kernel.fit(signals)
        
        outliers = [i for i, w in enumerate(weights) if w < 0.1]
        suspicious = [results[i].precinct_id for i in outliers]
        
        if suspicious:
            self.anomalies.append({'timestamp': datetime.now().isoformat(), 'suspicious_precincts': suspicious, 'weights': [float(weights[i]) for i in outliers]})
        
        self.verifications_performed += 1
        
        return {
            'verified_turnout_rate': float(fused[0]),
            'candidate_a_pct': float(fused[1] * 100),
            'candidate_b_pct': float(fused[2] * 100),
            'candidate_c_pct': float(fused[3] * 100),
            'suspicious_precincts': suspicious,
            'integrity_score': float(np.mean(weights)),
            'total_precincts': len(results),
            'anomalous_precincts': len(suspicious),
            'precinct_weights': {results[i].precinct_id: float(weights[i]) for i in range(len(results))}
        }
    
    def get_audit_report(self) -> Dict:
        return {'verifications': self.verifications_performed, 'total_anomalies': len(self.anomalies), 'anomaly_rate': len(self.anomalies) / max(1, self.verifications_performed), 'royalty': (self.verifications_performed * 25) / 10000, 'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'}
    
    def export_log(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump({'kernel': 'kl-017-lexvote', 'audit': self.get_audit_report(), 'anomalies': self.anomalies}, f, indent=2)


def main():
    kernel = LexVoteKernel()
    
    print("="*60)
    print("KL-017-LEXVOTE: Election Integrity Verification")
    print("="*60)
    
    results = [PrecinctResult(f"P-{i:03d}", 1000, 750 + np.random.randint(-50, 50), 400 + np.random.randint(-30, 30), 300 + np.random.randint(-30, 30), 50 + np.random.randint(-10, 10), datetime.now().timestamp()) for i in range(8)]
    
    results.append(PrecinctResult("P-008", 1000, 990, 980, 5, 5, datetime.now().timestamp()))
    results.append(PrecinctResult("P-009", 1000, 200, 10, 180, 10, datetime.now().timestamp()))
    
    result = kernel.verify_results(results)
    
    print(f"\nVerified Results:")
    print(f"  Turnout Rate: {result['verified_turnout_rate']:.1%}")
    print(f"  Candidate A: {result['candidate_a_pct']:.1f}%")
    print(f"  Candidate B: {result['candidate_b_pct']:.1f}%")
    print(f"  Candidate C: {result['candidate_c_pct']:.1f}%")
    print(f"\nIntegrity Metrics:")
    print(f"  Integrity Score: {result['integrity_score']:.2f}/1.00")
    print(f"  Total Precincts: {result['total_precincts']}")
    print(f"  Anomalous: {result['anomalous_precincts']}")
    
    if result['suspicious_precincts']:
        print(f"\n⚠️  ANOMALIES DETECTED")
        print(f"  Suspicious Precincts: {result['suspicious_precincts']}")
        print(f"\n  Precinct Weights (lower = more suspicious):")
        for pid in result['suspicious_precincts']:
            print(f"    {pid}: {result['precinct_weights'][pid]:.3f}")
    
    audit = kernel.get_audit_report()
    print(f"\n{'='*60}")
    print("AUDIT REPORT")
    print("="*60)
    print(f"Verifications: {audit['verifications']}")
    print(f"Anomalies Detected: {audit['total_anomalies']}")
    print(f"Anomaly Rate: {audit['anomaly_rate']:.1%}")
    print(f"Royalty: ${audit['royalty']:.2f}")
    
    kernel.export_log('kl-017-lexvote-log.json')
    print(f"\nLog exported to: kl-017-lexvote-log.json")


if __name__ == "__main__":
    main()
