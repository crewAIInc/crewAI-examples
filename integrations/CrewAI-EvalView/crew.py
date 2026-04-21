"""Example CrewAI crew for EvalView regression testing.

A simple research + writing crew that demonstrates tool-calling agents.
Replace this with your own crew definition.
"""
from __future__ import annotations

from crewai import Agent, Crew, Task, Process
from crewai.tools import tool


@tool("search_web")
def search_web(query: str) -> str:
    """Search the web for information about a topic."""
    # In production, this would call a real search API
    return (
        f"Search results for '{query}':\n"
        "1. Renewable energy capacity grew 50% in 2025\n"
        "2. Solar costs dropped below $20/MWh in major markets\n"
        "3. Battery storage deployments doubled year-over-year"
    )


@tool("summarize_text")
def summarize_text(text: str) -> str:
    """Summarize a long text into key bullet points."""
    # In production, this would use an LLM or extraction logic
    return f"Summary of input ({len(text)} chars): Key trends identified."


researcher = Agent(
    role="Research Analyst",
    goal="Find accurate, up-to-date information on the given topic",
    backstory=(
        "You are a meticulous research analyst who always verifies "
        "information using search tools before drawing conclusions."
    ),
    tools=[search_web],
    verbose=False,
)

writer = Agent(
    role="Content Writer",
    goal="Write clear, well-structured reports based on research findings",
    backstory=(
        "You are an experienced writer who turns research data into "
        "readable, actionable reports."
    ),
    tools=[summarize_text],
    verbose=False,
)

research_task = Task(
    description="Research {topic} and provide key findings with sources",
    expected_output="A detailed summary of findings with key data points",
    agent=researcher,
)

writing_task = Task(
    description="Write a concise report based on the research findings about {topic}",
    expected_output="A well-structured report with introduction, key findings, and conclusion",
    agent=writer,
)

crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
    process=Process.sequential,
    verbose=False,
)
