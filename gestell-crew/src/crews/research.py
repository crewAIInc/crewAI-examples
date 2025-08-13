from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from typing import List, Optional
from crewai.tools import BaseTool


@CrewBase
class GestellResearchCrew:
    """Gestell Crew to Conduct Research"""

    agents_config = "../../config/crew.yaml"
    tasks_config = "../../config/task.yaml"

    def __init__(self, tools: Optional[List[BaseTool]] = None):
        """Initialize crew with custom tools"""
        super().__init__()
        # Use provided tools or default to empty list
        self.tools = tools or []

    @agent
    def research_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["research_agent"],
            allow_delegation=False,
            verbose=True,
            tools=self.tools,
            llm="gpt-4.1-mini",
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config["research_task"],
            agent=self.research_agent(),
        )

    @crew
    def crew(self) -> Crew:
        """Creates the GestellCrew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
