"""KYB Compliance Verification Crew using Strale for company data and screening."""

import os
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_strale import StraleToolkit


@CrewBase
class KybComplianceCrew:
    """KYB (Know Your Business) compliance verification crew.

    Uses Strale tools to:
    - Look up company registry data across 27 countries
    - Validate EU VAT numbers via VIES
    - Screen against sanctions lists (OFAC, EU, UN, UK)
    - Check PEP (Politically Exposed Persons) databases
    - Scan adverse media coverage

    Produces a structured KYB verification report with a risk assessment.

    Requirements:
        pip install crewai-strale
        export STRALE_API_KEY=sk_live_...  # get at https://strale.dev/signup
    """

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self):
        self.strale_toolkit = StraleToolkit(
            api_key=os.environ.get("STRALE_API_KEY", ""),
        )
        self.strale_tools = self.strale_toolkit.get_tools()

    @agent
    def company_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["company_researcher"],
            tools=self.strale_tools,
            verbose=True,
        )

    @agent
    def compliance_screener(self) -> Agent:
        return Agent(
            config=self.agents_config["compliance_screener"],
            tools=self.strale_tools,
            verbose=True,
        )

    @agent
    def report_writer(self) -> Agent:
        return Agent(
            config=self.agents_config["report_writer"],
            verbose=True,
        )

    @task
    def company_lookup(self) -> Task:
        return Task(config=self.tasks_config["company_lookup"])

    @task
    def compliance_screening(self) -> Task:
        return Task(config=self.tasks_config["compliance_screening"])

    @task
    def kyb_report(self) -> Task:
        return Task(config=self.tasks_config["kyb_report"])

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
