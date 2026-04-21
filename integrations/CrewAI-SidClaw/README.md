# CrewAI + SidClaw

Adds a human approval and audit layer to CrewAI agents using [SidClaw](https://github.com/sidclawhq/platform) — an open-source governance SDK for AI agents.

This example shows a DevOps crew with two tools:

| Tool | Data classification | SidClaw decision |
|---|---|---|
| `deploy_to_production` | `confidential` | **Approval required** — waits for human sign-off before deploying |
| `run_db_migration` | `restricted` | **Denied** — blocked by policy, never executes |
| `check_service_health` | `internal` | **Allow** — runs immediately, full audit trace recorded |

## Why governance matters here

CrewAI agents are great at orchestrating complex DevOps workflows. But `deploy_to_production` and `run_db_migration` are irreversible. Without a governance layer, the crew decides and acts — no human checkpoint, no audit trail.

SidClaw adds:
- Policy evaluation before each tool call (< 50ms overhead)
- Human approval workflow for high-risk actions (approval card in dashboard)
- Tamper-proof hash-chain audit trace for every action
- One-line integration: `govern_crewai_tool(tool, client=client)`

## Prerequisites

1. Python 3.10+
2. A SidClaw account (free tier at [app.sidclaw.com](https://app.sidclaw.com) — 5 agents free)
3. An OpenAI API key

## Setup

```bash
# Clone and navigate
cd integrations/CrewAI-SidClaw

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

## Create agent and policies

Run the SidClaw CLI to set up your agent and policies:

```bash
npx create-sidclaw-app@latest --name devops-crew --template devops
```

Or create them in the dashboard at [app.sidclaw.com](https://app.sidclaw.com).

## Run the example

```bash
python main.py
```

Expected output:

```
[SidClaw] check_service_health → ALLOW (trace: trc_...)
  All services healthy.

[SidClaw] deploy_to_production → APPROVAL REQUIRED
  Waiting for approval in dashboard: https://app.sidclaw.com/dashboard/approvals
  (Approve or deny at app.sidclaw.com to continue)

[SidClaw] run_db_migration → DENY
  Blocked: database migrations require DBA review. Action was not executed.
```

## How it works

```python
from sidclaw import SidClaw
from sidclaw.middleware.crewai import govern_crewai_tool

client = SidClaw(api_key=os.environ["SIDCLAW_API_KEY"], agent_id="devops-crew")

governed_deploy = govern_crewai_tool(
    deploy_tool,
    client=client,
    data_classification="confidential",
)
```

`govern_crewai_tool` wraps the tool's `_run` method. Before execution, it calls the SidClaw policy engine. On `allow`, the tool runs and the outcome is recorded to the audit trace. On `approval_required`, execution pauses until a human approves or denies in the dashboard. On `deny`, `ActionDeniedError` is raised and the tool never executes.

## Self-hosting

SidClaw can be self-hosted with Docker:

```bash
git clone https://github.com/sidclawhq/platform
cd platform
docker compose up
```

The SDK license is Apache 2.0. The platform uses FSL 1.1 (free for organizations under CHF 1M annual revenue).

## Links

- [SidClaw GitHub](https://github.com/sidclawhq/platform)
- [Documentation](https://docs.sidclaw.com)
- [Live demo](https://demo-devops.sidclaw.com) (no signup needed)
- [PyPI](https://pypi.org/project/sidclaw/)
