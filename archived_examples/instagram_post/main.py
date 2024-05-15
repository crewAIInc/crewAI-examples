from dotenv import load_dotenv
load_dotenv()

from textwrap import dedent
from crewai import Agent, Crew

from tasks import MarketingAnalysisTasks
from agents import MarketingAnalysisAgents

tasks = MarketingAnalysisTasks()
agents = MarketingAnalysisAgents()

print("## Welcome to the marketing Crew")
print('-------------------------------')
product_website = input("What is the product website you want a marketing strategy for?\n")
product_details = input("Any extra details about the product and or the instagram post you want?\n")


# Create Agents
product_competitor_agent = agents.product_competitor_agent()
strategy_planner_agent = agents.strategy_planner_agent()
creative_agent = agents.creative_content_creator_agent()
# Create Tasks
website_analysis = tasks.product_analysis(product_competitor_agent, product_website, product_details)
market_analysis = tasks.competitor_analysis(product_competitor_agent, product_website, product_details)
campaign_development = tasks.campaign_development(strategy_planner_agent, product_website, product_details)
write_copy = tasks.instagram_ad_copy(creative_agent)

# Create Crew responsible for Copy
copy_crew = Crew(
	agents=[
		product_competitor_agent,
		strategy_planner_agent,
		creative_agent
	],
	tasks=[
		website_analysis,
		market_analysis,
		campaign_development,
		write_copy
	],
	verbose=True
)

ad_copy = copy_crew.kickoff()

# Create Crew responsible for Image
senior_photographer = agents.senior_photographer_agent()
chief_creative_diretor = agents.chief_creative_diretor_agent()
# Create Tasks for Image
take_photo = tasks.take_photograph_task(senior_photographer, ad_copy, product_website, product_details)
approve_photo = tasks.review_photo(chief_creative_diretor, product_website, product_details)

image_crew = Crew(
	agents=[
		senior_photographer,
		chief_creative_diretor
	],
	tasks=[
		take_photo,
		approve_photo
	],
	verbose=True
)

image = image_crew.kickoff()

# Print results
print("\n\n########################")
print("## Here is the result")
print("########################\n")
print("Your post copy:")
print(ad_copy)
print("'\n\nYour midjourney description:")
print(image)
