import sys
from crewai import Agent, Task
import os
from dotenv import load_dotenv
from crewai import Crew, Process

from langchain_openai import AzureChatOpenAI

os.environ.clear()
load_dotenv()

default_llm = AzureChatOpenAI(
    openai_api_version=os.environ.get("AZURE_OPENAI_VERSION", "2023-07-01-preview"),
    azure_deployment=os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt35"),
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT", "https://<your-endpoint>.openai.azure.com/"),
    api_key=os.environ.get("AZURE_OPENAI_KEY")
)


# Create a researcher agent
researcher = Agent(
  role='Senior Researcher',
  goal='Discover groundbreaking technologies',
  verbose=True,
  backstory='A curious mind fascinated by cutting-edge innovation and the potential to change the world, you know everything about tech.'
)

# Create a writer agent
writer = Agent(
  role='Writer',
  goal='Craft compelling stories about tech discoveries',
  verbose=True,
  backstory='A creative soul who translates complex tech jargon into engaging narratives for the masses, you write using simple words in a friendly and inviting tone that does not sounds like AI.'
)


# Task for the researcher
research_task = Task(
  description='Identify the next big trend in AI',
  agent=researcher  # Assigning the task to the researcher
)

# Task for the writer
write_task = Task(
  description='Write an article on AI advancements leveraging the research made.',
  agent=writer  # Assigning the task to the writer
)

# Instantiate your crew
tech_crew = Crew(
  agents=[researcher, writer],
  tasks=[research_task, write_task],
  process=Process.sequential  # Tasks will be executed one after the other
)

# Begin the task execution
tech_crew.kickoff()