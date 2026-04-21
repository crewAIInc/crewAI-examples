# Kalibr-Resilient Job Posting Crew

A production-grade CrewAI crew with automatic LLM routing and failure recovery via [Kalibr](https://kalibr.systems).

This example extends the standard job-posting crew with Kalibr's execution path router. The crew researches company culture, identifies role requirements, drafts a job posting, and reviews it — all while Kalibr monitors outcome signals and routes each LLM call to the model most likely to succeed.

## Why Kalibr

Most CrewAI examples are hardcoded to GPT-4o. That's fine for demos. In production:

- Provider degradation events (rate limits, latency spikes, partial outages) happen multiple times per week
- A single-model crew fails when that model degrades
- Kalibr routes to your backup model automatically, learned from live outcome data

**Benchmark results during a simulated GPT-4o degradation event:**
| Setup | Task Success Rate |
|---|---|
| Hardcoded GPT-4o | 16–36% |
| Kalibr-routed (GPT-4o + Claude Sonnet) | 88–100% |

## Running the Script

**Configure Environment**: Copy `.env.example` to `.env` and fill in:
- `OPENAI_API_KEY` — [OpenAI API key](https://platform.openai.com/api-keys)
- `ANTHROPIC_API_KEY` — [Anthropic API key](https://console.anthropic.com/) (fallback model)
- `SERPER_API_KEY` — [Serper](https://serper.dev) for web search
- `KALIBR_API_KEY` and `KALIBR_TENANT_ID` — [Kalibr dashboard](https://dashboard.kalibr.systems)

**Install Dependencies**: `uv sync`

**Execute**: `uv run kalibr_resilient_crew`

## How Kalibr works here

`import kalibr` at the top of `main.py` (before any OpenAI/Anthropic import) monkey-patches the SDK clients. From that point on, every LLM call the crew makes is:
1. Traced with task goal context
2. Routed to the currently-succeeding model
3. Scored on outcome (did the agent produce valid output?)
4. Used to improve future routing decisions

No changes to agent definitions, task configs, or crew logic.

## Get Kalibr credentials

```bash
pip install kalibr
kalibr auth  # device-code auth — opens browser, one click
```

Or sign up at [dashboard.kalibr.systems](https://dashboard.kalibr.systems).
