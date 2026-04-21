from typing import List

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, WebsiteSearchTool, FileReadTool
from pydantic import BaseModel, Field
from kalibr.integrations.crewai import KalibrCrewAIInstrumentor

import os

KalibrCrewAIInstrumentor(
    tenant_id=os.environ.get("KALIBR_TENANT_ID", ""),
    goal="job_posting_production",
).instrument()

web_search_tool = WebsiteSearchTool()
serper_dev_tool = SerperDevTool()
file_read_tool = FileReadTool(
    file_path='job_description_example.md',
    description='A tool to read the job description example file.',
)


class ResearchRoleRequirements(BaseModel):
    skills: List[str] = Field(..., description="List of recommended skills for the ideal candidate.")
    experience: List[str] = Field(..., description="List of recommended experience for the ideal candidate.")
    qualities: List[str] = Field(..., description="List of recommended qualities for the ideal candidate.")


@CrewBase
class KalibrResilientJobPostingCrew:
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def research_agent(self) -> Agent:
        return Agent(config=self.agents_config['research_agent'], tools=[web_search_tool, serper_dev_tool], verbose=True)

    @agent
    def writer_agent(self) -> Agent:
        return Agent(config=self.agents_config['writer_agent'], tools=[web_search_tool, serper_dev_tool, file_read_tool], verbose=True)

    @agent
    def review_agent(self) -> Agent:
        return Agent(config=self.agents_config['review_agent'], tools=[web_search_tool, serper_dev_tool, file_read_tool], verbose=True)

    @task
    def research_company_culture_task(self) -> Task:
        return Task(config=self.tasks_config['research_company_culture_task'], agent=self.research_agent())

    @task
    def research_role_requirements_task(self) -> Task:
        return Task(config=self.tasks_config['research_role_requirements_task'], agent=self.research_agent(), output_json=ResearchRoleRequirements)

    @task
    def draft_job_posting_task(self) -> Task:
        return Task(config=self.tasks_config['draft_job_posting_task'], agent=self.writer_agent())

    @task
    def review_and_edit_job_posting_task(self) -> Task:
        return Task(config=self.tasks_config['review_and_edit_job_posting_task'], agent=self.review_agent())

    @task
    def industry_analysis_task(self) -> Task:
        return Task(config=self.tasks_config['industry_analysis_task'], agent=self.research_agent())

    @crew
    def crew(self) -> Crew:
        return Crew(agents=self.agents, tasks=self.tasks, process=Process.sequential, verbose=True)
