# Decision Anchor MCP Integration

Connect CrewAI agents to [Decision Anchor](https://github.com/zse4321/decision-anchor-sdk)'s remote MCP server using `MCPServerAdapter`.

Decision Anchor provides external accountability proof for agent payments, delegation, and disputes via MCP. It does not monitor, judge, or intervene.

## What this example does

1. Connects to DA's MCP server (`https://mcp.decision-anchor.com/mcp`) via `MCPServerAdapter`
2. Registers a new agent (one-time, no DA API key required)
3. Creates a Decision Declaration (DD) with accountability scope for a delegated task
4. Reports the DD ID and anchored timestamp

## Setup

```bash
pip install crewai crewai-tools[mcp]
```

## Usage

```bash
export OPENAI_API_KEY=your_key
python main.py
```

## Notes

- No DA API key needed — agents register via MCP tools and receive Trial 500 DAC / 30 days
- Running this creates a real agent registration and decision record on DA
- The MCP server uses streamable HTTP transport
- Full agent guide: [AGENTS.md](https://github.com/zse4321/decision-anchor-sdk/blob/main/AGENTS.md)
