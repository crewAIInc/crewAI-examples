from typing import List, Optional
from crewai import Agent, Crew, Process, Task
from crewai import LLM
from crewai.project import CrewBase, agent, crew, task

# Uncomment the following line to use an example of a custom tool
# from marketing_posts.tools.custom_tool import MyCustomTool

# Check our tools documentations for more information on how to use them
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from pydantic import BaseModel, Field

from trulens.apps.custom import instrument

from crewai.crew import Crew
from crewai.agent import Agent
from crewai.task import Task
from crewai.agents.crew_agent_executor import CrewAgentExecutor

llm = LLM(
    model="azure/sfc-cortex-analyst-dev",
    api_version="AZURE_API_VERSION=2023-07-01-preview",
)


class MarketingPostVerification(BaseModel):
    quality: Optional[int]
    feedback: Optional[str]


# Instrument some Crew class methods:
instrument.method(Crew, "kickoff")
instrument.method(Crew, "kickoff_async")
instrument.method(Crew, "train")
instrument.method(Agent, "execute_task")
instrument.method(Task, "execute_sync")
instrument.method(Task, "execute_async")
instrument.method(Task, "_execute_core")
instrument.method(CrewAgentExecutor, "invoke")


@CrewBase
class EvaluatorCrew():
    """e2e evaluator"""
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def quality_evaluator_reviewer(self) -> Agent:
        return Agent(
            config=self.agents_config['quality_evalutor_reviewer'],
            tools=[SerperDevTool(), ScrapeWebsiteTool()],
            verbose=True,
            memory=False,
            llm='azure/sfc-cortex-analyst-dev',
        )

    @task
    def verify_marketing_post_task(self) -> Task:
        return Task(
            config=self.tasks_config['verify_marketing_post'],
            output_pydantic=MarketingPostVerification,
            agent=self.quality_evaluator_reviewer(),
        )

    @crew
    def crew(self) -> Crew:
        """Creates the marketing post eval crew"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
