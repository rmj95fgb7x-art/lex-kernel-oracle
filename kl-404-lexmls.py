"""
KL-404-LEXMLS: MLS Multi-Sportsbook Odds Fusion
Lex Liberatum Kernels v1.1
GROWING ROYALTY: $1B MLS betting (fastest growing US sport)
Patent: PCT Pending | Royalty: 25bp → 0x44f8...C689
"""

import numpy as np
from typing import Dict, List
from dataclasses import dataclass
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.adaptive_spectral_kernel import AdaptiveSpectralKernel


@dataclass
class MLSOdds:
    sportsbook: str
    three_way_home: float  # Soccer uses 3-way: Win/Draw/Win
    three_way_draw: float
    three_way_away: float
    total_goals: float
    over_odds: float
    under_odds: float


class LexMLSKernel:
    def __init__(self):
        self.kernel = AdaptiveSpectralKernel(alpha=1.95)
        self.bets = 0
        self.revenue = 0.0
    
    def fuse_mls_odds(self, game: str, sources: List[MLSOdds]) -> Dict:
        # Soccer 3-way betting is unique
        signals = np.array([
            [o.three_way_home/100, o.three_way_draw/100, o.three_way_away/100,
             o.total_goals, o.over_odds/100, o.under_odds/100]
            for o in sources
        ])
        
        fused, weights = self.kernel.fit(signals)
        
        self.bets += 1
        self.revenue += 0.0025
        
        return {
            'game': game,
            'consensus_home_win': float(fused[0] * 100),
            'consensus_draw': float(fused[1] * 100),
            'consensus_away_win': float(fused[2] * 100),
            'consensus_total': float(fused[3]),
            'implied_probabilities': self._calc_probabilities(fused),
            'confidence': float(np.mean(weights))
        }
    
    def _calc_probabilities(self, fused: np.ndarray) -> Dict:
        # Convert American odds to implied probabilities
        def american_to_prob(odds):
            if odds > 0:
                return 100 / (odds + 100)
            else:
                return abs(odds) / (abs(odds) + 100)
        
        home_prob = american_to_prob(fused[0] * 100)
        draw_prob = american_to_prob(fused[1] * 100)
        away_prob = american_to_prob(fused[2] * 100)
        
        # Normalize (should sum to 1.0)
        total = home_prob + draw_prob + away_prob
        
        return {
            'home_win': home_prob / total,
            'draw': draw_prob / total,
            'away_win': away_prob / total
        }
    
    def get_stats(self) -> Dict:
        return {
            'bets': self.bets,
            'revenue': self.revenue,
            'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'
        }


def main():
    kernel = LexMLSKernel()
    print("="*60)
    print("KL-404-LEXMLS: MLS Odds Fusion")
    print("="*60)
    
    sources = [
        MLSOdds("DraftKings", 150, 240, 180, 2.5, -110, -110),
        MLSOdds("FanDuel", 155, 250, 175, 2.5, -108, -112),
        MLSOdds("BetMGM", 145, 235, 185, 3.0, -110, -110),
        MLSOdds("Caesars", 152, 245, 178, 2.5, -112, -108),
        MLSOdds("PointsBet", 148, 238, 182, 2.5, -110, -110)
    ]
    
    result = kernel.fuse_mls_odds("LA Galaxy vs Seattle Sounders", sources)
    
    print(f"\n⚽ Game: {result['game']}")
    print(f"📊 Consensus Odds:")
    print(f"   Home Win: {result['consensus_home_win']:.0f} ({result['implied_probabilities']['home_win']:.1%})")
    print(f"   Draw: {result['consensus_draw']:.0f} ({result['implied_probabilities']['draw']:.1%})")
    print(f"   Away Win: {result['consensus_away_win']:.0f} ({result['implied_probabilities']['away_win']:.1%})")
    print(f"📊 Total: {result['consensus_total']:.1f} goals")
    
    # Simulate MLS season
    print("\n[SIMULATE MLS SEASON]")
    kernel.bets = 34 * 29 // 2 * 6  # 34 games × 29 teams ÷ 2 × 6 bet types
    kernel.revenue = kernel.bets * 0.0025
    
    stats = kernel.get_stats()
    print(f"\n{'='*60}")
    print("MLS SEASON SUMMARY")
    print("="*60)
    print(f"Bets: {stats['bets']:,}")
    print(f"Revenue: ${stats['revenue']:,.2f}")
    print(f"\n💰 MLS is FASTEST GROWING")
    print(f"   Current market: $1B/year")
    print(f"   Growth rate: 40%+ annually")
    print(f"   2030 projection: $5B → ${5000000000 * 0.0025:,.0f}/year")
    print(f"   Beneficiary: {stats['beneficiary']}")


if __name__ == "__main__":
    main()
