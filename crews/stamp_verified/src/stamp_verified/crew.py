"""Trust-verified agent crew using AgentStamp for identity verification."""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from stamp_verified.tools.trust_check_tool import AgentStampTrustCheckTool


@CrewBase
class StampVerifiedCrew:
    """A crew that verifies agent trust before task coordination.

    Demonstrates how to integrate AgentStamp trust checks into a
    multi-agent workflow — agents are verified before they participate.
    """

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def trust_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["trust_analyst"],
            tools=[AgentStampTrustCheckTool()],
            verbose=True,
            memory=False,
        )

    @agent
    def task_coordinator(self) -> Agent:
        return Agent(
            config=self.agents_config["task_coordinator"],
            verbose=True,
            memory=False,
        )

    @task
    def verify_agent_trust(self) -> Task:
        return Task(
            config=self.tasks_config["verify_agent_trust"],
            agent=self.trust_analyst(),
        )

    @task
    def coordinate_verified_task(self) -> Task:
        return Task(
            config=self.tasks_config["coordinate_verified_task"],
            agent=self.task_coordinator(),
            context=[self.verify_agent_trust()],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the StampVerified crew."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
