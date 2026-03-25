"""
Example: CrewAI crew with three-layer security gate.

Before running:
    cp .env.example .env
    # Fill in your API keys in .env
    uv sync
    uv run main.py
"""

from dotenv import load_dotenv
load_dotenv()

from crewai import Agent, Task, Crew
from security_gate import security_gate


# Define agents
researcher = Agent(
    role="Researcher",
    goal="Find accurate information on the given topic",
    backstory="You are a thorough researcher who verifies sources.",
)

writer = Agent(
    role="Writer",
    goal="Write a clear summary based on the research",
    backstory="You are a concise technical writer.",
)

# Define tasks
research_task = Task(
    description="Research the topic: {topic}",
    expected_output="A list of key findings with sources.",
    agent=researcher,
)

write_task = Task(
    description="Write a summary based on the research findings.",
    expected_output="A clear 2-3 paragraph summary.",
    agent=writer,
)

# Create crew with security gate
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    before_kickoff_callbacks=[security_gate],
)

if __name__ == "__main__":
    # Without attestation: gate passes (both keys optional)
    result = crew.kickoff(inputs={"topic": "open standards for AI agent identity"})
    print(result)

    # With attestation: gate verifies runtime before crew runs
    # result = crew.kickoff(inputs={
    #     "topic": "open standards for AI agent identity",
    #     "runtime_attestation": "<JWT from your runtime>",
    #     "audience": "https://your-crew.com",
    # })
