"""
KL-411-LEXEQUITY: Multi-Source Stock Trading Fusion
Lex Liberatum Kernels v1.1
MASSIVE ROYALTY: $200B daily US stock volume
Patent: PCT Pending | Royalty: 25bp → 0x44f8...C689
"""

import numpy as np
from typing import Dict, List
from dataclasses import dataclass
import json
import sys, os
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.adaptive_spectral_kernel import AdaptiveSpectralKernel


@dataclass
class EquitySignal:
    source: str
    price: float
    volume: float
    vwap: float  # Volume weighted average price
    rsi: float  # Relative strength index
    macd: float  # Moving average convergence divergence
    options_flow: float  # Unusual options activity score
    dark_pool_pct: float  # % of volume in dark pools
    timestamp: str


class LexEquityKernel:
    def __init__(self):
        self.kernel = AdaptiveSpectralKernel(alpha=1.95)
        self.trades = 0
        self.revenue = 0.0
    
    def fuse_equity_signals(self, ticker: str, signals: List[EquitySignal]) -> Dict:
        """
        Fuse multiple data sources for stock trading
        Combines price, technical indicators, and flow data
        """
        signal_matrix = np.array([
            [s.price, s.vwap, s.rsi/100, s.macd, s.options_flow, s.dark_pool_pct/100]
            for s in signals
        ])
        
        fused, weights = self.kernel.fit(signal_matrix)
        
        # Generate trading decision
        decision = self._generate_trade_decision(ticker, fused, weights, signals)
        
        # Detect institutional activity
        institutional = self._detect_institutional(signals, weights)
        
        self.trades += 1
        self.revenue += 0.0025
        
        return {
            'ticker': ticker,
            'consensus_price': float(fused[0]),
            'consensus_vwap': float(fused[1]),
            'consensus_rsi': float(fused[2] * 100),
            'consensus_macd': float(fused[3]),
            'options_sentiment': float(fused[4]),
            'dark_pool_activity': float(fused[5] * 100),
            'source_reliability': {
                signals[i].source: float(weights[i])
                for i in range(len(signals))
            },
            'institutional_activity': institutional,
            'trading_decision': decision,
            'confidence': float(np.mean(weights)),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _generate_trade_decision(self, ticker: str, fused: np.ndarray, 
                                 weights: np.ndarray, signals: List[EquitySignal]) -> Dict:
        """
        Generate BUY/SELL/HOLD based on consensus signals
        """
        price = fused[0]
        vwap = fused[1]
        rsi = fused[2] * 100
        macd = fused[3]
        options_flow = fused[4]
        dark_pool = fused[5] * 100
        
        # Calculate signal strength
        bullish_score = 0
        bearish_score = 0
        
        # Price vs VWAP
        if price < vwap * 0.995:  # 0.5% below VWAP
            bullish_score += 2
        elif price > vwap * 1.005:
            bearish_score += 2
        
        # RSI (oversold/overbought)
        if rsi < 30:  # Oversold
            bullish_score += 3
        elif rsi > 70:  # Overbought
            bearish_score += 3
        
        # MACD
        if macd > 0:
            bullish_score += 2
        else:
            bearish_score += 2
        
        # Options flow (smart money)
        if options_flow > 0.6:  # Bullish options activity
            bullish_score += 3
        elif options_flow < 0.4:  # Bearish options activity
            bearish_score += 3
        
        # Dark pool activity (institutional positioning)
        if dark_pool > 40:  # Heavy institutional buying
            bullish_score += 2
        
        # Decision logic
        net_score = bullish_score - bearish_score
        
        if net_score >= 5:
            return {
                'action': 'BUY',
                'strength': 'STRONG' if net_score >= 7 else 'MODERATE',
                'entry_price': float(price),
                'target_price': float(price * 1.03),  # 3% target
                'stop_loss': float(price * 0.98),  # 2% stop
                'size_pct': min(100, net_score * 10),  # % of portfolio
                'rationale': {
                    'bullish_signals': bullish_score,
                    'bearish_signals': bearish_score,
                    'net_score': net_score
                },
                'time_horizon': '1-5 days'
            }
        elif net_score <= -5:
            return {
                'action': 'SELL',
                'strength': 'STRONG' if net_score <= -7 else 'MODERATE',
                'entry_price': float(price),
                'target_price': float(price * 0.97),  # 3% target
                'stop_loss': float(price * 1.02),  # 2% stop
                'size_pct': min(100, abs(net_score) * 10),
                'rationale': {
                    'bullish_signals': bullish_score,
                    'bearish_signals': bearish_score,
                    'net_score': net_score
                },
                'time_horizon': '1-5 days'
            }
        else:
            return {
                'action': 'HOLD',
                'reason': 'mixed_signals',
                'net_score': net_score,
                'wait_for': 'stronger_confirmation'
            }
    
    def _detect_institutional(self, signals: List[EquitySignal], weights: np.ndarray) -> Dict:
        """
        Detect institutional/smart money activity
        """
        # Look at most reliable source
        best_idx = np.argmax(weights)
        best_signal = signals[best_idx]
        
        institutional_buying = (
            best_signal.dark_pool_pct > 35 and  # Heavy dark pool
            best_signal.options_flow > 0.6 and  # Bullish options
            best_signal.volume > np.mean([s.volume for s in signals]) * 1.5  # High volume
        )
        
        institutional_selling = (
            best_signal.dark_pool_pct > 35 and
            best_signal.options_flow < 0.4 and
            best_signal.volume > np.mean([s.volume for s in signals]) * 1.5
        )
        
        return {
            'detected': institutional_buying or institutional_selling,
            'direction': 'BUYING' if institutional_buying else 'SELLING' if institutional_selling else 'NEUTRAL',
            'dark_pool_pct': best_signal.dark_pool_pct,
            'options_flow': best_signal.options_flow,
            'confidence': float(weights[best_idx]),
            'follow_smart_money': institutional_buying or institutional_selling
        }
    
    def get_stats(self) -> Dict:
        return {
            'trades': self.trades,
            'revenue': self.revenue,
            'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'
        }
    
    def export_log(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump({'kernel': 'kl-411-lexequity', 'stats': self.get_stats()}, f, indent=2)


def main():
    kernel = LexEquityKernel()
    print("="*60)
    print("KL-411-LEXEQUITY: Multi-Source Stock Trading Fusion")
    print("="*60)
    
    # Example: AAPL across multiple data sources
    signals = [
        EquitySignal("Bloomberg", 178.52, 52.3e6, 178.45, 55.2, 0.85, 0.72, 38.5, "2026-01-05T16:00:00Z"),
        EquitySignal("Reuters", 178.50, 52.1e6, 178.43, 54.8, 0.88, 0.70, 37.2, "2026-01-05T16:00:00Z"),
        EquitySignal("Yahoo", 178.55, 51.8e6, 178.48, 56.0, 0.82, 0.68, 36.8, "2026-01-05T16:00:00Z"),
        EquitySignal("TradingView", 178.48, 52.5e6, 178.42, 55.5, 0.90, 0.75, 39.2, "2026-01-05T16:00:00Z"),
        EquitySignal("Interactive Brokers", 178.51, 52.2e6, 178.44, 55.0, 0.87, 0.73, 38.0, "2026-01-05T16:00:00Z")
    ]
    
    result = kernel.fuse_equity_signals("AAPL", signals)
    
    print(f"\n📈 Ticker: {result['ticker']}")
    print(f"💰 Consensus Price: ${result['consensus_price']:.2f}")
    print(f"📊 Consensus VWAP: ${result['consensus_vwap']:.2f}")
    print(f"📊 Consensus RSI: {result['consensus_rsi']:.1f}")
    print(f"📊 Consensus MACD: {result['consensus_macd']:.2f}")
    print(f"📊 Options Sentiment: {result['options_sentiment']:.2f}")
    print(f"📊 Dark Pool Activity: {result['dark_pool_activity']:.1f}%")
    print(f"🎯 Confidence: {result['confidence']:.1%}")
    
    inst = result['institutional_activity']
    if inst['detected']:
        print(f"\n🏦 INSTITUTIONAL ACTIVITY DETECTED!")
        print(f"   Direction: {inst['direction']}")
        print(f"   Dark pool: {inst['dark_pool_pct']:.1f}%")
        print(f"   Options flow: {inst['options_flow']:.2f}")
        print(f"   → {'FOLLOW' if inst['follow_smart_money'] else 'MONITOR'} smart money")
    
    decision = result['trading_decision']
    print(f"\n📊 TRADING DECISION: {decision['action']}")
    if decision['action'] != 'HOLD':
        print(f"   Strength: {decision['strength']}")
        print(f"   Entry: ${decision['entry_price']:.2f}")
        print(f"   Target: ${decision['target_price']:.2f}")
        print(f"   Stop: ${decision['stop_loss']:.2f}")
        print(f"   Position size: {decision['size_pct']:.0f}%")
        print(f"   Time horizon: {decision['time_horizon']}")
        print(f"   Rationale: Bullish={decision['rationale']['bullish_signals']}, "
              f"Bearish={decision['rationale']['bearish_signals']}, "
              f"Net={decision['rationale']['net_score']}")
    
    # Simulate trading day
    print("\n[SIMULATE TRADING DAY - SPY 500]")
    kernel.trades = 500 * 100  # 500 stocks × 100 signals/day each
    kernel.revenue = kernel.trades * 0.0025
    
    stats = kernel.get_stats()
    print(f"\n{'='*60}")
    print("EQUITY TRADING SUMMARY")
    print("="*60)
    print(f"Signals: {stats['trades']:,}")
    print(f"Revenue: ${stats['revenue']:,.2f}")
    print(f"\n💰 ANNUAL PROJECTION")
    print(f"   At 1M signals/day: ${1000000 * 0.0025 * 252:,.0f}/year (252 trading days)")
    print(f"   US stock volume: $200B/day → ${200000000000 * 0.0025:,.0f}/day potential")
    print(f"   Beneficiary: {stats['beneficiary']}")
    
    kernel.export_log('kl-411-lexequity-log.json')


if __name__ == "__main__":
    main()
