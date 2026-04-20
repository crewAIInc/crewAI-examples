# Calendar Scheduling Crew

A multi-agent crew that schedules conflict-free calendar meetings using [Temporal Cortex](https://github.com/temporal-cortex/mcp), an MCP server that gives CrewAI agents deterministic calendar tools.

## What It Does

Three agents collaborate to schedule a meeting:

1. **Temporal Analyst** — Gets the current time and resolves natural language like "next Tuesday at 2pm" into precise timestamps
2. **Calendar Manager** — Discovers connected calendars and finds available time slots
3. **Scheduling Coordinator** — Books the meeting using Two-Phase Commit (no double-bookings)

The crew uses CrewAI's native `MCPServerAdapter` to auto-discover all 12 Temporal Cortex tools — no wrapper code needed.

## Why Not Just Use a Calendar API Directly?

LLMs score below 50% on temporal reasoning ([OOLONG benchmark](https://arxiv.org/abs/2511.02817)). They pick the wrong Tuesday, check the wrong timezone, and double-book your calendar. Temporal Cortex replaces LLM inference with deterministic computation for all calendar math — datetime resolution, cross-provider availability merging (Google + Outlook + CalDAV), and atomic booking.

## Prerequisites

- Python 3.10+
- Node.js 18+
- A Google Calendar, Microsoft Outlook, or CalDAV account

## Setup

1. Install dependencies:
   ```bash
   pip install crewai crewai-tools[mcp] python-dotenv
   ```

2. Authenticate with your calendar provider:
   ```bash
   npx @temporal-cortex/cortex-mcp auth google
   ```

3. Configure environment:
   ```bash
   cp .env_example .env
   # Edit .env with your Google OAuth credentials
   ```

4. Run:
   ```bash
   python main.py
   ```

## Customization

- **Change the meeting details**: Edit `main.py` to modify the meeting title, duration, or target time
- **Add more agents**: The [tool reference](https://github.com/temporal-cortex/mcp/blob/main/docs/tools.md) documents all 15 tools across 5 layers
- **Use Platform Mode**: Replace stdio with SSE transport to connect to the managed Temporal Cortex Platform (no Node.js required) — see `main.py` comments
- **Use DSL syntax**: For the simplest integration, use the `mcps` field directly on Agent instead of MCPServerAdapter

## Cost

This example uses your default LLM (typically GPT-4 or equivalent). A single crew run with 3 agents and 3 tasks costs approximately $0.05–0.15 in LLM API fees, depending on your model. The Temporal Cortex MCP server is free and runs locally.
