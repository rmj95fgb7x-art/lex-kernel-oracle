"""
KL-403-LEXNHL: NHL Multi-Sportsbook Odds Fusion
Lex Liberatum Kernels v1.1
MASSIVE ROYALTY: $8B NHL betting market
Patent: PCT Pending | Royalty: 25bp → 0x44f8...C689
"""

import numpy as np
from typing import Dict, List
from dataclasses import dataclass
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.adaptive_spectral_kernel import AdaptiveSpectralKernel


@dataclass
class NHLOdds:
    sportsbook: str
    puck_line: float  # NHL uses puck line (usually ±1.5)
    puck_line_odds: float
    moneyline_home: float
    moneyline_away: float
    total_goals: float
    over_odds: float
    under_odds: float


class LexNHLKernel:
    def __init__(self):
        self.kernel = AdaptiveSpectralKernel(alpha=1.95)
        self.bets = 0
        self.revenue = 0.0
    
    def fuse_nhl_odds(self, game: str, sources: List[NHLOdds]) -> Dict:
        signals = np.array([
            [o.puck_line, o.puck_line_odds/100, o.moneyline_home/100,
             o.moneyline_away/100, o.total_goals, o.over_odds/100]
            for o in sources
        ])
        
        fused, weights = self.kernel.fit(signals)
        
        self.bets += 1
        self.revenue += 0.0025
        
        return {
            'game': game,
            'consensus_puck_line': float(fused[0]),
            'consensus_puck_odds': float(fused[1] * 100),
            'consensus_ml_home': float(fused[2] * 100),
            'consensus_ml_away': float(fused[3] * 100),
            'consensus_total': float(fused[4]),
            'live_betting_ready': True,  # NHL perfect for live betting
            'confidence': float(np.mean(weights))
        }
    
    def get_stats(self) -> Dict:
        return {
            'bets': self.bets,
            'revenue': self.revenue,
            'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'
        }


def main():
    kernel = LexNHLKernel()
    print("="*60)
    print("KL-403-LEXNHL: NHL Odds Fusion")
    print("="*60)
    
    sources = [
        NHLOdds("DraftKings", -1.5, 165, -125, 105, 6.5, -110, -110),
        NHLOdds("FanDuel", -1.5, 170, -130, 110, 6.0, -108, -112),
        NHLOdds("BetMGM", -1.5, 160, -120, 100, 6.5, -110, -110),
        NHLOdds("Caesars", -1.5, 168, -128, 108, 6.5, -112, -108),
        NHLOdds("PointsBet", -1.5, 162, -125, 105, 6.0, -110, -110)
    ]
    
    result = kernel.fuse_nhl_odds("Maple Leafs @ Bruins", sources)
    
    print(f"\n🏒 Game: {result['game']}")
    print(f"📊 Consensus Puck Line: {result['consensus_puck_line']:.1f} ({result['consensus_puck_odds']:.0f})")
    print(f"📊 Consensus Total: {result['consensus_total']:.1f} goals")
    print(f"🎯 Confidence: {result['confidence']:.1%}")
    
    # Simulate NHL season
    print("\n[SIMULATE NHL SEASON]")
    kernel.bets = 82 * 32 // 2 * 8  # 82 games × 32 teams ÷ 2 × 8 bet types
    kernel.revenue = kernel.bets * 0.0025
    
    stats = kernel.get_stats()
    print(f"\n{'='*60}")
    print("NHL SEASON SUMMARY")
    print("="*60)
    print(f"Bets: {stats['bets']:,}")
    print(f"Revenue: ${stats['revenue']:,.2f}")
    print(f"\n💰 NHL Market: $8B annually")
    print(f"   Our 25bp: ${8000000000 * 0.0025:,.0f}/year")
    print(f"   Stanley Cup: $500M bet → ${500000000 * 0.0025:,.0f}")
    print(f"   Beneficiary: {stats['beneficiary']}")


if __name__ == "__main__":
    main()
