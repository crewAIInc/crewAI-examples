# importing the required modules
import logging
import os
from crewai import Agent, Task, Process, Crew
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)

# DuckDuckGo arama aracını tanımlama
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.llms import Ollama

ollama_openhermes = Ollama(model="openhermes")
ollama_llm = ollama_openhermes

# DuckDuckGo arama aracını tanımlama
search_tool = DuckDuckGoSearchRun()

# introduce the agents with their specific roles and goals
researcher = Agent(
  role='Senior Research Analyst',
  goal='Find out details regarding Gradient Descent',
  backstory="""You are an expert in deep learning. 
  You are passionate about education.
  You can explain complex concepts into simple terms.""",
  verbose=True,
  allow_delegation=False,
  tools=[search_tool],
  llm=ollama_llm
)

writer = Agent(
  role='Technical Writer',
  goal='Craft compelling content on Gradient Descent',
  backstory="""You are a renowned Technical Writer, known for
  your informative and insightful articles.
  You transform complex concepts into compelling narratives.""",
  verbose=True,
  allow_delegation=True,
  llm=ollama_llm
)

# Assigning the Tasks
# Create tasks for your agents
task1 = Task(
  description="""Conduct a comprehensive analysis of Gradient Descent.
  Identify key definitions and potential use-cases.
  Your final answer MUST be a full analysis""",
  agent=researcher,
  expected_output=""
)

task2 = Task(
  description="""Using the insights provided, develop a technical blog
  post that highlights the most important aspects of Gradient Descent.
  Your post should be informative yet accessible, catering to a tech-savvy audience.
  Your final answer MUST be the full blog post of at least 4 paragraphs.""",
  agent=writer,
  expected_output=""
)

# Assemble the Crew
# Instantiate your crew with a sequential process
crew = Crew(
  agents=[researcher, writer],
  tasks=[task1, task2],
  verbose=2
)

# Kick Things Off
result = crew.kickoff()
print(result)