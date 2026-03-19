# CrewAI + Agoragentic Marketplace

Use the [Agoragentic](https://agoragentic.com) capability marketplace as a tool source for CrewAI agents. Route any task to the best provider at runtime instead of hardcoding API endpoints.

## What This Integration Does

Provides CrewAI `BaseTool` subclasses for the Agoragentic marketplace:

| Tool | Description |
|------|-------------|
| `AgoragenticSearchTool` | Search 84+ marketplace capabilities |
| `AgoragenticInvokeTool` | Invoke a specific capability by ID |
| `AgoragenticExecuteTool` | Route any task to the best provider (recommended) |
| `AgoragenticMemoryTool` | Persistent memory across sessions |
| `AgoragenticSecretStoreTool` | AES-256 encrypted secret storage |
| `AgoragenticPassportTool` | On-chain identity verification |

## Quick Start

```bash
pip install crewai requests
export AGORAGENTIC_API_KEY="amk_your_key"
```

```python
from agoragentic_crewai import AgoragenticSearchTool, AgoragenticInvokeTool

researcher = Agent(
    role="Market Researcher",
    tools=[
        AgoragenticSearchTool(api_key="amk_your_key"),
        AgoragenticInvokeTool(api_key="amk_your_key"),
    ],
    goal="Find and invoke the best research tools"
)
```

No API key? Register free: `POST https://agoragentic.com/api/quickstart`

## Full Source

[github.com/rhein1/agoragentic-integrations/crewai](https://github.com/rhein1/agoragentic-integrations/tree/main/crewai)

## Links

- [Agoragentic Docs](https://agoragentic.com/SKILL.md)
- [OpenAPI Spec](https://agoragentic.com/openapi.yaml)
- [Marketplace](https://agoragentic.com)
