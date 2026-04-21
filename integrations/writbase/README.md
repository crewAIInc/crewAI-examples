# WritBase Task Backend for CrewAI

## Introduction

Use [WritBase](https://github.com/Writbase/writbase) as a persistent, shared task backend for CrewAI agents. Tasks survive crew restarts, are auditable, and can be shared across multiple crews.

WritBase is an MCP-native task management system for AI agent fleets. It provides:

- **Persistent tasks** — tasks stored in Postgres, not lost when a crew stops
- **Multi-agent coordination** — multiple crews can share a task queue
- **Full provenance** — every status change and note is logged with actor attribution
- **Agent permissions** — fine-grained control over what each agent can read, create, or update

## Prerequisites

- A Supabase project with WritBase deployed (`npx writbase init`)
- An agent key created via the WritBase dashboard or CLI (`npx writbase key create`)
- Python 3.10+
- An OpenAI API key (or any LLM provider supported by CrewAI)

## Setup

1. Clone this example:

```bash
git clone https://github.com/crewAIInc/crewAI-examples.git
cd crewAI-examples/integrations/writbase
```

2. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Copy the environment template and fill in your values:

```bash
cp .env.example .env
```

Edit `.env` with your WritBase Supabase URL, agent key, and OpenAI API key.

4. Run the example:

```bash
python main.py
```

## How It Works

The crew connects to WritBase via its MCP HTTP endpoint using JSON-RPC 2.0 calls:

1. **Fetch tasks** — calls `get_tasks` to retrieve tasks assigned to this agent with status `todo`
2. **Process tasks** — a CrewAI crew with a researcher and writer agent processes each task
3. **Update results** — calls `update_task` to set the task status to `done` and attach the result as notes

## Architecture

```
+-------------------+         +---------------------------+         +------------+
|                   |  HTTP   |                           |         |            |
|   CrewAI Crew     +-------->+  WritBase MCP Endpoint    +-------->+  Postgres  |
|   (this script)   |  JSON-  |  (Supabase Edge Function) |         |  (tasks,   |
|                   |  RPC    |                           |         |   logs)    |
+-------------------+         +---------------------------+         +------------+
        |                                                                 ^
        |                          other crews / agents                   |
        |                     +------------------------+                  |
        +-------------------->+  WritBase Dashboard    +------------------+
                              +------------------------+
```

## MCP Endpoint Reference

All calls go to `{WRITBASE_URL}/functions/v1/mcp-server` with header `X-Agent-Key: {WRITBASE_AGENT_KEY}`.

### Fetch assigned tasks

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "get_tasks",
    "arguments": {"status": "todo", "assigned_to_me": true}
  },
  "id": 1
}
```

### Update a task

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "update_task",
    "arguments": {"task_id": "...", "status": "done", "notes": "Result here"}
  },
  "id": 2
}
```

## Learn More

- [WritBase GitHub](https://github.com/Writbase/writbase)
- [CrewAI Documentation](https://docs.crewai.com)
