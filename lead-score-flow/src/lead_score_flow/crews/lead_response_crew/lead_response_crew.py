from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class LeadResponseCrew:
    """Lead Response Crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def email_followup_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["email_followup_agent"],
            verbose=True,
            allow_delegation=False,
        )

    @task
    def send_followup_email_task(self) -> Task:
        return Task(
            config=self.tasks_config["send_followup_email"],
            verbose=True,
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Lead Response Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
