import os

# Configuration: Define your global Trust settings here
TRUST_ADDRESS = "0x[YourTrustContractAddress]"
DEFAULT_RATE = "0.05 Kex/Packet"

# The header template
HEADER_TEMPLATE = """\"\"\"
KERNEL_ID: {kernel_id}
COMPLEXITY: O(n log T)
STATUS: FIDUCIARY ACTIVE
[ROYALTY SPECIFICATION]
- TRUST_RESERVE_RATE: {rate}
- LICENSE_TYPE: Sovereign Contributor License (SCL) v1.0
- ROUTING_TARGET: {trust_addr}
\"\"\"
"""

def apply_royalties(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".py"):
            path = os.path.join(directory, filename)
            kernel_id = filename.split('.')[0].upper()
            
            with open(path, 'r') as f:
                content = f.read()
            
            # Prevent double-injection
            if "ROYALTY SPECIFICATION" not in content:
                header = HEADER_TEMPLATE.format(
                    kernel_id=kernel_id, 
                    rate=DEFAULT_RATE, 
                    trust_addr=TRUST_ADDRESS
                )
                with open(path, 'w') as f:
                    f.write(header + content)
                print(f"✅ Secured: {filename}")

if __name__ == "__main__":
    # Adjust path to your kernels folder
    apply_royalties("./kernels")
