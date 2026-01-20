from agents import Agents
from tasks import Tasks

from crewai import Crew

tasks = Tasks()
agents = Agents()

# Create Agents
researcher_agent = agents.quant_financial_agent()
reporting_analyst_agent = agents.reporting_analyst()

# Define Tasks for each agent
research_company_culture_task = tasks.research_company_stocks(researcher_agent)
summarize_stock_task = tasks.summarize_stock_information(researcher_agent)

# Instantiate the crew with a sequential process
crew = Crew(
    agents=[researcher_agent, reporting_analyst_agent],
    tasks=[
        research_company_culture_task,
        summarize_stock_task,
    ],
)

# Kick off the process
result = crew.kickoff()

print("Financial Analysis Process Completed.")
print("Final Financial Analysis:")
print(result)
