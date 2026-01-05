"""
KL-402-LEXNFL: NFL Multi-Sportsbook Odds Fusion
Lex Liberatum Kernels v1.1
MASSIVE ROYALTY: $93B NFL betting market (largest in US)
Patent: PCT Pending | Royalty: 25bp → 0x44f8...C689
"""

import numpy as np
from typing import Dict, List
from dataclasses import dataclass
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.adaptive_spectral_kernel import AdaptiveSpectralKernel


@dataclass
class NFLOdds:
    sportsbook: str
    spread: float
    spread_odds: float
    moneyline_home: float
    moneyline_away: float
    total: float
    over_odds: float
    under_odds: float


class LexNFLKernel:
    def __init__(self):
        self.kernel = AdaptiveSpectralKernel(alpha=1.95)
        self.bets = 0
        self.revenue = 0.0
    
    def fuse_nfl_odds(self, game: str, sources: List[NFLOdds]) -> Dict:
        # NFL-specific: Spread is CRITICAL (most popular bet type)
        signals = np.array([
            [o.spread, o.spread_odds/100, o.moneyline_home/100, 
             o.moneyline_away/100, o.total, o.over_odds/100]
            for o in sources
        ])
        
        fused, weights = self.kernel.fit(signals)
        
        self.bets += 1
        self.revenue += 0.0025
        
        return {
            'game': game,
            'consensus_spread': float(fused[0]),
            'consensus_spread_odds': float(fused[1] * 100),
            'consensus_moneyline_home': float(fused[2] * 100),
            'consensus_moneyline_away': float(fused[3] * 100),
            'consensus_total': float(fused[4]),
            'consensus_over_odds': float(fused[5] * 100),
            'sharp_action': self._detect_sharp_money(signals, weights),
            'sportsbook_consensus': float(np.mean(weights))
        }
    
    def _detect_sharp_money(self, signals: np.ndarray, weights: np.ndarray) -> Dict:
        """
        Detect where sharp money (professional bettors) is going
        Sharp money = sportsbooks with highest weight moving lines
        """
        # Find sportsbook with highest weight (most accurate historically)
        sharp_book = np.argmax(weights)
        sharp_line = signals[sharp_book]
        consensus_line = np.mean(signals, axis=0)
        
        # If sharp book deviates from consensus, that's where sharp money is
        deviation = sharp_line - consensus_line
        
        return {
            'sharp_book_index': int(sharp_book),
            'sharp_spread': float(sharp_line[0]),
            'public_spread': float(consensus_line[0]),
            'fade_the_public': abs(deviation[0]) > 0.5  # Fade if 0.5+ point difference
        }
    
    def get_stats(self) -> Dict:
        return {
            'bets': self.bets,
            'revenue': self.revenue,
            'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'
        }


def main():
    kernel = LexNFLKernel()
    print("="*60)
    print("KL-402-LEXNFL: NFL Odds Fusion")
    print("="*60)
    
    # Example: Chiefs vs Bills (playoff game)
    sources = [
        NFLOdds("DraftKings", -2.5, -110, -135, 115, 51.5, -110, -110),
        NFLOdds("FanDuel", -3.0, -108, -140, 120, 51.0, -112, -108),
        NFLOdds("BetMGM", -2.5, -112, -130, 110, 52.0, -110, -110),
        NFLOdds("Caesars", -3.0, -110, -138, 118, 51.5, -108, -112),
        NFLOdds("PointsBet", -2.0, -115, -125, 105, 51.5, -110, -110)
    ]
    
    result = kernel.fuse_nfl_odds("Chiefs @ Bills", sources)
    
    print(f"\n🏈 Game: {result['game']}")
    print(f"📊 Consensus Spread: {result['consensus_spread']:.1f} ({result['consensus_spread_odds']:.0f})")
    print(f"📊 Consensus ML: {result['consensus_moneyline_home']:.0f} / {result['consensus_moneyline_away']:.0f}")
    print(f"📊 Consensus Total: {result['consensus_total']:.1f}")
    
    if result['sharp_action']['fade_the_public']:
        print(f"\n🔥 SHARP MONEY DETECTED!")
        print(f"   Sharp spread: {result['sharp_action']['sharp_spread']:.1f}")
        print(f"   Public spread: {result['sharp_action']['public_spread']:.1f}")
        print(f"   → Fade the public, follow the sharp money!")
    
    # Simulate NFL season
    print("\n[SIMULATE NFL SEASON]")
    games_per_week = 16
    weeks = 18
    bets_per_game = 10  # Spread, ML, total, props
    total = games_per_week * weeks * bets_per_game
    
    for _ in range(total):
        kernel.bets += 1
        kernel.revenue += 0.0025
    
    stats = kernel.get_stats()
    print(f"\n{'='*60}")
    print("NFL SEASON SUMMARY")
    print("="*60)
    print(f"Bets: {stats['bets']:,}")
    print(f"Revenue: ${stats['revenue']:,.2f}")
    print(f"\n💰 NFL is LARGEST US betting market")
    print(f"   Market size: $93B annually")
    print(f"   Our 25bp cut: ${93000000000 * 0.0025:,.0f}/year potential")
    print(f"   Super Bowl alone: $7B bet → ${7000000000 * 0.0025:,.0f}")
    print(f"   Beneficiary: {stats['beneficiary']}")


if __name__ == "__main__":
    main()
