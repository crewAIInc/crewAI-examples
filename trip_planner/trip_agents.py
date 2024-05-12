import os

from crewai import Agent
from langchain_openai.chat_models import ChatOpenAI
from langchain_community.chat_models import ChatOllama

from tools.browser_tools import BrowserTools
from tools.calculator_tools import CalculatorTools
from tools.search_tools import SearchTools

from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")


class TripAgents():

    def __init__(self):
        self.mistral = ChatOllama(model = "crewai-mistral")    #check model file
        self.llama2 = ChatOllama(model = "crewai-llama2")   
        self.gemma = ChatOllama(model = "crewai-gemma")
        self.openai = ChatOpenAI(api_key = api_key, temperature=0)

    def city_selection_agent(self):
        return Agent(
            role='City Selection Expert',
            goal='Select the best city based on weather, season, and prices',
            backstory=
            'An expert in analyzing travel data to pick ideal destinations',
            tools=[
                SearchTools.search_internet,
                BrowserTools.scrape_and_summarize_website,
            ],
            verbose=True,
            allow_delegation=False,
            max_iter= 15,
            llm = self.openai,
            #llm = self.mistral)

    def local_expert(self):
        return Agent(
            role='Local Expert at this city',
            goal='Provide the BEST insights about the selected city',
            backstory="""A knowledgeable local guide with extensive information
            about the city, it's attractions and customs""",
            tools=[
                SearchTools.search_internet,
                BrowserTools.scrape_and_summarize_website,
            ],
            verbose=True,
            llm = self.openai)

    def travel_concierge(self):
        return Agent(
            role='Amazing Travel Concierge',
            goal="""Create the most amazing travel itineraries with budget and 
            packing suggestions for the city""",
            backstory="""Specialist in travel planning and logistics with 
            decades of experience""",
            tools=[
                SearchTools.search_internet,
                BrowserTools.scrape_and_summarize_website,
                CalculatorTools.calculate,
            ],
            verbose=True,
            llm = self.openai)
