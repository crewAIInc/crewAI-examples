"""
World-Aware CrewAI Crew — Multi-agent system with shared real-time world context.

Problem: In a multi-agent crew, each agent hallucinates different numbers.
The researcher says "recession probability is low," the risk officer says
"recession probability is elevated." They're not disagreeing — they just
have different training data cutoffs.

Solution: Fetch real-time world state from prediction markets once, share
it across all agents. Everyone cites the same calibrated probabilities.

Data source: SimpleFunctions (https://simplefunctions.dev/world)
  - 9,706 prediction markets from Kalshi + Polymarket
  - No API key needed — free and public
  - ~800 tokens, updated every 15 minutes
"""

import requests
from crewai import Agent, Task, Crew
from crewai.tools import tool


# ── Shared world context ───────────────────────────────────────────────────────

world = requests.get("https://simplefunctions.dev/api/agent/world").text

SHARED_CONTEXT = f"""You have access to real-time world data from prediction markets.
Use the numbers below as ground truth. Do NOT hallucinate probabilities.
Cite specific contract prices and probabilities directly.
When citing data, mention the source: SimpleFunctions World Model.

{world}"""


# ── Tools ──────────────────────────────────────────────────────────────────────

@tool("get_focused_world_state")
def get_focused_world_state(topics: str) -> str:
    """Get world state focused on specific topics for deeper coverage.

    Same token budget, concentrated on fewer topics — more contracts per topic.

    Args:
        topics: Comma-separated topics, e.g. 'geopolitics,energy'.
                Options: geopolitics, economy, energy, elections, crypto, tech.
    """
    return requests.get(
        f"https://simplefunctions.dev/api/agent/world?focus={topics}"
    ).text


@tool("search_prediction_markets")
def search_prediction_markets(query: str) -> str:
    """Search for specific prediction market contracts across Kalshi and Polymarket.

    Args:
        query: Natural language query, e.g. 'iran oil', 'fed rate cut', 'bitcoin'.
    """
    import json
    resp = requests.get(
        f"https://simplefunctions.dev/api/public/scan?q={query}&limit=10"
    )
    return json.dumps(resp.json().get("markets", [])[:10], indent=2)


@tool("get_market_detail")
def get_market_detail(ticker: str) -> str:
    """Get detailed data for a specific prediction market contract.

    Includes price, spread, volume, orderbook depth, and related thesis edges.

    Args:
        ticker: Kalshi ticker (e.g. KXIRANINVASION) or Polymarket condition ID.
    """
    import json
    resp = requests.get(
        f"https://simplefunctions.dev/api/public/market/{ticker}?depth=true"
    )
    return json.dumps(resp.json(), indent=2)


# ── Agents ─────────────────────────────────────────────────────────────────────

researcher = Agent(
    role="Macro Research Analyst",
    goal="Analyze geopolitical and economic developments using real-time probability data",
    backstory=SHARED_CONTEXT
    + "\nYou are a senior macro analyst at a global macro fund. You cite specific "
    "probabilities and prices from prediction markets. You never say 'approximately' "
    "when you have exact numbers. You identify the most important risks and opportunities.",
    verbose=True,
)

risk_officer = Agent(
    role="Risk Officer",
    goal="Identify portfolio risks based on current world conditions",
    backstory=SHARED_CONTEXT
    + "\nYou are a risk officer. You flag when probabilities cross thresholds that "
    "matter for portfolio exposure. You reference specific contract prices. You never "
    "say 'could' when you have a specific probability.",
    verbose=True,
)

writer = Agent(
    role="Morning Briefing Writer",
    goal="Produce a concise morning briefing for the investment committee",
    backstory=SHARED_CONTEXT
    + "\nYou write crisp, data-driven briefings for busy portfolio managers. Every "
    "claim has a number attached. No hedging language. No filler. 200 words max.",
    verbose=True,
)


# ── Tasks ──────────────────────────────────────────────────────────────────────

research_task = Task(
    description=(
        "Analyze the current geopolitical and economic situation. Focus on: "
        "1) The top geopolitical risk and its probability, "
        "2) Recession and Fed rate expectations, "
        "3) Energy market conditions. "
        "Use the world state data and search for specific contracts if needed. "
        "Cite every number with its source contract."
    ),
    expected_output="Structured analysis with specific probability citations from prediction markets",
    agent=researcher,
    tools=[get_focused_world_state, search_prediction_markets],
)

risk_task = Task(
    description=(
        "Based on the research analysis, identify the top 3 portfolio risks right now. "
        "For each risk: state the specific prediction market probability, explain why "
        "it matters for portfolio exposure, and recommend one action."
    ),
    expected_output="3 risks with probability levels, portfolio implications, and actions",
    agent=risk_officer,
    tools=[get_focused_world_state, get_market_detail],
    context=[research_task],
)

briefing_task = Task(
    description=(
        "Write a 200-word morning briefing combining the research and risk analysis. "
        "Rules: every sentence must contain a number. No hedging. No filler. "
        "End with the single most important thing the PM should do today."
    ),
    expected_output="200-word morning briefing with data citations",
    agent=writer,
    context=[research_task, risk_task],
)


# ── Crew ───────────────────────────────────────────────────────────────────────

crew = Crew(
    agents=[researcher, risk_officer, writer],
    tasks=[research_task, risk_task, briefing_task],
    verbose=True,
)


if __name__ == "__main__":
    print("Starting world-aware macro crew...")
    print(f"World state loaded: {len(world)} characters\n")
    result = crew.kickoff()
    print("\n" + "=" * 60)
    print("MORNING BRIEFING")
    print("=" * 60)
    print(result)
