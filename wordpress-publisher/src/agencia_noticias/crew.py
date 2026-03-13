from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
import os

# Uncomment the following line to use an example of a custom tool
# from agencia_noticias.tools.custom_tool import MyCustomTool

from crewai_tools import ScrapeWebsiteTool
from crewai_tools import SerperDevTool

# Adicionar a ferramenta para publicar no WordPress
# Assumindo que você tem uma ferramenta personalizada chamada WordPressPublishTool
from agencia_noticias.tools.wp_publisher import WordPressPublishTool

scrape_tool = ScrapeWebsiteTool()
search_tool = SerperDevTool()

wordpress_tool = WordPressPublishTool(
	blog_url="https://your-website.com/",  # URL do seu blog WordPress
    token=os.getenv('BLOG_API')  # Token JWT ou credenciais de API
)  # Ferramenta personalizada para publicação no WordPress

@CrewBase
class AgenciaNoticiasCrew():
	"""AgenciaNoticias crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	@agent
	def researcher(self) -> Agent:
		return Agent(
			config=self.agents_config['researcher'],
			tools=[
				scrape_tool,
				search_tool
			],
			verbose=True
		)

	@agent
	def reporting_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['reporting_analyst'],
			verbose=True
		)

	@agent
	def translator(self) -> Agent:
		return Agent(
			config=self.agents_config['translator'],
			verbose=True
		)

	# Novo agente para publicação no WordPress
	@agent
	def blog_publisher(self) -> Agent:
		return Agent(
			config=self.agents_config['blog_publisher'],
			tools=[wordpress_tool],  # Ferramenta de publicação no WordPress
			verbose=True
		)

	@task
	def research_task(self) -> Task:
		return Task(
			config=self.tasks_config['research_task'],
		)

	@task
	def reporting_task(self) -> Task:
		return Task(
			config=self.tasks_config['reporting_task'],
			output_file='report.md'
		)

	@task
	def translate_task(self) -> Task:
		return Task(
			config=self.tasks_config['translate_task'],
			agent=self.translator(),
			output_file='report_ptbr.md'
		)

	# Nova tarefa para publicar no blog WordPress
	@task
	def publish_task(self) -> Task:
		return Task(
			config=self.tasks_config['publish_task'],
			agent=self.blog_publisher(),  # Agente de publicação
			input_file='report_ptbr.md'  # O arquivo que será publicado
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the AgenciaNoticias crew"""
		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)