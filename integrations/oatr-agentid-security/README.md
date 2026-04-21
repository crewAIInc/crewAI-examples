# CrewAI Trust Security

Three-layer security gate for [CrewAI](https://github.com/crewAIInc/crewAI) using open trust standards.

Verifies both **runtime identity** and **agent identity** before any crew task runs, using CrewAI's built-in `before_kickoff_callbacks` hook.

## The three layers

| Layer | What it checks | Standard |
|-------|---------------|----------|
| **OATR** | Is the runtime registered and non-revoked? | [Open Agent Trust Registry](https://github.com/FransDevelopment/open-agent-trust-registry) |
| **AgentID** | Is this specific agent who it claims to be? | [AgentID](https://github.com/haroldmalikfrimpong-ops/getagentid) |
| **Security Gate** | Combined pre-kickoff check via CrewAI callback | This repo |

## What each layer catches

| Attack | OATR | AgentID | Together |
|--------|------|---------|----------|
| Rogue runtime impersonating a trusted one | Blocked | Not its scope | Blocked |
| Compromised agent within a trusted runtime | Runtime looks fine | Blocked | Blocked |
| Revoked runtime (key compromise) | Blocked | Not its scope | Blocked |
| Replayed credential from a different agent | Not its scope | Blocked | Blocked |

## Quick start

```bash
cp .env.example .env
# Fill in your API keys in .env
uv sync
uv run main.py
```

## Usage

```python
from crewai import Agent, Task, Crew
from security_gate import security_gate

crew = Crew(
    agents=[...],
    tasks=[...],
    before_kickoff_callbacks=[security_gate],
)

# Without attestation: gate passes (both checks are optional)
crew.kickoff(inputs={"topic": "your topic"})

# With runtime attestation: OATR verifies before tasks run
crew.kickoff(inputs={
    "topic": "your topic",
    "runtime_attestation": "<JWT from your runtime>",
    "audience": "https://your-crew.com",
})

# With both layers: runtime + agent identity verified
crew.kickoff(inputs={
    "topic": "your topic",
    "runtime_attestation": "<JWT>",
    "agent_id": "<AgentID identifier>",
    "audience": "https://your-crew.com",
})
```

## How the security gate works

The `security_gate` function runs before `Crew.kickoff()` via CrewAI's [`before_kickoff_callbacks`](https://github.com/crewAIInc/crewAI/blob/main/lib/crewai/src/crewai/crew.py#L233).

**Layer 1 (OATR):** Fetches the signed registry manifest (cached for 15 minutes), decodes the JWT header to extract the issuer ID and key ID, looks up the issuer in the manifest, checks status is active, and verifies the Ed25519 signature. If any step fails, the crew does not start.

**Layer 2 (AgentID):** Verifies the specific agent's identity via AgentID's verification API. This checks that the individual agent (not just the runtime) is registered and authorized. Optional if `agentid-crewai` is not installed.

**Layer 3 (Combined):** Both checks run in sequence. The crew only starts if all provided credentials pass verification.

## OATR verification codes

| Code | Meaning |
|------|---------|
| `unknown_issuer` | Issuer not found in the registry manifest |
| `revoked_issuer` | Issuer is revoked or status is not active |
| `unknown_key` | Issuer found but key ID doesn't match any active key |
| `expired_attestation` | JWT has expired |
| `audience_mismatch` | JWT audience doesn't match expected value |
| `invalid_signature` | Ed25519 signature verification failed |

## Per-step verification

For tighter enforcement, use CrewAI's `step_callback` to re-verify before each tool call:

```python
from security_gate import verify_runtime_attestation

def step_verifier(step_output):
    """Re-verify runtime attestation before each step."""
    attestation = step_output.get("runtime_attestation")
    if attestation:
        result = verify_runtime_attestation(attestation, audience="https://your-crew.com")
        if not result["valid"]:
            raise PermissionError(f"Step blocked: {result['reason']}")
    return step_output

crew = Crew(
    agents=[...],
    tasks=[...],
    before_kickoff_callbacks=[security_gate],
    step_callback=step_verifier,
)
```

## Context

This example was built as a collaboration between the [Open Agent Trust Registry](https://github.com/FransDevelopment/open-agent-trust-registry) and [AgentID](https://github.com/haroldmalikfrimpong-ops/getagentid), both members of the [Agent Identity Working Group](https://github.com/corpollc/qntm/issues/5).

The WG has ratified three specs (QSP-1 Envelope Format, DID Resolution v1.0, Entity Verification v1.0) with cross-implementation conformance tests across 6 independent projects.

Related thread: [crewAIInc/crewAI#5019](https://github.com/crewAIInc/crewAI/issues/5019)

## License

MIT
