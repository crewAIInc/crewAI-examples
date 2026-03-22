# Stamp Verified — Trust-Gated Agent Crew

A CrewAI example that verifies AI agent trustworthiness before task coordination using [AgentStamp](https://agentstamp.org).

## What It Does

1. **Trust Analyst** agent checks an AI agent's trust profile via AgentStamp's free API
2. **Task Coordinator** only assigns work to agents that pass the trust threshold
3. The crew produces a trust verification report + task coordination plan

## AgentStamp Trust Check

AgentStamp provides cryptographic identity stamps and trust scoring (0-100) for AI agents. The trust check API is free and requires no API key.

Each trust check returns:
- **Trust score** (0-100) — reputation built through heartbeats, endorsements, and uptime
- **Stamp tier** — free, bronze, silver, or gold (higher tiers = stronger identity)
- **Endorsements** — peer endorsements from other verified agents
- **Heartbeat status** — whether the agent is actively maintaining its reputation

## Running the Example

### Prerequisites

- Python 3.10-3.13
- [UV](https://docs.astral.sh/uv/) package manager
- OpenAI API key

### Setup

```bash
cd crews/stamp_verified
cp .env.example .env
# Edit .env with your OpenAI API key
```

### Install & Run

```bash
uv sync
uv run stamp_verified
```

### Custom Agent Verification

Edit `src/stamp_verified/main.py` to verify a specific agent:

```python
inputs = {
    "wallet_address": "0xYourAgentWallet",  # Agent to verify
    "min_score": 50,                         # Minimum trust threshold
    "task_description": "Your task here",
}
```

## Key Components

### Custom Tool: `AgentStampTrustCheckTool`

Located in `src/stamp_verified/tools/trust_check_tool.py` — a CrewAI tool that calls the AgentStamp trust API. No API key needed.

```python
from stamp_verified.tools.trust_check_tool import AgentStampTrustCheckTool

# Use in any CrewAI agent
agent = Agent(
    role="Trust Verifier",
    tools=[AgentStampTrustCheckTool()],
    ...
)
```

### Trust-Gated Workflow

The crew runs sequentially: trust check first, task coordination second. The coordinator only proceeds if the agent passes verification — a pattern useful for any multi-agent system where trust matters.

## Learn More

- [AgentStamp](https://agentstamp.org) — Trust verification for AI agents
- [AgentStamp GitHub Action](https://github.com/vinaybhosle/agentstamp/tree/main/action) — CI/CD trust gates
- [CrewAI Docs](https://docs.crewai.com) — Multi-agent framework

By [@vinaybhosle](https://github.com/vinaybhosle)
