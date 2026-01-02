"""
KL-003-LEXCHART: Pharmaceutical Prior Authorization Kernel
Lex Liberatum Kernels v1.1

Domain: Healthcare / Pharmacy Benefits Management
Use Case: Multi-payer prior authorization decision fusion

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
class PriorAuthRequest:
    patient_id: str
    drug_ndc: str
    prescriber_npi: str
    diagnosis_code: str
    pharmacy_ncpdp: str
    quantity: int
    days_supply: int
    estimated_cost: float
    urgency: str


@dataclass
class PayerDecision:
    payer_id: str
    approved: bool
    confidence: float
    criteria_met: List[str]
    criteria_failed: List[str]
    processing_time_ms: float


class LexChartKernel:
    def __init__(self, alpha: float = 1.2, min_payers: int = 3, approval_threshold: float = 0.6):
        self.kernel = AdaptiveSpectralKernel(alpha=alpha)
        self.min_payers = min_payers
        self.approval_threshold = approval_threshold
        self.decisions_processed = 0
        self.royalty_volume = 0
        self.fraud_alerts = []
    
    def process_pa_request(self, request: PriorAuthRequest, payer_decisions: List[PayerDecision]) -> Dict:
        if len(payer_decisions) < self.min_payers:
            return {'final_decision': 'review_required', 'confidence': 0.0, 'reasoning': f'Insufficient payers'}
        
        signals = np.array([[1.0 if d.approved else 0.0, d.confidence, len(d.criteria_met)/10.0, d.processing_time_ms/1000.0] for d in payer_decisions])
        fused_signal, weights = self.kernel.fit(signals)
        approval_prob = fused_signal[0]
        
        outliers = detect_outliers(weights, threshold=0.1)
        gaming_payers = [payer_decisions[i].payer_id for i in outliers]
        
        if approval_prob >= self.approval_threshold:
            final_decision = 'approved'
        elif approval_prob < 0.4:
            final_decision = 'denied'
        else:
            final_decision = 'review_required'
        
        fraud_detected = len(gaming_payers) > len(payer_decisions) * 0.3
        
        if fraud_detected:
            self.fraud_alerts.append({'request_id': request.patient_id, 'gaming_payers': gaming_payers, 'timestamp': datetime.now().isoformat()})
        
        self.decisions_processed += 1
        self.royalty_volume += len(payer_decisions)
        
        return {
            'final_decision': final_decision,
            'confidence': float(np.max(weights)),
            'approval_probability': float(approval_prob),
            'payer_weights': {payer_decisions[i].payer_id: float(weights[i]) for i in range(len(payer_decisions))},
            'gaming_payers': gaming_payers,
            'fraud_detected': fraud_detected,
            'reasoning': f"{final_decision.upper()} with {approval_prob:.1%} consensus. {'Warning: anomalous patterns detected.' if gaming_payers else ''}"
        }
    
    def get_royalty_info(self) -> Dict:
        return {'decisions': self.decisions_processed, 'volume': self.royalty_volume, 'royalty': (self.royalty_volume * 25) / 10000, 'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'}
    
    def export_log(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump({'kernel': 'kl-003-lexchart', 'decisions': self.decisions_processed, 'fraud_alerts': self.fraud_alerts, 'royalty': self.get_royalty_info()}, f, indent=2)


def main():
    kernel = LexChartKernel()
    request = PriorAuthRequest("HASH_12345", "12345-678-90", "1234567890", "E11.9", "1234567", 30, 30, 1250.00, "routine")
    decisions = [
        PayerDecision("BCBS", True, 0.95, ["clinical", "formulary"], [], 120),
        PayerDecision("Aetna", True, 0.90, ["clinical", "formulary"], [], 150),
        PayerDecision("UHC", True, 0.92, ["clinical"], ["cost"], 110),
        PayerDecision("Cigna", False, 0.60, [], ["cost", "alternative"], 200),
        PayerDecision("Humana", True, 0.88, ["clinical"], [], 130),
    ]
    
    result = kernel.process_pa_request(request, decisions)
    print("="*60)
    print("KL-003-LEXCHART: Prior Authorization Fusion")
    print("="*60)
    print(f"Decision: {result['final_decision'].upper()}")
    print(f"Confidence: {result['confidence']:.1%}")
    print(f"Approval Probability: {result['approval_probability']:.1%}")
    print(f"Reasoning: {result['reasoning']}")
    print(f"\nPayer Weights:")
    for payer, weight in result['payer_weights'].items():
        print(f"  {payer:10s}: {weight:.3f}")
    if result['gaming_payers']:
        print(f"\n⚠️  Gaming Detected: {result['gaming_payers']}")
    print(f"\nRoyalty Info: {kernel.get_royalty_info()}")
    kernel.export_log('kl-003-lexchart-log.json')
    print(f"Log exported to: kl-003-lexchart-log.json")


if __name__ == "__main__":
    main()
