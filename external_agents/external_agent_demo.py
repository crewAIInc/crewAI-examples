import os

from uuid import uuid4

from crewai import Agent, Task, Crew
from openai_tools_agent import OpenAIToolsAgent

from langchain import hub
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_openai import ChatOpenAI

os.environ["OPENAI_API_KEY"] = ...

# You can delete this block if you don't want to use Langsmith
unique_id = uuid4().hex[0:8]
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = f"Tracing Walkthrough - {unique_id}"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = ...
from langsmith import Client

client = Client()
# End of Langsmith block


search_tool = DuckDuckGoSearchRun()

prompt = hub.pull("hwchase17/openai-tools-agent")
prompt2 = hub.pull("hwchase17/react-json")
prompt3 = hub.pull("cpatrickalves/react-chat-agent")

llm = ChatOpenAI(model="gpt-4-0125-preview", temperature=0)
researcher = OpenAIToolsAgent(
    llm=llm, prompt=prompt, tools=[search_tool], role="Senior Research Analyst"
)

writer = Agent(
    role="Tech Content Strategist",
    goal="Craft compelling content on tech advancements",
    backstory="""You are a renowned Content Strategist, known for your insightful and engaging articles.
  You transform complex concepts into compelling narratives.""",
    verbose=True,
    allow_delegation=True,
)

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
    tasks=[task2],
    verbose=2,  # You can set it to 1 or 2 to different logging levels
)

# Get your crew to work!
result = crew.kickoff()

print("######################")
print(result)
