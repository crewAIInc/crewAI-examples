"""
CrewAI + Arch Tools: Give your AI agents 58+ real-world API tools

This example builds a research agent with web scraping, search, and crypto
data — all powered by Arch Tools (https://archtools.dev).

Setup:
    pip install crewai arch-tools
    export ARCH_TOOLS_API_KEY=arch_your_key_here
    export OPENAI_API_KEY=sk-...
    python main.py
"""

import os
from crewai import Agent, Task, Crew, LLM
from crewai.tools import BaseTool
from arch_tools import ArchTools

# --- Initialize Arch Tools client ---
arch = ArchTools(api_key=os.environ["ARCH_TOOLS_API_KEY"])


# --- Define tools that wrap Arch Tools endpoints ---

class WebScrapeTool(BaseTool):
    name: str = "web_scraper"
    description: str = "Scrape and extract text content from any URL. Input: a valid URL string."

    def _run(self, url: str) -> str:
        result = arch.web_scrape(url)
        return result.get("text", result.get("markdown", str(result)))[:5000]


class WebSearchTool(BaseTool):
    name: str = "web_search"
    description: str = "Search the web for any query. Input: a search query string."

    def _run(self, query: str) -> str:
        result = arch.search_web(query, limit=5)
        results = result.get("results", [])
        if not results:
            return f"No results found for: {query}"
        lines = []
        for r in results[:5]:
            title = r.get("title", "Untitled")
            url = r.get("url", "")
            snippet = r.get("snippet", "")
            lines.append(f"• {title}\n  {url}\n  {snippet}")
        return "\n\n".join(lines)


class CryptoPriceTool(BaseTool):
    name: str = "crypto_price"
    description: str = "Get the current price for a cryptocurrency. Input: symbol like 'bitcoin' or 'ethereum'."

    def _run(self, symbol: str) -> str:
        result = arch.crypto_price(symbol)
        return str(result)


class SentimentTool(BaseTool):
    name: str = "sentiment_analysis"
    description: str = "Analyze the sentiment of a text passage. Input: text to analyze."

    def _run(self, text: str) -> str:
        result = arch.sentiment_analysis(text)
        return str(result)


class SummarizeTool(BaseTool):
    name: str = "text_summarizer"
    description: str = "Summarize a long text into bullet points. Input: text to summarize."

    def _run(self, text: str) -> str:
        result = arch.summarize(text, style="bullets")
        return result.get("summary", str(result))


# --- Build the agent ---

researcher = Agent(
    role="Research Analyst",
    goal="Gather and synthesize information from multiple web sources, "
         "including live market data and sentiment analysis",
    backstory=(
        "You are an expert research analyst with access to web scraping, "
        "search engines, cryptocurrency data, and NLP tools. You gather "
        "information methodically, cross-reference sources, and produce "
        "clear, actionable reports."
    ),
    tools=[
        WebScrapeTool(),
        WebSearchTool(),
        CryptoPriceTool(),
        SentimentTool(),
        SummarizeTool(),
    ],
    llm=LLM(model="gpt-4o"),
    verbose=True,
)

# --- Define the task ---

task = Task(
    description=(
        "Research the current state of AI agent tooling and crypto payments. "
        "Do the following:\n"
        "1. Search the web for 'AI agent tools API 2026'\n"
        "2. Scrape https://archtools.dev to understand what Arch Tools offers\n"
        "3. Get the current Bitcoin and Ethereum prices\n"
        "4. Analyze the sentiment of the scraped content\n"
        "5. Compile a concise research report with your findings"
    ),
    expected_output=(
        "A structured research report with sections: "
        "AI Agent Tooling Landscape, Arch Tools Overview, "
        "Crypto Market Snapshot, and Key Takeaways"
    ),
    agent=researcher,
)

# --- Run the crew ---

if __name__ == "__main__":
    crew = Crew(
        agents=[researcher],
        tasks=[task],
        verbose=True,
    )
    result = crew.kickoff()
    print("\n" + "=" * 60)
    print("RESEARCH REPORT")
    print("=" * 60)
    print(result)
