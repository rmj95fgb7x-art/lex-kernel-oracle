"""
KL-091-LEXTRADE: Stock Trade Execution Optimization Kernel
Lex Liberatum Kernels v1.1
HIGH ROYALTY POTENTIAL: Billions of trades daily, milliseconds = millions
Patent: PCT Pending | Royalty: 25bp → 0x44f8...C689
"""

import numpy as np
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime
import json
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.temporal_kernel import TemporalAdaptiveKernel


@dataclass
class TradeOrder:
    order_id: str
    symbol: str
    side: str
    quantity: int
    order_type: str
    limit_price: float
    timestamp: float


@dataclass
class VenueQuote:
    venue_id: str
    bid_price: float
    ask_price: float
    bid_size: int
    ask_size: int
    latency_ms: float
    fill_probability: float


class LexTradeKernel:
    def __init__(self):
        self.kernel = TemporalAdaptiveKernel(alpha=1.5, beta=0.88, lambda_jitter=0.5, drift_threshold=0.1)
        self.trades_executed = 0
        self.total_value = 0.0
        self.timestep = 0
    
    def route_order(self, order: TradeOrder, venues: List[VenueQuote]) -> Dict:
        if order.side == "buy":
            signals = np.array([[v.ask_price, v.ask_size, v.latency_ms, v.fill_probability] for v in venues])
        else:
            signals = np.array([[v.bid_price, v.bid_size, v.latency_ms, v.fill_probability] for v in venues])
        fused, weights = self.kernel.update(signals)
        best_price = fused[0]
        avg_size = fused[1]
        avg_latency = fused[2]
        avg_fill_prob = fused[3]
        best_venue_idx = np.argmax(weights)
        best_venue = venues[best_venue_idx]
        exec_price = best_venue.ask_price if order.side == "buy" else best_venue.bid_price
        slippage = abs(exec_price - best_price) / best_price if best_price > 0 else 0
        trade_value = order.quantity * exec_price
        self.trades_executed += 1
        self.total_value += trade_value
        self.timestep += 1
        return {'order_id': order.order_id, 'symbol': order.symbol, 'side': order.side, 'quantity': order.quantity, 'execution_price': float(exec_price), 'best_venue': best_venue.venue_id, 'latency_ms': float(best_venue.latency_ms), 'slippage': float(slippage), 'fill_probability': float(best_venue.fill_probability), 'trade_value': float(trade_value), 'venue_weights': {venues[i].venue_id: float(weights[i]) for i in range(len(venues))}}
    
    def get_stats(self) -> Dict:
        return {'trades': self.trades_executed, 'total_value': self.total_value, 'avg_trade': self.total_value/max(1, self.trades_executed), 'royalty': (self.trades_executed * 25) / 10000, 'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'}
    
    def export_log(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump({'kernel': 'kl-091-lextrade', 'stats': self.get_stats()}, f, indent=2)


def main():
    kernel = LexTradeKernel()
    print("="*60)
    print("KL-091-LEXTRADE: Trade Execution Optimization")
    print("="*60)
    order = TradeOrder("ORD-001", "AAPL", "buy", 1000, "limit", 185.50, datetime.now().timestamp())
    venues = [VenueQuote("NYSE", 185.48, 185.52, 500, 800, 1.2, 0.95), VenueQuote("NASDAQ", 185.49, 185.51, 600, 1000, 0.8, 0.98), VenueQuote("BATS", 185.50, 185.53, 400, 700, 1.5, 0.92), VenueQuote("IEX", 185.47, 185.54, 300, 500, 2.0, 0.88)]
    result = kernel.route_order(order, venues)
    print(f"\nOrder: {result['order_id']}")
    print(f"Symbol: {result['symbol']}")
    print(f"Side: {result['side'].upper()}")
    print(f"Quantity: {result['quantity']:,}")
    print(f"Execution: ${result['execution_price']:.2f} @ {result['best_venue']}")
    print(f"Latency: {result['latency_ms']:.1f}ms")
    print(f"Slippage: {result['slippage']:.4%}")
    print(f"Value: ${result['trade_value']:,.2f}")
    print("\nVenue Weights:")
    for v, w in result['venue_weights'].items():
        print(f"  {v:10s}: {w:.3f}")
    print("\n[SIMULATE 1M TRADES]")
    for i in range(1000000):
        sym = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"][i%5]
        qty = np.random.randint(100, 5000)
        side = "buy" if np.random.rand() > 0.5 else "sell"
        price = 100 + np.random.rand()*200
        order = TradeOrder(f"ORD-{i}", sym, side, qty, "market", price, datetime.now().timestamp())
        venues = [VenueQuote(f"VENUE{j}", price - 0.02 + np.random.rand()*0.02, price + np.random.rand()*0.02, np.random.randint(500, 2000), np.random.randint(500, 2000), np.random.rand()*3, 0.85 + np.random.rand()*0.15) for j in range(4)]
        kernel.route_order(order, venues)
    stats = kernel.get_stats()
    print(f"\n{'='*60}")
    print("TRADE EXECUTION SUMMARY")
    print("="*60)
    print(f"Trades Executed: {stats['trades']:,}")
    print(f"Total Value: ${stats['total_value']:,.0f}")
    print(f"Avg Trade: ${stats['avg_trade']:,.2f}")
    print(f"\n💰 ROYALTY: ${stats['royalty']:,.2f}")
    print(f"   At 100M trades/day: ${(100000000 * 25)/10000:,.2f}/day = ${(100000000 * 25 * 250)/10000:,.2f}/year")
    print(f"   At 1B trades/day: ${(1000000000 * 25)/10000:,.2f}/day = ${(1000000000 * 25 * 250)/10000:,.2f}/year")
    print(f"   Global equity volume: 100B+ shares/day")
    print(f"   Beneficiary: {stats['beneficiary']}")
    kernel.export_log('kl-091-lextrade-log.json')


if __name__ == "__main__":
    main()
