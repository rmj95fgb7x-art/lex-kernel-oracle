```python
# src/utils_test.py

import unittest
from src.utils import compute_all_metrics, detect_outliers

class TestUtils(unittest.TestCase):
    def test_compute_all_metrics(self):
        data = [1, 2, 3, 4, 5]
        metrics = compute_all_metrics(data)
        
        self.assertEqual(metrics['mean'], 3.0)
        self.assertEqual(metrics['median'], 3.0)
        self.assertAlmostEqual(metrics['std_dev'], 1.4142135623730951)

    def test_detect_outliers(self):
        data = [1, 2, 3, 4, 100]
        outliers = detect_outliers(data)
        
        self.assertListEqual(outliers, [100])

if __name__ == '__main__':
    unittest.main()
```