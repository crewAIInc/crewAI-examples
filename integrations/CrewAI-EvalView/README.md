# CrewAI + EvalView — Regression Testing for Crews

Catch silent regressions in your CrewAI agents. EvalView snapshots your crew's full execution trace — which agent called which tool, in what order, with what parameters — and diffs it against a golden baseline on every change.

```
  ✓ stock-analysis           PASSED
  ⚠ content-team             TOOLS_CHANGED
      Step 2: analyst_agent
      - calculator_tool(ticker="AAPL", metric="pe_ratio")
      + calculator_tool(ticker="AAPL", metric="market_cap")
  ✗ trip-planner             REGRESSION  -25 pts
      researcher_agent skipped search_tool entirely
```

`crewai test` tells you scores. EvalView tells you **what changed and why.**

## Quick Start

### 1. Install

```bash
pip install evalview crewai crewai-tools
```

### 2. Define your crew

```python
# crew.py
from crewai import Agent, Crew, Task, Process

researcher = Agent(
    role="Researcher",
    goal="Research topics thoroughly",
    backstory="You are an expert researcher.",
    tools=[search_tool],
)

writer = Agent(
    role="Writer",
    goal="Write clear, accurate content",
    backstory="You are a skilled writer.",
)

research_task = Task(
    description="Research {topic} and provide key findings",
    expected_output="A summary of key findings",
    agent=researcher,
)

writing_task = Task(
    description="Write a report based on the research findings",
    expected_output="A well-written report",
    agent=writer,
)

crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
    process=Process.sequential,
)
```

### 3. Set up EvalView with native adapter

```python
# evalview_setup.py
from crew import crew
from evalview.adapters.crewai_native_adapter import CrewAINativeAdapter

adapter = CrewAINativeAdapter(crew=crew)
```

Or configure via YAML (no Python needed):

```yaml
# .evalview/config.yaml
adapter: crewai-native
crew_module: crew
crew_attribute: crew
```

### 4. Write test cases

```yaml
# tests/research-report.yaml
name: research-report
adapter: crewai-native
crew_module: crew
crew_attribute: crew

input:
  query: "Write a report about renewable energy trends"
  topic: "renewable energy trends 2026"

expected:
  tools:
    - search_tool
  output:
    contains:
      - "renewable"
      - "energy"
    not_contains:
      - "error"

thresholds:
  min_score: 70
  max_latency: 120000
```

### 5. Snapshot and check

```bash
evalview snapshot    # Capture baseline
# ... make changes to prompts, tools, or models ...
evalview check       # Catch regressions
```

## How EvalView Works with CrewAI

The native adapter:

1. Calls `crew.kickoff()` directly — no HTTP server or `--serve` flag needed
2. Captures tool calls via CrewAI's event bus (`ToolUsageFinishedEvent`) with exact arguments, output, agent role, and timing
3. Extracts per-task results from `CrewOutput.tasks_output`
4. Gets token usage from `CrewOutput.token_usage`

This gives EvalView full visibility into the crew's execution — not just the final output.

## CI Integration

Block broken crews in every PR:

```yaml
# .github/workflows/evalview.yml
name: EvalView Crew Check
on: [pull_request]

jobs:
  check:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
      - name: Check for regressions
        uses: hidai25/eval-view@main
        with:
          openai-api-key: ${{ secrets.OPENAI_API_KEY }}
```

## Watch Mode

Re-run checks on every file save while iterating on prompts:

```bash
evalview watch --quick    # No LLM judge, $0, sub-second
```

## Handling Non-Determinism

CrewAI agents are non-deterministic. EvalView handles this:

```bash
# Save alternate valid behaviors (up to 5 variants)
evalview snapshot --variant v2

# Or auto-discover variants
evalview check --statistical 10 --auto-variant
```

## Links

- [EvalView](https://github.com/hidai25/eval-view) — Open-source regression testing for AI agents
- [EvalView CrewAI Adapter](https://github.com/hidai25/eval-view/blob/main/evalview/adapters/crewai_native_adapter.py)
- [CrewAI Testing Docs](https://docs.crewai.com/concepts/testing)
