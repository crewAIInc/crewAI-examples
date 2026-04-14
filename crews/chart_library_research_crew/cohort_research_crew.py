# -*- coding: utf-8 -*-
"""
CrewAI example — two-agent crew using Chart Library's cohort primitive
for grounded financial research.

Agents
------
Researcher — calls get_cohort_distribution + explain_cohort_filters to
             surface conditional structure. Never writes prose.
Analyst    — takes the researcher's numeric findings and writes a
             sized-up briefing for a portfolio manager. Must cite
             every number with its sample size and survivorship flag.

Run
---
    pip install crewai crewai-tools requests
    export OPENAI_API_KEY=sk-...       # or ANTHROPIC_API_KEY + tweak
    export CHART_LIBRARY_KEY=cl_...    # chartlibrary.io/developers
    python cohort_research_crew.py NVDA 2024-06-18
"""
from __future__ import annotations

import json
import os
import sys

import requests

try:
    from crewai import Agent, Crew, Process, Task
    from crewai.tools import tool
except ImportError:  # pragma: no cover
    raise SystemExit("pip install crewai crewai-tools requests")

CHART_BASE = "https://chartlibrary.io"
CHART_KEY = os.environ["CHART_LIBRARY_KEY"]
H = {"Authorization": f"Bearer {CHART_KEY}", "Content-Type": "application/json"}


# ── Tools ──────────────────────────────────────────────────

@tool("get_cohort_distribution")
def get_cohort(symbol: str, date: str, same_sector: bool = False,
               same_vix_bucket: bool = False, same_trend: bool = False) -> str:
    """Return historical forward-return distribution for a chart pattern.
    Returns JSON with cohort_id (use with other tools), return/MAE/MFE/RV
    percentiles at 5d and 10d, sample size, and survivorship flag.

    Args:
        symbol: Ticker e.g. 'NVDA'
        date: ISO date e.g. '2024-06-18'
        same_sector: restrict to same sector as anchor
        same_vix_bucket: restrict to same VIX regime
        same_trend: restrict to same SPY trend regime
    """
    filters = {}
    if same_sector:
        filters["sector"] = "same_as_anchor"
    regime = {}
    if same_vix_bucket: regime["same_vix_bucket"] = True
    if same_trend:      regime["same_trend"] = True
    if regime:
        filters["regime"] = regime
    body = {
        "anchor": {"symbol": symbol, "date": date},
        "filters": filters, "horizons": [5, 10],
        "top_k": 500, "include_path_stats": True,
    }
    r = requests.post(f"{CHART_BASE}/api/v1/cohort", headers=H, json=body, timeout=30)
    return json.dumps(r.json(), default=str)


@tool("explain_cohort_filters")
def explain_cohort(cohort_id: str, horizon: int = 5) -> str:
    """Rank which additional filter would shift the distribution most for
    a previously-returned cohort. Call AFTER get_cohort_distribution.
    """
    r = requests.get(
        f"{CHART_BASE}/api/v1/cohort/{cohort_id}/explain",
        headers=H, params={"horizon": horizon}, timeout=30,
    )
    return json.dumps(r.json(), default=str)


@tool("refine_cohort_with_filters")
def refine_cohort(cohort_id: str, same_vix_bucket: bool = False,
                  same_trend: bool = False) -> str:
    """Narrow a stored cohort with an extra regime filter. Sub-second.
    Returns a new cohort_id + updated distributions.
    """
    extra = {}
    regime = {}
    if same_vix_bucket: regime["same_vix_bucket"] = True
    if same_trend:      regime["same_trend"] = True
    if regime: extra["regime"] = regime
    r = requests.post(
        f"{CHART_BASE}/api/v1/cohort/{cohort_id}/filter",
        headers=H, json={"extra_filters": extra, "include_path_stats": True},
        timeout=30,
    )
    return json.dumps(r.json(), default=str)


# ── Agents ─────────────────────────────────────────────────

researcher = Agent(
    role="Quantitative Pattern Researcher",
    goal=(
        "For a given (symbol, date) setup, produce a fully-grounded set of "
        "conditional distribution statistics. Every number you return must "
        "come from a tool call; never synthesize forward-return statistics."
    ),
    backstory=(
        "You are a quantitative researcher who prioritizes honest base rates "
        "over plausible narrative. You know shape-only similarity is noisy, "
        "so you always refine the cohort with regime/sector filters and "
        "quote sample size plus survivorship in every claim."
    ),
    tools=[get_cohort, explain_cohort, refine_cohort],
    verbose=True,
    allow_delegation=False,
)

analyst = Agent(
    role="Portfolio Analyst",
    goal=(
        "Turn the researcher's numeric findings into a 150-word briefing "
        "for a discretionary portfolio manager. Every statistic must be "
        "cited with its sample size, and survivorship must be disclosed."
    ),
    backstory=(
        "You are a long-tenured analyst. You never trust forward-return "
        "numbers without sample size. You explicitly disclose survivorship "
        "because you've been burned by hidden bias before."
    ),
    tools=[],  # no direct data access — analyst works only from the researcher's output
    verbose=True,
    allow_delegation=False,
)


# ── Tasks ──────────────────────────────────────────────────

def build_tasks(symbol: str, date: str) -> list[Task]:
    return [
        Task(
            description=(
                f"Research the {symbol} setup on {date}. Steps:\n"
                f"  1. Call get_cohort_distribution({symbol!r}, {date!r}) with no filters.\n"
                f"  2. Note cohort_id, sample size, survivorship, and 5d/10d return/MAE/MFE/RV percentiles.\n"
                f"  3. Call explain_cohort_filters(cohort_id) to identify which filter "
                f"     (same_sector, same_vix_bucket, same_trend) shifts the distribution most.\n"
                f"  4. Call refine_cohort_with_filters(cohort_id, <winning_filter>=True) to narrow.\n"
                f"  5. Report the baseline vs refined comparison as structured JSON-like prose. "
                f"Do not write narrative — just the numbers."
            ),
            expected_output=(
                "A numeric-only report listing: baseline cohort stats (n, survivorship, "
                "5d percentiles, 10d percentiles), explain rankings, refined cohort stats, "
                "and the magnitude of shift caused by the winning filter."
            ),
            agent=researcher,
        ),
        Task(
            description=(
                "Write a 150-word PM briefing on the setup based solely on the researcher's "
                "findings. Include sample size for every statistic cited. Disclose survivorship "
                "(how many delisted names were in the cohort). End with a one-sentence "
                "sizing/risk implication. Do NOT invent any number not in the research output."
            ),
            expected_output="A 150-word briefing with embedded n= citations and a closing sizing line.",
            agent=analyst,
        ),
    ]


# ── Entry point ────────────────────────────────────────────

def main():
    symbol = sys.argv[1] if len(sys.argv) > 1 else "NVDA"
    date = sys.argv[2] if len(sys.argv) > 2 else "2024-06-18"
    crew = Crew(
        agents=[researcher, analyst],
        tasks=build_tasks(symbol, date),
        process=Process.sequential,
        verbose=True,
    )
    result = crew.kickoff()
    print("\n─── FINAL BRIEFING ───")
    print(result)


if __name__ == "__main__":
    main()
