from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv

from .tools.agentbay_tools import (
    agentbay_run_code,
    agentbay_create_session,
    agentbay_delete_session,
    agentbay_run_in_session,
    agentbay_write_in_session,
    agentbay_read_in_session,
    agentbay_upload_file,
    agentbay_upload_files,
    agentbay_download_file,
    agentbay_get_link,
)
from .tools.local_tools import (
    save_files_locally,
    verify_http_service,
)

load_dotenv()


@CrewBase
class AgentBayTemporaryCodeCrew:
    """
    Crew for temporary session code execution.

    This crew is designed for simple, one-off code execution tasks.
    Each execution creates a fresh session and cleans up automatically.
    """
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def code_executor(self) -> Agent:
        return Agent(
            config=self.agents_config['code_executor'],  # type: ignore[index]
            tools=[
                agentbay_run_code,  # Temporary session code execution tool
            ],
            allow_delegation=False,
            verbose=True,
        )

    @task
    def run_code_task(self) -> Task:
        return Task(
            config=self.tasks_config['run_code_task'],  # type: ignore[index]
            agent=self.code_executor(),
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.code_executor()],
            tasks=[self.run_code_task()],
            process=Process.sequential,
            verbose=True,
        )


@CrewBase
class AgentBayCodeCrew:
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def code_executor(self) -> Agent:
        return Agent(
            config=self.agents_config['code_executor'],  # type: ignore[index]
            tools=[
                # Persistent session management tools (for full development pipeline)
                agentbay_create_session,
                agentbay_delete_session,
                # In-session operation tools
                agentbay_run_in_session,
                agentbay_write_in_session,
                agentbay_read_in_session,
                # File transfer tools
                agentbay_upload_file,
                agentbay_upload_files,
                agentbay_download_file,
            ],
            allow_delegation=False,
            verbose=True,
        )

    @agent
    def framework_designer(self) -> Agent:
        return Agent(
            config=self.agents_config['framework_designer'],  # type: ignore[index]
            tools=[],
            allow_delegation=False,
            verbose=True,
        )

    @agent
    def implementer(self) -> Agent:
        return Agent(
            config=self.agents_config['implementer'],  # type: ignore[index]
            tools=[
                save_files_locally,  # Save generated files to local filesystem (pure local tool, no AgentBay dependency)
            ],
            allow_delegation=False,
            verbose=True,
        )

    @agent
    def result_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['result_analyst'],  # type: ignore[index]
            tools=[
                agentbay_read_in_session,  # May need to read remote execution result files
                agentbay_get_link,  # Get local-accessible URL for cloud services
                verify_http_service,  # Verify HTTP service response
            ],
            allow_delegation=False,
            verbose=True,
        )

    @task
    def design_project(self) -> Task:
        """Analyze requirements and design project framework."""
        return Task(
            config=self.tasks_config['design_project'],  # type: ignore[index]
            agent=self.framework_designer(),
        )

    @task
    def generate_project(self) -> Task:
        return Task(
            config=self.tasks_config['generate_project'],  # type: ignore[index]
            agent=self.implementer(),
        )

    @task
    def upload_project(self) -> Task:
        return Task(
            config=self.tasks_config['upload_project'],  # type: ignore[index]
            agent=self.code_executor(),
        )

    @task
    def install_and_run(self) -> Task:
        return Task(
            config=self.tasks_config['install_and_run'],  # type: ignore[index]
            agent=self.code_executor(),
        )

    @task
    def analyze_result(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_result'],  # type: ignore[index]
            agent=self.result_analyst(),
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,  # type: ignore[attr-defined]
            tasks=self.tasks,  # type: ignore[attr-defined]
            process=Process.sequential,
            verbose=True,
        )

