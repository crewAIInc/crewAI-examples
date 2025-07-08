import sys
from crewai import Agent, Task
import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM

load_dotenv()

default_llm = LLM(
    model=os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o"),
    api_version=os.environ.get("AZURE_OPENAI_VERSION", "2024-10-21"),
    api_key=os.environ.get("AZURE_OPENAI_KEY"),
    base_url=os.environ.get("AZURE_OPENAI_ENDPOINT", "https://<your-endpoint>.openai.azure.com/")
)


# Create a researcher agent
researcher = Agent(
  role='Senior Researcher',
  goal='Discover groundbreaking technologies',
  verbose=True,
  llm=default_llm,
  backstory='A curious mind fascinated by cutting-edge innovation and the potential to change the world, you know everything about tech.'
)

# Task for the researcher
research_task = Task(
  description='Identify the next big trend in AI',
  expected_output='5 paragraphs on the next big AI trend',
  agent=researcher  # Assigning the task to the researcher
)


# Instantiate your crew
tech_crew = Crew(
  agents=[researcher],
  tasks=[research_task],
  process=Process.sequential  # Tasks will be executed one after the other
)

# Begin the task execution
tech_crew.kickoff()
