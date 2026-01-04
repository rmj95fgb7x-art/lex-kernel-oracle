# Deployment History

## Base Sepolia Testnet

**Deployed:** January 3, 2025  
**Deployer:** `0x1a4C4d943aa165924f1b8BC975A44B8e6938AA45`

### Smart Contracts

| Contract | Address | BaseScan |
|----------|---------|----------|
| LexKernelRegistry | `0xfFbEed10A8e4b41775E3800a340b20762Bf0B360` | [View →](https://sepolia.basescan.org/address/0xfFbEed10A8e4b41775E3800a340b20762Bf0B360) |
| LexKernelSubscription | `0x48EAFE021EB16d9848258e6FC2653f6fef6aB5dd` | [View →](https://sepolia.basescan.org/address/0x48EAFE021EB16d9848258e6FC2653f6fef6aB5dd) |

### Registered Kernels

| Kernel ID | Transaction Hash | BaseScan |
|-----------|------------------|----------|
| kl-052-lexbank | `0x736f07a3...` | [View →](https://sepolia.basescan.org/tx/0x736f07a3672b3f9c7c5ec4dc9d8ccc7b3ccab17d3a53ac140faf7e525ed2c7bd) |
| kl-091-lextrade | `0x5ed07e77...` | [View →](https://sepolia.basescan.org/tx/0x5ed07e77683d999e8907232a30fbaa6e11588186b2b4cca76ccfba510a17f1df) |
| kl-098-lexad | `0x5f01275d...` | [View →](https://sepolia.basescan.org/tx/0x5f01275d3c012f4346bd795400aca4016d505767f4481e37af486959fa719f65) |

### Test Executions

| # | Transaction Hash | Status | BaseScan |
|---|------------------|--------|----------|
| 1 | `0x14e8d804...` | ✅ Success | [View →](https://sepolia.basescan.org/tx/0x14e8d804cd4f296dc08b4191eb4b262444200ea0e4892e22e6df379ae66a618f) |
| 2 | `0xbac0e1b4...` | ✅ Success | [View →](https://sepolia.basescan.org/tx/0xbac0e1b4b1b3e20a5b7f5737234b397efa38e61d8b091b8d5208b2516aa0565f) |
| 3 | `0x9512583a...` | ✅ Success | [View →](https://sepolia.basescan.org/tx/0x9512583a1379986bd4979761cd82e610c7706045ea03c3c00e868a438287a5c1) |
| 4 | `0x51734938...` | ✅ Success | [View →](https://sepolia.basescan.org/tx/0x51734938c025103235d48274c36d3465af3cef7b96aef2733f53904a1e3f34d7) |
| 5 | `0x4a376958...` | ✅ Success | [View →](https://sepolia.basescan.org/tx/0x4a3769588f35adddc171d3aacec1bff3338cfebdfa7ab3f0a7443cd9fe489225) |

### Royalty Verification

**Beneficiary Address:** `0x44f8219cBABad92E6bf245D8c767179629D8C689`  
**Total Received:** 0.0004 ETH (5 executions × 0.0001 ETH)

[View Beneficiary on BaseScan →](https://sepolia.basescan.org/address/0x44f8219cBABad92E6bf245D8c767179629D8C689)

---

## Base Mainnet

**Status:** 🚧 Coming Q2 2025

---

## How to Interact

### Execute a Kernel (Web3.js)

```javascript
const registry = new ethers.Contract(
  "0xfFbEed10A8e4b41775E3800a340b20762Bf0B360",
  registryABI,
  signer
);

const params = ethers.toUtf8Bytes(JSON.stringify({
  transaction: { amount: 1000, ... }
}));

const tx = await registry.executeKernel(
  "kl-052-lexbank",
  params,
  { value: ethers.parseEther("0.0001") }
);

await tx.wait();
console.log("Executed! Hash:", tx.hash);
