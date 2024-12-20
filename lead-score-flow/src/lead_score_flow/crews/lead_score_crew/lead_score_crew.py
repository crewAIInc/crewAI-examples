from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from lead_score_flow.types import CandidateScore


@CrewBase
class LeadScoreCrew:
    """Lead Score Crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def hr_evaluation_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["hr_evaluation_agent"],
            verbose=True,
        )

    @task
    def evaluate_candidate_task(self) -> Task:
        return Task(
            config=self.tasks_config["evaluate_candidate"],
            output_pydantic=CandidateScore,
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Lead Score Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
