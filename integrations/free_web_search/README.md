# Free Web Search Integration with CrewAI (v13.0.0)

This example demonstrates how to use [`free-web-search-ultimate`](https://github.com/wd041216-bit/free-web-search-ultimate) as a zero-cost web search tool within CrewAI agents.

## Why free-web-search-ultimate?

Unlike paid search APIs (Tavily, Brave, Exa, SerpAPI), `free-web-search-ultimate` requires **no API key** and **no subscription**. It supports:

- **Multiple engines**: DuckDuckGo, Bing, Google, Brave, Yahoo
- **Content types**: web pages, news articles, images, videos
- **MCP protocol**: compatible with any MCP-enabled client

## Installation

```bash
pip install crewai free-web-search-ultimate==13.0.0
```

## Usage

```python
from crewai import Agent, Task, Crew
from crewai.tools import tool
from free_web_search_ultimate import UltimateSearcher

searcher = UltimateSearcher()

@tool("Web Search")
def web_search(query: str) -> str:
    """Search the web for up-to-date information. No API key required."""
    results = searcher.search(query, engine="duckduckgo", max_results=5)
    return "\n\n".join([
        f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['snippet']}"
        for r in results
    ])

researcher = Agent(
    role="Research Analyst",
    goal="Find accurate, up-to-date information on any topic",
    backstory="Expert researcher with access to real-time web search",
    tools=[web_search],
    verbose=True
)

research_task = Task(
    description="Research the latest developments in {topic} and provide a comprehensive summary.",
    expected_output="A detailed summary with sources and key findings.",
    agent=researcher
)

crew = Crew(agents=[researcher], tasks=[research_task], verbose=True)
result = crew.kickoff(inputs={"topic": "AI agents in 2025"})
print(result)
```

## MCP Server Usage

You can also use `free-web-search-ultimate` as an MCP server with CrewAI's MCP integration:

```bash
# Start the MCP server
python -m free_web_search_ultimate.server
```

## Links

- **PyPI**: https://pypi.org/project/free-web-search-ultimate/
- **GitHub**: https://github.com/wd041216-bit/free-web-search-ultimate
- **Version**: 13.0.0
