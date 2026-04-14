# CrewAI + Chart Library — Two-Agent Research Crew

Two agents in a sequential crew using Chart Library's cohort primitive:

- **Researcher** calls the data tools (`get_cohort_distribution`,
  `explain_cohort_filters`, `refine_cohort_with_filters`). Produces a
  numeric-only report.
- **Analyst** turns those numbers into a 150-word PM briefing,
  citing sample sizes and disclosing survivorship.

The separation is useful: the researcher has tool access but no
narrative license; the analyst has narrative license but no tool
access. This enforces that every written claim maps back to a real
retrieved number.

## Run

```bash
pip install crewai crewai-tools requests
export OPENAI_API_KEY=sk-...        # CrewAI default; change to taste
export CHART_LIBRARY_KEY=cl_...     # chartlibrary.io/developers
python cohort_research_crew.py NVDA 2024-06-18
```

## Propagate upstream

CrewAI maintains a `crewai-examples` repo and a "marketplace" at
crewai.com. For broader reach:

- Submit to `github.com/crewAIInc/crewAI-examples` under
  `examples/chart_library_research_crew/`
- Consider adding Chart Library as a listed tool in CrewAI's official
  `crewai-tools` package (separate PR)
- Post a tutorial on [crewai.com community](https://community.crewai.com/)
  linking back to chartlibrary.io/developers

## Extend

- Swap researcher's model for a faster one (tool-calling doesn't need a
  frontier model — Claude Haiku or GPT-4o mini works).
- Add a `risk_officer` agent that reads the analyst's briefing and
  calls back to Chart Library for a same-regime drawdown distribution
  before signing off.
- Hook the final output into a trading-advice service that requires
  survivorship disclosure as a pre-flight check.
