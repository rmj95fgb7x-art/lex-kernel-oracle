# Lex Liberatum - Blockchain Integration

## Architecture
User → Smart Contract (Base) → Chainlink Functions → API (Python) → Kernels
↓
Royalty to 0x44f8…C689
## Components

1. **LexKernelRegistry.sol** - Main contract, handles execution requests
2. **LexKernelSubscription.sol** - Monthly subscription model
3. **API Server** - FastAPI bridge to Python kernels
4. **Chainlink Functions** - Decentralized oracle network

## Quick Start

```bash
npm install
npm run deploy:testnet
cd api && uvicorn server:app
Costs
	∙	Execution: 0.0025 ETH + ~0.1 LINK per kernel call
	∙	Subscription: 0.05-5 ETH/month depending on tier
Support
Docs: https://docs.lexliberatum.io
Discord: https://discord.gg/lexliberatum
---

