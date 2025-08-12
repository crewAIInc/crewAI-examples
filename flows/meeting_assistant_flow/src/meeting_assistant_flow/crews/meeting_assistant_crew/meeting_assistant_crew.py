from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from langchain_openai import ChatOpenAI

from meeting_assistant_flow.types import (
    MeetingTaskList,
)


@CrewBase
class MeetingAssistantCrew:
    """Meeting Assistant Crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    llm = ChatOpenAI(model="gpt-4")

    @agent
    def meeting_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config["meeting_analyzer"],
            llm=self.llm,
        )

    @task
    def analyze_meeting(self) -> Task:
        return Task(
            config=self.tasks_config["analyze_meeting"],
            output_pydantic=MeetingTaskList,
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Meeting Issue Generation Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
