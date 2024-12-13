from typing import List
from crewai import Agent, Crew, Process, Task
from crewai import LLM
from crewai.project import CrewBase, agent, crew, task
from marketing_posts_e2e_eval.marketing_crew.reflection import ReflectionTask
from marketing_posts_e2e_eval.marketing_crew.reflection import Feedback as ReflectionFeedback

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

llm = LLM(
    model="azure/sfc-cortex-analyst-dev",
    api_version="AZURE_API_VERSION=2023-07-01-preview",
)

@CrewBase
class MarketingPostsCrew():
	"""MarketingPosts crew"""
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	@agent
	def lead_market_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['lead_market_analyst'],
			tools=[SerperDevTool(), ScrapeWebsiteTool()],
			verbose=False,
			memory=False,
            llm='azure/sfc-cortex-analyst-dev',
		)

	@agent
	def chief_marketing_strategist(self) -> Agent:
		return Agent(
			config=self.agents_config['chief_marketing_strategist'],
			tools=[SerperDevTool(), ScrapeWebsiteTool()],
			verbose=True,
			memory=False,
            llm='azure/sfc-cortex-analyst-dev',
		)

	@agent
	def creative_content_creator(self) -> Agent:
		return Agent(
			config=self.agents_config['creative_content_creator'],
			verbose=True,
			memory=False,
            llm='azure/sfc-cortex-analyst-dev',
		)
	
	@agent
	def reflection_agent(self) -> Agent:
		return Agent(
			role="Super Supervisor",
			goal="You give highly insightful and useful advice to elevate the quality of results from your team.",
			backstory="You're a team enabler and have a keen eye for detail and a strong understanding of what makes marketing engaging and effective.",
			allow_delegation=False,
			verbose=True,
			tools=None,
		)
	
	@task
	def research_task(self) -> Task:
		return Task(
			config=self.tasks_config['research_task'],
			agent=self.lead_market_analyst()
		)

	@task
	def project_understanding_task(self) -> Task:
		return ReflectionTask(
			config=self.tasks_config['project_understanding_task'],
			agent=self.chief_marketing_strategist(),
			reflection_task=Task(
				config=self.tasks_config['project_understanding_reflection_task'],
				output_json=ReflectionFeedback
			),
			reflection_agent=self.reflection_agent()
		)

	@task
	def marketing_strategy_task(self) -> Task:
		return ReflectionTask(
			config=self.tasks_config['marketing_strategy_task'],
			agent=self.chief_marketing_strategist(),
			output_json=MarketStrategy,
			reflection_task=Task(
				config=self.tasks_config['marketing_strategy_reflection_task'],
				output_json=ReflectionFeedback
			),
			reflection_agent=self.reflection_agent()
		)

	@task
	def campaign_idea_task(self) -> Task:
		return ReflectionTask(
			config=self.tasks_config['campaign_idea_task'],
			agent=self.creative_content_creator(),
   			output_json=CampaignIdea,
			reflection_task=Task(
				config=self.tasks_config['campaign_idea_reflection_task'],
				output_json=ReflectionFeedback
			),
			reflection_agent=self.reflection_agent()
		)

	@task
	def copy_creation_task(self) -> Task:
		return ReflectionTask(
			config=self.tasks_config['copy_creation_task'],
			agent=self.creative_content_creator(),
   			context=[self.marketing_strategy_task(), self.campaign_idea_task()],
			output_json=Copy,
			reflection_task=Task(
				config=self.tasks_config['copy_creation_reflection_task'],
				output_json=ReflectionFeedback
			),
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
