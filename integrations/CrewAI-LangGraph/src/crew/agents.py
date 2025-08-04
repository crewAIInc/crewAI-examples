from langchain_community.agent_toolkits import GmailToolkit
from langchain_community.tools.gmail.get_thread import GmailGetThread
from langchain_community.tools.tavily_search import TavilySearchResults

from textwrap import dedent
from crewai import Agent
from .tools import CreateDraftTool

class EmailFilterAgents():
	def __init__(self):
		self.gmail = GmailToolkit()

	def email_filter_agent(self):
		return Agent(
			role='Senior Email Analyst',
			goal='Filter out non-essential emails like newsletters and promotional content',
			backstory=dedent("""\
				As a Senior Email Analyst, you have extensive experience in email content analysis.
				You are adept at distinguishing important emails from spam, newsletters, and other
				irrelevant content. Your expertise lies in identifying key patterns and markers that
				signify the importance of an email."""),
			verbose=True,
			allow_delegation=False
		)

	def email_action_agent(self):

		return Agent(
			role='Email Action Specialist',
			goal='Identify action-required emails and compile a list of their IDs',
			backstory=dedent("""\
				With a keen eye for detail and a knack for understanding context, you specialize
				in identifying emails that require immediate action. Your skill set includes interpreting
				the urgency and importance of an email based on its content and context."""),
			tools=[
				GmailGetThread(api_resource=self.gmail.api_resource),
				TavilySearchResults()
			],
			verbose=True,
			allow_delegation=False,
		)

	def email_response_writer(self):
		return Agent(
			role='Email Response Writer',
			goal='Draft responses to action-required emails',
			backstory=dedent("""\
				You are a skilled writer, adept at crafting clear, concise, and effective email responses.
				Your strength lies in your ability to communicate effectively, ensuring that each response is
				tailored to address the specific needs and context of the email."""),
			tools=[
				TavilySearchResults(),
				GmailGetThread(api_resource=self.gmail.api_resource),
				CreateDraftTool.create_draft
			],
			verbose=True,
			allow_delegation=False,
		)