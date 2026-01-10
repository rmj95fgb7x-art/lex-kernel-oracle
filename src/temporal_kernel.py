```python
# src/temporal_kernel.py

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class TemporalDataPoint:
    timestamp: float
    value: float

class TemporalAdaptiveKernel:
    def __init__(self, alpha: float = 0.5):
        self.alpha = alpha
        self.kernel_values: Dict[str, List[TemporalDataPoint]] = {}

    def update(self, key: str, timestamp: float, value: float):
        if key not in self.kernel_values:
            self.kernel_values[key] = []
        
        # Remove old data based on alpha (temporal forgetting factor)
        now = datetime.now().timestamp()
        current_data = [dp for dp in self.kernel_values[key] if now - dp.timestamp < 1 / self.alpha]
        current_data.append(TemporalDataPoint(timestamp, value))
        self.kernel_values[key] = current_data

    def get_value(self, key: str, timestamp: float) -> Optional[float]:
        data_points = self.kernel_values.get(key)
        if not data_points:
            return None
        
        # Interpolate or use the most recent value
        closest_time = min(data_points, key=lambda dp: abs(dp.timestamp - timestamp))
        return closest_time.value

    def get_mean(self, key: str) -> Optional[float]:
        data_points = self.kernel_values.get(key)
        if not data_points:
            return None
        
        return np.mean([dp.value for dp in data_points])

    def get_median(self, key: str) -> Optional[float]:
        data_points = self.kernel_values.get(key)
        if not data_points:
            return None
        
        return np.median([dp.value for dp in data_points])
```