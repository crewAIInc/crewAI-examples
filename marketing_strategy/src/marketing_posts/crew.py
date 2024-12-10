from typing import List
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from marketing_posts.reflection import ReflectionTask

# Uncomment the following line to use an example of a custom tool
# from marketing_posts.tools.custom_tool import MyCustomTool

# Check our tools documentations for more information on how to use them
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from pydantic import BaseModel, Field

class MarketStrategy(BaseModel):
	"""Market strategy model"""
	name: str = Field(..., description="Name of the market strategy")
	tatics: List[str] = Field(..., description="List of tactics to be used in the market strategy")
	channels: List[str] = Field(..., description="List of channels to be used in the market strategy")
	KPIs: List[str] = Field(..., description="List of KPIs to be used in the market strategy")

class CampaignIdea(BaseModel):
	"""Campaign idea model"""
	name: str = Field(..., description="Name of the campaign idea")
	description: str = Field(..., description="Description of the campaign idea")
	audience: str = Field(..., description="Audience of the campaign idea")
	channel: str = Field(..., description="Channel of the campaign idea")

class Copy(BaseModel):
	"""Copy model"""
	title: str = Field(..., description="Title of the copy")
	body: str = Field(..., description="Body of the copy")

@CrewBase
class MarketingPostsCrew():
	"""MarketingPosts crew"""
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	@agent
	def reflection_agent(self) -> Agent:
		return Agent(
			role="Critical Reviewer",
			goal="Provide critical feedback on the quality of the content. Give a 0 - 3 scale rating and actionable feedback.",
			backstory="You're a senior consultant and critical reviewer of work. You have a keen eye for detail and a strong understanding of what makes content engaging and effective.",
			allow_delegation=False,
			verbose=True,
		)

	@agent
	def lead_market_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['lead_market_analyst'],
			tools=[SerperDevTool(), ScrapeWebsiteTool()],
			verbose=True,
			memory=False,
		)

	@agent
	def chief_marketing_strategist(self) -> Agent:
		return Agent(
			config=self.agents_config['chief_marketing_strategist'],
			tools=[SerperDevTool(), ScrapeWebsiteTool()],
			verbose=True,
			memory=False,
		)

	@agent
	def creative_content_creator(self) -> Agent:
		return Agent(
			config=self.agents_config['creative_content_creator'],
			verbose=True,
			memory=False,
		)

	@task
	def research_task(self) -> Task:
		return ReflectionTask(
			config=self.tasks_config['research_task'],
			agent=self.lead_market_analyst(),
			reflection_agent=self.reflection_agent()
		)

	@task
	def project_understanding_task(self) -> Task:
		return ReflectionTask(
			config=self.tasks_config['project_understanding_task'],
			agent=self.chief_marketing_strategist(),
			reflection_agent=self.reflection_agent()
		)

	@task
	def marketing_strategy_task(self) -> Task:
		return ReflectionTask(
			config=self.tasks_config['marketing_strategy_task'],
			agent=self.chief_marketing_strategist(),
			output_json=MarketStrategy,
			reflection_agent=self.reflection_agent()
		)

	@task
	def campaign_idea_task(self) -> Task:
		return ReflectionTask(
			config=self.tasks_config['campaign_idea_task'],
			agent=self.creative_content_creator(),
   			output_json=CampaignIdea,
			reflection_agent=self.reflection_agent()
		)

	@task
	def copy_creation_task(self) -> Task:
		return ReflectionTask(
			config=self.tasks_config['copy_creation_task'],
			agent=self.creative_content_creator(),
   			context=[self.marketing_strategy_task(), self.campaign_idea_task()],
			output_json=Copy,
			reflection_agent=self.reflection_agent()
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the MarketingPosts crew"""
		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)
