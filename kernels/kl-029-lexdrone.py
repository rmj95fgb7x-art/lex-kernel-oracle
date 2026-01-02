"""
KL-029-LEXDRONE: Swarm Coordination Kernel
Lex Liberatum Kernels v1.1
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
class DroneState:
    drone_id: str
    position: np.ndarray
    velocity: np.ndarray
    battery_pct: float
    signal_strength: float
    timestamp: float


class LexDroneKernel:
    def __init__(self):
        self.kernel = TemporalAdaptiveKernel(alpha=1.4, beta=0.92, lambda_jitter=0.4, drift_threshold=0.08)
        self.failures = []
        self.timestep = 0
    
    def coordinate_swarm(self, drones: List[DroneState]) -> Dict:
        signals = np.array([[d.position[0], d.position[1], d.position[2], d.velocity[0], d.velocity[1], d.velocity[2], d.battery_pct, d.signal_strength] for d in drones])
        fused, weights = self.kernel.update(signals)
        consensus_pos = fused[0:3]
        consensus_vel = fused[3:6]
        avg_battery = fused[6]
        avg_signal = fused[7]
        failed = [d.drone_id for i, d in enumerate(drones) if weights[i] < 0.08]
        low_battery = [d.drone_id for d in drones if d.battery_pct < 20]
        if failed:
            self.failures.append({'timestamp': datetime.now().isoformat(), 'failed_drones': failed, 'count': len(failed)})
        self.timestep += 1
        return {'consensus_position': consensus_pos.tolist(), 'consensus_velocity': consensus_vel.tolist(), 'avg_battery': float(avg_battery), 'avg_signal': float(avg_signal), 'failed_drones': failed, 'low_battery_drones': low_battery, 'swarm_health': float(np.mean(weights)), 'active_drones': len(drones) - len(failed), 'timestep': self.timestep}
    
    def get_stats(self) -> Dict:
        total_failures = sum(len(f['failed_drones']) for f in self.failures)
        return {'timesteps': self.timestep, 'failure_events': len(self.failures), 'total_failures': total_failures, 'royalty': (self.timestep * 25) / 10000, 'beneficiary': '0x44f8219cBABad92E6bf245D8c767179629D8C689'}
    
    def export_log(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump({'kernel': 'kl-029-lexdrone', 'stats': self.get_stats(), 'failures': self.failures}, f, indent=2)


def main():
    kernel = LexDroneKernel()
    print("="*60)
    print("KL-029-LEXDRONE: Swarm Coordination")
    print("="*60)
    for t in range(5):
        drones = [DroneState(f"DRONE-{i}", np.array([100 + i*10 + np.random.rand()*5, 200 + np.random.rand()*5, 50 + np.random.rand()*2]), np.array([5 + np.random.rand(), 0, 0]), 80 - t*15 if i == 0 else 85 + np.random.rand()*10, 0.3 if i == 0 and t > 2 else 0.9 + np.random.rand()*0.1, datetime.now().timestamp()) for i in range(20)]
        result = kernel.coordinate_swarm(drones)
        print(f"\nTimestep {result['timestep']}:")
        print(f"  Consensus Position: [{result['consensus_position'][0]:.1f}, {result['consensus_position'][1]:.1f}, {result['consensus_position'][2]:.1f}]")
        print(f"  Active Drones: {result['active_drones']}/20")
        print(f"  Avg Battery: {result['avg_battery']:.1f}%")
        print(f"  Swarm Health: {result['swarm_health']:.2f}")
        if result['failed_drones']:
            print(f"  ⚠️  Failed: {result['failed_drones']}")
        if result['low_battery_drones']:
            print(f"  🔋 Low Battery: {result['low_battery_drones']}")
    stats = kernel.get_stats()
    print(f"\n{'='*60}")
    print("SWARM STATS")
    print("="*60)
    print(f"Timesteps: {stats['timesteps']}")
    print(f"Failure Events: {stats['failure_events']}")
    print(f"Total Failures: {stats['total_failures']}")
    print(f"Royalty: ${stats['royalty']:.2f}")
    kernel.export_log('kl-029-lexdrone-log.json')


if __name__ == "__main__":
    main()
