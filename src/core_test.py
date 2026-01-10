```python
# src/core_test.py

import unittest
from src.core import Core
from src.temporal_kernel import TemporalAdaptiveKernel

class TestCore(unittest.TestCase):
    def test_register_and_get_kernel(self):
        core = Core()
        
        kernel = TemporalAdaptiveKernel(alpha=1.0)
        core.register_kernel("test_kernel", kernel)
        
        retrieved_kernel = core.get_kernel("test_kernel")
        
        self.assertIsInstance(retrieved_kernel, TemporalAdaptiveKernel)

if __name__ == '__main__':
    unittest.main()
```