from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from crewai_tools import CSVSearchTool, FileReadTool

@CrewBase
class MatchToProposalCrew():
		"""MatchToProposal crew"""
		agents_config = 'config/HPagents.yaml'
		tasks_config = 'config/HPTasks.yaml'

		@agent
		def jd_reader(self) -> Agent:
				return Agent(
						config=self.agents_config['jd_reader'],
						tools=[FileReadTool()],
						verbose=True,
						allow_delegation=False
				)
		@agent
		def hp_reader(self) -> Agent:
				return Agent(
						config=self.agents_config['hp_reader'],
						tools=[FileReadTool()],
						verbose=True,
						allow_delegation=False
				)
		
		@agent
		def hp_generator(self) -> Agent:
				return Agent(
						config=self.agents_config['hp_generator'],
						tools=[FileReadTool()],
						verbose=True,
						allow_delegation=False
				)

		@task
		def read_jd_task(self) -> Task:
				return Task(
						config=self.tasks_config['read_jd_task'],
						agent=self.jd_reader()
				)

		@task
		def read_hp_task(self) -> Task:
				return Task(
						config=self.tasks_config['read_hp_task'],
						agent=self.hp_reader()
				)
		@task
		def hp_generator_task(self) -> Task:
				return Task(
						config=self.tasks_config['hp_generator_task'],
						agent=self.hp_generator()
				)

		@crew
		def crew(self) -> Crew:
				"""Creates the MatchToProposal crew"""
				return Crew(
						agents=self.agents, # Automatically created by the @agent decorator
						tasks=self.tasks, # Automatically created by the @task decorator
						process=Process.sequential,
						verbose=2,
						# process=Process.hierarchical, # In case you want to use that instead https://docs.crewai.com/how-to/Hierarchical/
				)
