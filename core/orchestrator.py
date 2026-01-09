import importlib.util
import yaml
import sys

class LexOrchestrator:
    def __init__(self, registry_path="registry.yaml"):
        with open(registry_path, 'r') as f:
            self.registry = yaml.safe_load(f)['kernels']
        self.active_pipeline = []

    def activate_kernel(self, kernel_id):
        """Dynamic Loading: Pulls a kernel into memory only when needed."""
        meta = next((k for k in self.registry if k['id'] == kernel_id), None)
        if not meta:
            print(f"⚠️ Warning: Kernel {kernel_id} not found.")
            return

        # Load the file from path
        spec = importlib.util.spec_from_file_location(meta['id'], meta['path'])
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Initialize the kernel (Assumes a standard 'LexKernel' class in each file)
        instance = module.LexKernel()
        self.active_pipeline.append(instance)
        print(f"🛡️ Kernel Activated: {kernel_id}")

    def execute_shield(self, data):
        """Passes data through the active mathematical pipeline."""
        for kernel in self.active_pipeline:
            data = kernel.execute(data)
        return data

# Usage example for Lex OS boot:
# brain = LexOrchestrator()
# brain.activate_kernel("LEX_SPECTRAL")
