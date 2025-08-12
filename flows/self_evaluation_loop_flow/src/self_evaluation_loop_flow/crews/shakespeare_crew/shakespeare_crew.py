from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from self_evaluation_loop_flow.tools.CharacterCounterTool import CharacterCounterTool


@CrewBase
class ShakespeareanXPostCrew:
    """Shakespearean X Post Crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def shakespearean_bard(self) -> Agent:
        return Agent(
            config=self.agents_config["shakespearean_bard"],
            tools=[CharacterCounterTool()],
        )

    @task
    def write_x_post(self) -> Task:
        return Task(
            config=self.tasks_config["write_x_post"],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Shakespearean X Post Crew"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )
