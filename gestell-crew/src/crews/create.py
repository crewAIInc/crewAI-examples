from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from typing import List, Optional
from crewai.tools import BaseTool
from pathlib import Path
from crewai_tools import DirectoryReadTool, PDFSearchTool

files_dir = Path.cwd() / "files"


@CrewBase
class GestellCreateCrew:
    """Gestell Crew to Create a Collection and Upload Documents"""

    agents_config = "../../config/crew.yaml"
    tasks_config = "../../config/task.yaml"

    def __init__(self, tools: Optional[List[BaseTool]] = None):
        """Initialize crew with custom tools"""
        super().__init__()
        self.tools = tools or []

    @agent
    def document_analyzer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["document_analyzer_agent"],
            allow_delegation=False,
            verbose=True,
            llm="gpt-4.1-mini",
        )

    @agent
    def collection_planner_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["collection_planner_agent"],
            allow_delegation=False,
            verbose=True,
            llm="gpt-4.1-mini",
        )

    @task
    def analyze_document_task(self) -> Task:
        return Task(
            config=self.tasks_config["analyze_document_task"],
            agent=self.document_analyzer_agent(),
            tools=[DirectoryReadTool(directory=str(files_dir)), PDFSearchTool()],
        )

    @task
    def create_collection_task(self) -> Task:
        create_collection_tools = [
            tool
            for tool in self.tools
            if hasattr(tool, "name")
            and tool.name
            in ["createCollection", "listOrganizations", "listCollections"]
        ]
        return Task(
            config=self.tasks_config["create_collection_task"],
            agent=self.collection_planner_agent(),
            tools=create_collection_tools,
        )

    @task
    def upload_document_task(self) -> Task:
        upload_doc_tool = [
            tool
            for tool in self.tools
            if hasattr(tool, "name")
            and tool.name in ["uploadDocument", "listCollections", "listDocuments"]
        ]
        return Task(
            config=self.tasks_config["upload_document_task"],
            agent=self.document_analyzer_agent(),
            tools=upload_doc_tool,
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
