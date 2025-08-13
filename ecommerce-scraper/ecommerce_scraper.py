from crewai import Agent, Crew, Process, Task

from crewai_tools import ScrapegraphScrapeTool
from dotenv import load_dotenv

load_dotenv()

website = "https://www.ebay.it/sch/i.html?_from=R40&_trksid=m570.l1313&_nkw=keyboard&_sacat=0"
tool = ScrapegraphScrapeTool()

agent = Agent(
    role="Web Researcher",
    goal="Research and extract accurate information from websites",
    backstory="You are an expert web researcher with experience in extracting and analyzing information from various websites.",
    tools=[tool],
)

task = Task(
    name="scraping task",
    description=f"Visit the website {website} and extract detailed information about all the keyboards available.",
    expected_output="A file with the informations extracted from the website.",
    agent=agent,    
)

crew = Crew(
    agents=[agent],
    tasks=[task],
)

crew.kickoff()