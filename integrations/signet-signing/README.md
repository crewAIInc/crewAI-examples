# CrewAI + Signet: Signed Tool Calls with Audit Trail

This example shows how to add Ed25519 cryptographic signing to every
CrewAI tool call, producing a tamper-evident audit log.

## Why

- Prove which agent called which tool, with what parameters, and when
- Detect log tampering via SHA-256 hash chain
- Comply with SOC 2 / HIPAA audit requirements for AI agent actions

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Verify the audit trail

```bash
signet audit --since 1h
signet audit --verify
signet verify --chain
```

## How it works

Signet hooks into CrewAI's `before_tool_use` / `after_tool_use` callbacks.
Every tool invocation is signed with the agent's Ed25519 key and appended
to a local hash-chained JSONL log at `~/.signet/audit/`.

No infrastructure required. No network calls. Pure local crypto.

## Learn more

- [Signet GitHub](https://github.com/Prismer-AI/signet)
- [PyPI: signet-auth](https://pypi.org/project/signet-auth/)
