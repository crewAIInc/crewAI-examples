from textwrap import dedent
from crewai import Task

class GameTasks():
	def code_task(self, agent, game):
		return Task(description=dedent(f"""You will create a game using python, these are the instructions:

			Instructions
			------------
    	{game}

			Your Final answer must be the full python code, only the python code and nothing else.
			"""),
			agent=agent
		)

	def review_task(self, agent, game):
		return Task(description=dedent(f"""\
			You are helping create a game using python, these are the instructions:

			Instructions
			------------
			{game}

			Using the code you got, check for errors. Check for logic errors,
			syntax errors, missing imports, variable declarations, mismatched brackets,
			and security vulnerabilities.

			Your Final answer must be the full python code, only the python code and nothing else.
			"""),
			agent=agent
		)

	def evaluate_task(self, agent, game):
		return Task(description=dedent(f"""\
			You are helping create a game using python, these are the instructions:

			Instructions
			------------
			{game}

			You will look over the code to insure that it is complete and
			does the job that it is supposed to do.

			Your Final answer must be the full python code, only the python code and nothing else.
			"""),
			agent=agent
		)