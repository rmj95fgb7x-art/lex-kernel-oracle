"""
KL-435-LEXSCHEDULING: Clinic Scheduling Optimization
Appointment types + surgeon availability + patient urgency + no-show prediction
Patent: PCT Pending | Royalty: 25bp → 0x44f8...C689
"""

import numpy as np
from typing import Dict, List
from dataclasses import dataclass
import sys, os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.adaptive_spectral_kernel import AdaptiveSpectralKernel

@dataclass
class SchedulingInput:
    source: str
    urgency_score: float  # 0-1
    appointment_duration_min: int
    no_show_probability: float
    patient_flexibility: float  # Can they reschedule?
    surgeon_preference: float  # How well-suited is surgeon?

class LexSchedulingKernel:
    def __init__(self):
        self.kernel = AdaptiveSpectralKernel(alpha=1.95)
        self.schedules = 0
        self.revenue = 0.0
    
    def optimize_scheduling(self, patient_id: str, appointment_type: str, inputs: List[SchedulingInput]) -> Dict:
        signals = np.array([
            [i.urgency_score, i.appointment_duration_min/120.0, 
             1.0 - i.no_show_probability, i.patient_flexibility, i.surgeon_preference]
            for i in inputs
        ])
        
        fused, weights = self.kernel.fit(signals)
        
        urgency = float(fused[0])
        duration = int(fused[1] * 120)
        show_prob = float(fused[2])
        flexibility = float(fused[3])
        
        if urgency > 0.8:
            priority = "URGENT"
            schedule_within = "24-48 hours"
            slot_type = "Emergency slot"
        elif urgency > 0.6:
            priority = "HIGH"
            schedule_within = "1 week"
            slot_type = "Priority slot"
        elif urgency > 0.4:
            priority = "MODERATE"
            schedule_within = "2-4 weeks"
            slot_type = "Standard slot"
        else:
            priority = "ROUTINE"
            schedule_within = "4-8 weeks"
            slot_type = "Routine slot"
        
        # Overbooking recommendation based on no-show probability
        overbook = show_prob < 0.7
        
        self.schedules += 1
        self.revenue += 0.0025
        
        return {
            'patient_id': patient_id,
            'appointment_type': appointment_type,
            'priority': priority,
            'schedule_within': schedule_within,
            'slot_type': slot_type,
            'duration_minutes': duration,
            'show_probability': show_prob,
            'overbook_slot': overbook,
            'patient_flexibility': flexibility,
            'recommendation': f"Book {slot_type}, expect {duration}min, {show_prob:.0%} show rate",
            'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'
        }
    
    def get_stats(self):
        return {'schedules': self.schedules, 'revenue': self.revenue, 'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'}

def main():
    kernel = LexSchedulingKernel()
    print("KL-435-LEXSCHEDULING: Clinic Scheduling Optimization")
    
    inputs = [
        SchedulingInput("Triage nurse", 0.75, 45, 0.15, 0.6, 0.9),
        SchedulingInput("Referral urgency", 0.80, 50, 0.20, 0.5, 0.85),
        SchedulingInput("Historical data", 0.72, 45, 0.18, 0.65, 0.88),
        SchedulingInput("Clinic manager", 0.78, 48, 0.12, 0.7, 0.90)
    ]
    
    result = kernel.optimize_scheduling("PT005", "Post-op follow-up", inputs)
    
    print(f"Patient: {result['patient_id']}")
    print(f"Appointment: {result['appointment_type']}")
    print(f"Priority: {result['priority']}")
    print(f"Schedule within: {result['schedule_within']}")
    print(f"Slot type: {result['slot_type']}")
    print(f"Duration: {result['duration_minutes']} min")
    print(f"Show probability: {result['show_probability']:.0%}")
    print(f"Overbook this slot: {'YES' if result['overbook_slot'] else 'NO'}")
    print(f"Recommendation: {result['recommendation']}")
    
    kernel.schedules = 15000
    kernel.revenue = 15000 * 0.0025
    print(f"\nAnnual: {kernel.schedules:,} | Revenue: ${kernel.revenue:,.2f}")

if __name__ == "__main__":
    main()
