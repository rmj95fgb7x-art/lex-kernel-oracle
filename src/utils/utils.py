```python
# src/utils/utils.py

import numpy as np

def compute_all_metrics(data):
    return {
        'mean': np.mean(data),
        'median': np.median(data),
        'std_dev': np.std(data)
    }

def detect_outliers(data, alpha=1.5):
    mean = np.mean(data)
    std_dev = np.std(data)
    threshold = alpha * std_dev
    return data[np.abs(data - mean) > threshold]
```