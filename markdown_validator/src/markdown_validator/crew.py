from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from markdown_validator.tools.markdownTools import markdown_validation_tool


@CrewBase
class MarkDownValidatorCrew():
    """MarkDownValidatorCrew crew"""
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def RequirementsManager(self) -> Agent:
        return Agent(
            config=self.agents_config['Requirements_Manager'],
            tools=[markdown_validation_tool],
            allow_delegation=False,
            verbose=False
        )

    @task
    def syntax_review_task(self) -> Task:
        return Task(
            config=self.tasks_config['syntax_review_task'],
            agent=self.RequirementsManager()
        )

    @crew
    def crew(self) -> Crew:
        """Creates the MarkDownValidatorCrew crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=False,
        )
