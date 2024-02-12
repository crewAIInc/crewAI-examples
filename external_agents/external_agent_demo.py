import os
from typing import Any, List
import copy
from uuid import uuid4

from crewai import Agent, Task, Crew
from crewai.agents.langchain_agent import LangchainAgent

from langchain import hub
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent

os.environ["OPENAI_API_KEY"] = ...

# You can delete this block if you don't want to use Langsmith
from langsmith import Client

unique_id = uuid4().hex[0:8]
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = f"Tracing Walkthrough - {unique_id}"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = ...

client = Client()
# End of Langsmith block


search_tool = DuckDuckGoSearchRun()
tools = [DuckDuckGoSearchRun()]

researcher_prompt = hub.pull("hwchase17/openai-tools-agent")
llm = ChatOpenAI(model="gpt-4-0125-preview", temperature=0)

researcher_agent = AgentExecutor(
    agent=create_openai_tools_agent(llm, tools, researcher_prompt),
    tools=tools,
    verbose=True,
)
writer_agent = AgentExecutor(
    agent=create_openai_tools_agent(llm, [], researcher_prompt), tools=[], verbose=True
)

researcher = LangchainAgent(
    agent=researcher_agent,
    tools=[search_tool],
    role="Senior Research Analyst",
    allow_delegation=False,
)

writer = LangchainAgent(
    agent=writer_agent,
    role="Tech Content Strategist",
    allow_delegation=True,
)

# From here onwards it's exactly like the original example

# Create tasks for your agents
task1 = Task(
    description="""Conduct a comprehensive analysis of the latest advancements in AI in 2024.
  Identify key trends, breakthrough technologies, and potential industry impacts.
  Your final answer MUST be a full analysis report""",
    agent=researcher,
)

task2 = Task(
    description="""Using the insights provided, develop an engaging blog
  post that highlights the most significant AI advancements.
  Your post should be informative yet accessible, catering to a tech-savvy audience.
  Make it sound cool, avoid complex words so it doesn't sound like AI.
  Your final answer MUST be the full blog post of at least 4 paragraphs.""",
    agent=writer,
)

# Instantiate your crew with a sequential process
crew = Crew(
    agents=[researcher, writer],
    tasks=[task1, task2],
    verbose=2,  # You can set it to 1 or 2 to different logging levels
)

# Get your crew to work!
result = crew.kickoff()

print("######################")
print(result)
