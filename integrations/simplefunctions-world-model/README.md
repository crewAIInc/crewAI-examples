# World-Aware CrewAI Crew

A multi-agent crew where every agent shares the same real-time world context. The research analyst, risk officer, and briefing writer all see the same calibrated probabilities — no contradictions.

## The Problem

In a multi-agent crew, each agent hallucinates different numbers. The researcher says "recession probability is low." The risk officer says "recession probability is elevated." They're not disagreeing — they just have different training data cutoffs.

## The Solution

Fetch real-time world state from prediction markets once, share it across all agents. Data comes from [SimpleFunctions](https://simplefunctions.dev/world) — 9,706 contracts on Kalshi (CFTC-regulated) and Polymarket. No API key needed.

## Setup

```bash
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...
```

## Run

```bash
python main.py
```

## Architecture

```
SimpleFunctions World API (one call, ~800 tokens)
    ↓
Shared Context (all agents see same probabilities)
    ↓
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│   Researcher     │ → │  Risk Officer    │ → │  Briefing Writer │
│  - world_state   │   │  - world_state   │   │  (context from   │
│  - search_markets│   │  - market_detail │   │   both agents)   │
└─────────────────┘   └─────────────────┘   └─────────────────┘
```

## Output Example

Instead of vague hedging:
> "Geopolitical tensions remain elevated. We recommend monitoring the situation."

You get data-driven briefings:
> "Iran invasion probability: 53% (+5c). Hormuz disruption: 95%. Oil at $127 (+3.2%). Geopolitical Risk: 85/100. Recession: 33%. Primary risk: unhedged energy exposure. Action: review commodity hedges by EOD."

## Tools

| Tool | Description |
|------|-------------|
| `get_focused_world_state` | Deeper coverage of specific topics |
| `search_prediction_markets` | Find specific contracts by keyword |
| `get_market_detail` | Orderbook depth and thesis edges for a contract |
