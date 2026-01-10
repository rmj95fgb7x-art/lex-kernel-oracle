```python
# src/core/core.py

class Core:
    def __init__(self):
        self.kernels = {}

    def register_kernel(self, kernel_name, kernel_instance):
        self.kernels[kernel_name] = kernel_instance

    def get_kernel(self, kernel_name):
        return self.kernels.get(kernel_name)
```