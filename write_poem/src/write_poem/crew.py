from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

# If you want to run a snippet of code before or after the crew starts, 
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class WritePoem():
	"""WritePoem crew"""

	# Learn more about YAML configuration files here:
	# Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
	# Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	@agent
	def writer(self):
		return Agent(
			config=self.agents_config["writer"],
			verbose=True,
		)

	@agent
	def critic(self):
		return Agent(
			config=self.agents_config["critic"],
			verbose=True,
		)

	@task
	def write_poem(self):
		return Task(
			config=self.tasks_config['write_poem'],
		)

	@task
	def rewrite_poem(self):
		return Task(
			config=self.tasks_config['rewrite_poem'],
		)

	@task
	def critique_poem(self):
		return Task(
			config=self.tasks_config['critique_poem'],
		)

	def iterate_poem(self, inputs, iterations=3):
		poem = ""
		writer_agent: Agent = self.writer()
		critic_agent = self.critic()
		writer_task = self.write_poem()
		rewriter_task = self.rewrite_poem()
		critic_task = self.critique_poem()
		for i in range(iterations):
			print("######################")
			print(f"iteration: {i+1}")
			print("######################")
			if i == 0:
				poem = writer_agent.execute_task(task=writer_task, context=inputs)
			else:
				feedback = critic_agent.execute_task(task=critic_task, context=f"poem: ```{poem}```")
				poem = writer_agent.execute_task(task=rewriter_task, context=f"poem: ```{poem}``` feedback: ```{feedback}```")
		return poem

	@crew
	def crew(self) -> Crew:
		"""Creates the WritePoem crew"""
		# To learn how to add knowledge sources to your crew, check out the documentation:
		# https://docs.crewai.com/concepts/knowledge#what-is-knowledge

		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)
