```python
# src/temporal_kernel_test.py

import unittest
from src.temporal_kernel import TemporalAdaptiveKernel

class TestTemporalAdaptiveKernel(unittest.TestCase):
    def test_update_and_get_value(self):
        kernel = TemporalAdaptiveKernel(alpha=1.0)
        kernel.update("test_key", 0, 10)
        
        self.assertEqual(kernel.get_value("test_key", 0), 10)

    def test_temporal_forgetting(self):
        kernel = TemporalAdaptiveKernel(alpha=2.0)
        for t in range(5):
            kernel.update("test_key", t, t * 10)
        
        # Only the last value should be retained
        self.assertEqual(kernel.get_value("test_key", 4), 40)

    def test_get_mean_and_median(self):
        kernel = TemporalAdaptiveKernel(alpha=2.0)
        for t in range(5):
            kernel.update("test_key", t, t * 10)
        
        self.assertEqual(kernel.get_mean("test_key"), 20)
        self.assertEqual(kernel.get_median("test_key"), 20)

if __name__ == '__main__':
    unittest.main()
```