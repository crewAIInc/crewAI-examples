import os

from crewai import Crew, Process
from textwrap import dedent
from trip_agents import TripAgents
from trip_tasks import TripTasks

from langchain_openai.chat_models import ChatOpenAI
from langchain_community.chat_models import chatOllama

from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY") #pulled from .env file

class TripCrew:

  def __init__(self, origin, cities, date_range, interests):
    self.cities = cities
    self.origin = origin
    self.interests = interests
    self.date_range = date_range
    self.openai = ChatOpenAI(api_key = api_key, temperature = 0.3)
    #change model name to one of the available ollama model. (Performance will vary based on the model)
    self.mistral = ChatOllama(model = "crewai-mistral")      

  def run(self):
    agents = TripAgents()
    tasks = TripTasks()

    city_selector_agent = agents.city_selection_agent()
    local_expert_agent = agents.local_expert()
    travel_concierge_agent = agents.travel_concierge()

            identify_task = tasks.identify_task(
            agent=city_selector_agent,
            origin=self.origin,
            cities=self.cities,
            interests=self.interests,
            range=self.date_range
        )

        gather_task = tasks.gather_task(
            agent=local_expert_agent,
            origin=self.origin,
            interests=self.interests,
            range=self.date_range,
            context=[identify_task]   # can take in a list of context

        )

        plan_task = tasks.plan_task(
            agent=travel_concierge_agent,
            origin=self.origin,
            interests=self.interests,
            range=self.date_range,
            context=[gather_task]
        )

        crew = Crew(
            agents=[city_selector_agent, local_expert_agent, travel_concierge_agent],
            tasks=[identify_task, gather_task, plan_task],
            process= Process.Sequential,     #try out the previous Hierarchical process
            manager_llm=self.openai
            #manager_llm = self.mistral
        )


    result = crew.kickoff()
    return result

if __name__ == "__main__":
  print("## Welcome to Trip Planner Crew")
  print('-------------------------------')
  location = input(
    dedent("""
      From where will you be traveling from?
    """))
  cities = input(
    dedent("""
      What are the cities options you are interested in visiting?
    """))
  date_range = input(
    dedent("""
      What is the date range you are interested in traveling?
    """))
  interests = input(
    dedent("""
      What are some of your high level interests and hobbies?
    """))
  
  trip_crew = TripCrew(location, cities, date_range, interests)
  result = trip_crew.run()
  print("\n\n########################")
  print("## Here is you Trip Plan")
  print("########################\n")
  print(result)
