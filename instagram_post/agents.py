import os
from textwrap import dedent
from crewai import Agent
from tools.browser_tools import BrowserTools
from tools.search_tools import SearchTools
from langchain.agents import load_tools

from langchain.llms import Ollama

class MarketingAnalysisAgents:
	def __init__(self):
		self.llm = Ollama(model=os.environ['MODEL'])

	def product_competitor_agent(self):
		return Agent(
			role="Lead Market Analyst",
			goal=dedent("""\
				Conduct amazing analysis of the products and
				competitors, providing in-depth insights to guide
				marketing strategies."""),
			backstory=dedent("""\
				As the Lead Market Analyst at a premier
				digital marketing firm, you specialize in dissecting
				online business landscapes."""),
			tools=[
					BrowserTools.scrape_and_summarize_website,
					SearchTools.search_internet
			],
			allow_delegation=False,
			llm=self.llm,
			verbose=True
		)

	def strategy_planner_agent(self):
		return Agent(
			role="Chief Marketing Strategist",
			goal=dedent("""\
				Synthesize amazing insights from product analysis
				to formulate incredible marketing strategies."""),
			backstory=dedent("""\
				You are the Chief Marketing Strategist at
				a leading digital marketing agency, known for crafting
				bespoke strategies that drive success."""),
			tools=[
					BrowserTools.scrape_and_summarize_website,
					SearchTools.search_internet,
					SearchTools.search_instagram
			],
			llm=self.llm,
			verbose=True
		)

	def creative_content_creator_agent(self):
		return Agent(
			role="Creative Content Creator",
			goal=dedent("""\
				Develop compelling and innovative content
				for social media campaigns, with a focus on creating
				high-impact Instagram ad copies."""),
			backstory=dedent("""\
				As a Creative Content Creator at a top-tier
				digital marketing agency, you excel in crafting narratives
				that resonate with audiences on social media.
				Your expertise lies in turning marketing strategies
				into engaging stories and visual content that capture
				attention and inspire action."""),
			tools=[
					BrowserTools.scrape_and_summarize_website,
					SearchTools.search_internet,
					SearchTools.search_instagram
			],
			llm=self.llm,
			verbose=True
		)

	def senior_photographer_agent(self):
		return Agent(
				role="Senior Photographer",
				goal=dedent("""\
					Take the most amazing photographs for instagram ads that
					capture emotions and convey a compelling message."""),
				backstory=dedent("""\
					As a Senior Photographer at a leading digital marketing
					agency, you are an expert at taking amazing photographs that
					inspire and engage, you're now working on a new campaign for a super
					important customer and you need to take the most amazing photograph."""),
				tools=[
					BrowserTools.scrape_and_summarize_website,
					SearchTools.search_internet,
					SearchTools.search_instagram
				],
				llm=self.llm,
				allow_delegation=False,
				verbose=True
		)

	def chief_creative_diretor_agent(self):
		return Agent(
				role="Chief Creative Director",
				goal=dedent("""\
					Oversee the work done by your team to make sure it's the best
					possible and aligned with the product's goals, review, approve,
					ask clarifying question or delegate follow up work if necessary to make
					decisions"""),
				backstory=dedent("""\
					You're the Chief Content Officer of leading digital
					marketing specialized in product branding. You're working on a new
					customer, trying to make sure your team is crafting the best possible
					content for the customer."""),
				tools=[
					BrowserTools.scrape_and_summarize_website,
					SearchTools.search_internet,
					SearchTools.search_instagram
				],
				llm=self.llm,
				verbose=True
		)
