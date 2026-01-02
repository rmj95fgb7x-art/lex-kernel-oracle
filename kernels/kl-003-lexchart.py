"""
KL-003-LEXCHART: Pharmaceutical Prior Authorization Kernel
Lex Liberatum Kernels v1.1

Domain: Healthcare / Pharmacy Benefits Management
Use Case: Multi-payer prior authorization decision fusion

Features:
- Cross-institutional PA decisions
- Fraud detection (gaming metrics)
- Real-time adjudication
- HIPAA-compliant logging

Patent: PCT Pending
Royalty: 25bp → 0x44f8...C689
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.adaptive_spectral_kernel import AdaptiveSpectralKernel
from src.utils import compute_all_metrics, detect_outliers


@dataclass
class PriorAuthRequest:
    """Prior authorization request."""
    patient_id: str  # Hashed for HIPAA
    drug_ndc: str
    prescriber_npi: str
    diagnosis_code: str
    pharmacy_ncpdp: str
    quantity: int
    days_supply: int
    estimated_cost: float
    urgency: str  # "routine", "urgent", "emergency"


@dataclass
class PayerDecision:
    """Individual payer's PA decision."""
    payer_id: str
    approved: bool
    confidence: float  # 0-1
    criteria_met: List[str]
    criteria_failed: List[str]
    processing_time_ms: float


class LexChartKernel:
    """
    KL-003-LEXCHART: Multi-payer prior authorization fusion.
    
    Aggregates PA decisions from multiple payers/PBMs to detect:
    - Gaming (payer artificially denying to save costs)
    - Fraud (inappropriate approvals)
    - Clinical consensus
    
    Parameters
    ----------
    alpha : float, default=1.2
        Sensitivity (lower = more aggressive fraud detection)
    min_payers : int, default=3
        Minimum payers for consensus
    approval_threshold : float, default=0.6
        Threshold for final approval decision
    """
    
    def __init__(
        self,
        alpha: float = 1.2,
        min_payers: int = 3,
        approval_threshold: float = 0.6
    ):
        self.kernel = AdaptiveSpectralKernel(alpha=alpha)
        self.min_payers = min_payers
        self.approval_threshold = approval_threshold
        
        self.decisions_processed = 0
        self.royalty_volume = 0
        self.fraud_alerts = []
    
    def process_pa_request(
        self,
        request: PriorAuthRequest,
        payer_decisions: List[PayerDecision]
    ) -> Dict:
        """
        Process prior authorization with multi-payer fusion.
        
        Returns
        -------
        result : dict
            - final_decision: "approved" | "denied" | "review_required"
            - confidence: 0-1
            - payer_weights: Reliability scores
            - fraud_detected: Boolean
            - reasoning: Explanation
        """
        if len(payer_decisions) < self.min_payers:
            return {
                'final_decision': 'review_required',
                'confidence': 0.0,
                'reasoning': f'Insufficient payers ({len(payer_decisions)} < {self.min_payers})'
            }
        
        # Convert decisions to signals
        signals = self._decisions_to_signals(payer_decisions)
        
        # Fuse with kernel
        fused_signal, weights = self.kernel.fit(signals)
        
        # Extract approval probability
        approval_prob = fused_signal[0]  # First element is approval score
        
        # Detect outliers (gaming payers)
        outliers = detect_outliers(weights, threshold=0.1)
        gaming_payers = [payer_decisions[i].payer_id for i in outliers]
        
        # Final decision
        if approval_prob >= self.approval_threshold:
            final_decision = 'approved'
        elif approval_prob < 0.4:
            final_decision = 'denied'
        else:
            final_decision = 'review_required'
        
        # Fraud detection
        fraud_detected = len(gaming_payers) > len(payer_decisions) * 0.3
        
        if fraud_detected:
            self.fraud_alerts.append({
                'request_id': request.patient_id,
                'gaming_payers': gaming_payers,
                'timestamp': datetime.now().isoformat()
            })
        
        # Increment counters
        self.decisions_processed += 1
        self.royalty_volume += len(payer_decisions)
        
        return {
            'final_decision': final_decision,
            'confidence': float(np.max(weights)),
            'approval_probability': float(approval_prob),
            'payer_weights': {
                payer_decisions[i].payer_id: float(weights[i])
                for i in range(len(payer_decisions))
            },
            'gaming_payers': gaming_payers,
            'fraud_detected': fraud_detected,
            'reasoning': self._generate_reasoning(
                final_decision, approval_prob, gaming_payers
            )
        }
    
    def _decisions_to_signals(self, decisions: List[PayerDecision]) -> np.ndarray:
        """Convert payer decisions to signal format."""
        signals = []
        for dec in decisions:
            signal = np.array([
                1.0 if dec.approved else 0.0,
                dec.confidence,
                len(dec.criteria_met) / 10.0,  # Normalized
                dec.processing_time_ms / 1000.0  # Convert to seconds
            ])
            signals.append(signal)
        return np.array(signals)
    
    def _generate_reasoning(
        self,
        decision: str,
        prob: float,
        gaming: List[str]
    ) -> str:
        """Generate human-readable explanation."""
        if decision == 'approved':
            reason = f"Approved with {prob:.1%} consensus confidence."
        elif decision == 'denied':
            reason = f"Denied with {1-prob:.1%} consensus to deny."
        else:
            reason = f"Borderline case ({prob:.1%}), requires clinical review."
        
        if gaming:
            reason += f" Warning: {len(gaming)} payer(s) showed anomalous patterns."
        
        return reason
    
    def get_royalty_info(self) -> Dict:
        """Royalty calculation."""
        return {
            'decisions_processed': self.decisions_processed,
            'payer_reviews': self.royalty_volume,
            'royalty_amount': (self.royalty_volume * 25) / 10000,
            'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'
        }


def main():
    """Example usage."""
    kernel = LexChartKernel()
    
    request = PriorAuthRequest(
        patient_id="HASH_12345",
        drug_ndc="12345-678-90",
        prescriber_npi="1234567890",
        diagnosis_code="E11.9",
        pharmacy_ncpdp="1234567",
        quantity=30,
        days_supply=30,
        estimated_cost=1250.00,
        urgency="routine"
    )
    
    # 5 payers review
    decisions = [
        PayerDecision("BCBS", True, 0.95, ["clinical", "formulary"], [], 120),
        PayerDecision("Aetna", True, 0.90, ["clinical", "formulary"], [], 150),
        PayerDecision("UHC", True, 0.92, ["clinical"], ["cost"], 110),
        PayerDecision("Cigna", False, 0.60, [], ["cost", "alternative"], 200),  # Outlier
        PayerDecision("Humana", True, 0.88, ["clinical"], [], 130),
    ]
    
    result = kernel.process_pa_request(request, decisions)
    
    print("KL-003-LEXCHART: Prior Authorization Fusion")
    print(f"Decision: {result['final_decision'].upper()}")
    print(f"Confidence: {result['confidence']:.1%}")
    print(f"Reasoning: {result['reasoning']}")
    print(f"\nPayer Weights:")
    for payer, weight in result['payer_weights'].items():
        print(f"  {payer}: {weight:.3f}")


if __name__ == "__main__":
    main()
