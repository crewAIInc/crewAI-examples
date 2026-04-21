# Spraay Batch Payments – CrewAI Integration

A multi-agent CrewAI crew that enables AI agents to execute batch cryptocurrency payments on **Base** using the [Spraay protocol](https://spraay-base-dapp.vercel.app). Send ETH and ERC-20 tokens to up to **200 recipients in a single transaction** with **~80% gas savings**.

## Features

- **Batch ETH Payments** – Send equal or variable ETH amounts to multiple wallets
- **Batch Token Payments** – Distribute any ERC-20 token (USDC, USDT, etc.) with automatic approval
- **Multi-Agent Workflow** – Payment Planner → Executor → Reporter pipeline
- **Gas Efficient** – Up to 80% cheaper than individual transfers
- **4 Spraay Tools** – `batchSendETH`, `batchSendToken`, `batchSendETHVariable`, `batchSendTokenVariable`

## Architecture

```
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  Payment Planner │───▶│ Payment Executor │───▶│ Payment Reporter │
│                  │    │                  │    │                  │
│ • Validate addrs │    │ • Select tool    │    │ • Tx summary     │
│ • Choose method  │    │ • Execute on-chain│    │ • Gas savings    │
│ • Calculate fees │    │ • Return receipt │    │ • BaseScan link  │
└──────────────────┘    └──────────────────┘    └──────────────────┘
```

## Quick Start

### 1. Install Dependencies

```bash
pip install crewai crewai-tools web3
```

### 2. Set Environment Variables

```bash
export SPRAAY_PRIVATE_KEY="your_private_key_here"
export SPRAAY_RPC_URL="https://mainnet.base.org"  # optional, this is the default
export OPENAI_API_KEY="your_openai_key"
```

### 3. Run the Crew

```bash
python spraay_batch_payment_crew.py
```

### 4. Custom Payment Request

```python
from spraay_batch_payment_crew import create_spraay_crew

crew = create_spraay_crew()
result = crew.kickoff(inputs={
    "payment_request": (
        "Send 100 USDC to each of these addresses using token "
        "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913 (USDC on Base):\n"
        "0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18\n"
        "0x53d284357ec70cE289D6D64134DfAc8E511c8a3D"
    )
})
print(result)
```

## Available Tools

| Tool | Function | Use Case |
|------|----------|----------|
| `spraay_batch_send_eth` | `batchSendETH` | Equal ETH to N recipients |
| `spraay_batch_send_token` | `batchSendToken` | Equal tokens to N recipients |
| `spraay_batch_send_eth_variable` | `batchSendETHVariable` | Different ETH amounts per recipient |
| `spraay_batch_send_token_variable` | `batchSendTokenVariable` | Different token amounts per recipient |

## Using Tools Directly (Without Crew)

```python
from spraay_batch_payment_crew import SpraayBatchSendETHTool
from crewai import Agent

agent = Agent(
    role="Payroll Manager",
    goal="Process weekly team payments",
    tools=[SpraayBatchSendETHTool()],
    verbose=True,
)
```

## Common Token Addresses (Base)

| Token | Address |
|-------|---------|
| USDC | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` |
| USDT | `0xfde4C96c8593536E31F229EA8f37b2ADa2699bb2` |
| DAI | `0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb` |
| WETH | `0x4200000000000000000000000000000000000006` |

## How It Works

1. **Payment Planner** analyzes the request — validates addresses, selects equal vs variable distribution, calculates fees
2. **Payment Executor** calls the appropriate Spraay smart contract function via web3.py
3. **Payment Reporter** generates a summary with transaction hash, BaseScan link, and gas savings estimate

## Spraay Protocol Details

- **Contract**: [`0x1646452F98E36A3c9Cfc3eDD8868221E207B5eEC`](https://basescan.org/address/0x1646452F98E36A3c9Cfc3eDD8868221E207B5eEC) (Base mainnet)
- **Max recipients**: 200 per transaction
- **Protocol fee**: 0.3%
- **Chains**: Base, Arbitrum, Unichain, Plasma, BOB, Bittensor
- **Website**: [spraay-base-dapp.vercel.app](https://spraay-base-dapp.vercel.app)

## Security Notes

- Never commit your private key — use environment variables
- Always verify recipient addresses before executing payments
- Test with small amounts first
- The Spraay contract is deployed and verified on BaseScan

## License

MIT
