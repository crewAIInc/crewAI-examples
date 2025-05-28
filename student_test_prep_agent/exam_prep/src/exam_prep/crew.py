from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv
from .tools.youtube_tool import YouTubeTool

load_dotenv()

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class ExamPrep():
    """ExamPrep crew"""

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def input_interpreter(self) -> Agent:
        return Agent(
            config=self.agents_config['input_interpreter'],
            verbose=True
        )

    @agent
    def schedule_builder(self) -> Agent:
        return Agent(
            config=self.agents_config['schedule_builder'],
            verbose=True
        )

    @agent
    def strategy_planner(self) -> Agent:
        return Agent(
            config=self.agents_config['strategy_planner'],
            verbose=True
        )
    
    @agent
    def youtube_fetcher(self) -> Agent:
        return Agent(
            config=self.agents_config['youtube_fetcher'],
            tools=[YouTubeTool()],
            verbose=True
        )
    
    @agent
    def output_formatter(self) -> Agent:
        return Agent(
            config=self.agents_config['output_formatter'],
            verbose=True
        )
    
    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def extract_exam_info(self) -> Task:
        return Task(
            config=self.tasks_config['extract_exam_info'],
        )
    
    @task
    def build_schedule(self) -> Task:
        return Task(
            config=self.tasks_config['build_schedule'],
        )
    
    @task
    def build_strategy(self) -> Task:
        return Task(
            config=self.tasks_config['build_strategy'],
        )
    
    @task
    def fetch_youtube_videos(self) -> Task:
        return Task(
            config=self.tasks_config['fetch_youtube_videos'],
        )
    
    @task
    def format_output(self) -> Task:
        return Task(
            config=self.tasks_config['format_output'],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the ExamPrep crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
