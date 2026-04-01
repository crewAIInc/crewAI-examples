"""
Free Web Search + CrewAI Example (v13.0.0)
Zero-cost, API-key-free web search for CrewAI agents.
"""

from crewai import Agent, Task, Crew
from crewai.tools import tool
from free_web_search_ultimate import UltimateSearcher

searcher = UltimateSearcher()


@tool("Web Search")
def web_search(query: str) -> str:
    """Search the web for up-to-date information using free-web-search-ultimate.
    
    No API key required. Supports DuckDuckGo, Bing, Google, Brave, Yahoo.
    
    Args:
        query: The search query string.
        
    Returns:
        Formatted search results with titles, URLs, and snippets.
    """
    results = searcher.search(query, engine="duckduckgo", max_results=5)
    if not results:
        return "No results found."
    return "\n\n".join([
        f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['snippet']}"
        for r in results
    ])


@tool("News Search")
def news_search(query: str) -> str:
    """Search for recent news articles using free-web-search-ultimate.
    
    Args:
        query: The news search query.
        
    Returns:
        Formatted news results with titles, URLs, and publication dates.
    """
    results = searcher.search_news(query, max_results=5)
    if not results:
        return "No news found."
    return "\n\n".join([
        f"[{r.get('date', 'N/A')}] {r['title']}\nURL: {r['url']}"
        for r in results
    ])


researcher = Agent(
    role="Research Analyst",
    goal="Find accurate, up-to-date information using free web search",
    backstory=(
        "You are an expert researcher with access to real-time web search. "
        "You use free-web-search-ultimate to find information without any API costs."
    ),
    tools=[web_search, news_search],
    verbose=True,
)

research_task = Task(
    description=(
        "Research the latest developments in {topic}. "
        "Use web search to find current information and news. "
        "Provide a comprehensive summary with sources."
    ),
    expected_output=(
        "A detailed 3-paragraph summary with key findings, "
        "recent developments, and relevant source URLs."
    ),
    agent=researcher,
)

crew = Crew(
    agents=[researcher],
    tasks=[research_task],
    verbose=True,
)

if __name__ == "__main__":
    result = crew.kickoff(inputs={"topic": "AI agents and MCP protocol in 2025"})
    print("\n=== Research Result ===")
    print(result)
