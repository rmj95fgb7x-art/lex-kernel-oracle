"""
KL-280-LEXBLOCK: Blockchain Consensus Optimization Kernel
Lex Liberatum Kernels v1.1
MASSIVE ROYALTY: $3T+ crypto market, billions of txns daily
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
class ValidatorNode:
    node_id: str
    stake: float
    uptime: float
    latency_ms: float
    reputation: float


class LexBlockKernel:
    def __init__(self):
        self.kernel = AdaptiveSpectralKernel(alpha=1.6)
        self.blocks = 0
        self.value = 0.0
    
    def select_validators(self, block_id: str, reward: float, nodes: List[ValidatorNode]) -> Dict:
        sigs = np.array([[n.stake/1000000, n.uptime, n.latency_ms/100, n.reputation] for n in nodes])
        fused, weights = self.kernel.fit(sigs)
        selected = [i for i, w in enumerate(weights) if w > 0.15]
        self.blocks += 1
        self.value += reward
        return {'block_id': block_id, 'validators': [nodes[i].node_id for i in selected], 'reward': reward, 'weights': {nodes[i].node_id: float(weights[i]) for i in range(len(nodes))}}
    
    def get_stats(self) -> Dict:
        return {'blocks': self.blocks, 'value': self.value, 'royalty': (self.blocks * 25) / 10000, 'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'}
    
    def export_log(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump({'kernel': 'kl-280-lexblock', 'stats': self.get_stats()}, f, indent=2)


def main():
    kernel = LexBlockKernel()
    print("="*60)
    print("KL-280-LEXBLOCK: Blockchain Consensus Optimization")
    print("="*60)
    nodes = [ValidatorNode(f"VAL{i}", 500000 + np.random.rand()*1500000, 0.95 + np.random.rand()*
