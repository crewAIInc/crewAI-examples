from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from linkedin_post_automater.tools.linkedin_post_tool import LinkedInImagePostTool
from linkedin_post_automater.tools.news_tool import RealTimeNewsSearchTool
from linkedin_post_automater.tools.image_genaration_tool import GeminiImageGenerator
from typing import List
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class LinkedinPostAutomater():
    """LinkedinPostAutomater crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools

    @agent
    def News_Article_Researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['News_Article_Researcher'],  # type: ignore[index]
            verbose=True ,
            tools = [RealTimeNewsSearchTool()]
        )


    @agent
    def Planner_and_Researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['Planner_and_Researcher'],  # type: ignore[index]
            verbose=True ,
            tools = [GeminiImageGenerator()]
        )

    @agent
    def Article_Maker_and_LinkedIn_Poster(self) -> Agent:
        return Agent(
            config=self.agents_config['Article_Maker_and_LinkedIn_Poster'], # type: ignore[index]
            verbose=True,
            tools = [LinkedInImagePostTool()]
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def News_Article_Researcher_Task(self) -> Task:
        return Task(
            config=self.tasks_config['News_Article_Researcher_Task'],  # type: ignore[index]
            output_file = "news.md"
        )

    @task
    def Planner_and_Researcher_Task(self) -> Task:
        return Task(
            config=self.tasks_config['Planner_and_Researcher_Task'],  # type: ignore[index]
        )

    @task
    def Article_Maker_and_LinkedIn_Poster_Task(self) -> Task:
        return Task(
            config=self.tasks_config['Article_Maker_and_LinkedIn_Poster_Task'], # type: ignore[index]
            output_file='report.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the LinkedinPostAutomater crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
