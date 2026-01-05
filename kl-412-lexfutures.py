"""
KL-412-LEXFUTURES: Futures Curve & Spread Trading Fusion
Lex Liberatum Kernels v1.1
MASSIVE ROYALTY: $30T annual futures volume
Patent: PCT Pending | Royalty: 25bp → 0x44f8...C689
"""

import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
import json
import sys, os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.adaptive_spectral_kernel import AdaptiveSpectralKernel


@dataclass
class FuturesContract:
    exchange: str
    contract_month: str  # e.g., "2026-03"
    price: float
    open_interest: float
    volume: float
    bid: float
    ask: float
    days_to_expiry: int


class LexFuturesKernel:
    def __init__(self):
        self.kernel = AdaptiveSpectralKernel(alpha=1.95)
        self.trades = 0
        self.revenue = 0.0
    
    def fuse_futures_curve(self, asset: str, contracts: List[FuturesContract]) -> Dict:
        """
        Fuse futures curve across exchanges
        Detect contango/backwardation opportunities
        """
        # Group by contract month
        curve_by_month = {}
        for contract in contracts:
            month = contract.contract_month
            if month not in curve_by_month:
                curve_by_month[month] = []
            curve_by_month[month].append(contract)
        
        # Fuse each month's prices across exchanges
        fused_curve = {}
        for month, month_contracts in curve_by_month.items():
            signals = np.array([
                [c.price, c.bid, c.ask, c.open_interest/1e6, c.volume/1e6]
                for c in month_contracts
            ])
            
            fused, weights = self.kernel.fit(signals)
            
            fused_curve[month] = {
                'consensus_price': float(fused[0]),
                'consensus_bid': float(fused[1]),
                'consensus_ask': float(fused[2]),
                'days_to​​​​​​​​​​​​​​​​
