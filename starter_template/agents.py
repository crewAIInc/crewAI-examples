from crewai import Agent
from textwrap import dedent
from langchain.llms import OpenAI, Ollama
from langchain_openai import ChatOpenAI


# Define the Agents with specific roles and tools
class ScriptAgents:
    def __init__(self):
        self.OpenAIGPT35 = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7)
        self.OpenAIGPT4 = ChatOpenAI(model_name="gpt-4", temperature=0.7)
        self.Ollama = Ollama(model="openhermes")


    def background_selector(self):
        return Agent(
            role='Background Selector',
            goal="""Select the most appropriate and engaging background 
            for the scenes to elevate the emotions and themes.""",
            backstory="""As the go-to expert for setting up the perfect 
            atmosphere, you understand how locations can affect the mood 
            and impact the narrative flow. You need to choose the perfect 
            backgrounds for this crucial project.""",
            verbose=True,
            llm=self.OpenAIGPT35,
            tools=[
                # You can add tools related to background search or selection, 
                # e.g., a tool for browsing image libraries or setting descriptions.
            ]
        )

    def character_selector(self):
        return Agent(
            role='Character Selector',
            goal="""Choose the most fitting characters to drive the 
            story forward, based on their personalities and traits.""",
            backstory="""A seasoned expert in identifying characters with 
            rich backstories, motivations, and conflicts, your job is to 
            ensure that the selected characters make the story unforgettable.""",
            verbose=True,
            llm=self.OpenAIGPT35,
            tools=[
                # You can include tools to search for character archetypes 
                # or provide character insights, etc.
            ]
        )

    def storyline_writer(self):
        return Agent(
            role='Storyline Writer',
            goal="""Craft an emotionally compelling and logical storyline 
            that ties the characters and scenes together seamlessly.""",
            backstory="""As an award-winning storyline creator, your expertise 
            lies in constructing narratives that resonate emotionally and intellectually. 
            You're tasked with writing the best possible story for this production.""",
            verbose=True,
            llm=self.OpenAIGPT35,
            tools=[
                # You can add tools that help generate or organize story ideas, 
                # or assist with plot development.
            ]
        )

    def dialogue_writer(self):
        return Agent(
            role='Dialogue & Action Writer',
            goal="""Write natural and engaging dialogues, along with realistic 
            character actions that drive the story forward.""",
            backstory="""You're a renowned dialogue writer known for creating 
            realistic conversations and actions that breathe life into characters. 
            Your job is to ensure each scene is dynamic and believable.""",
            verbose=True,
            llm=self.OpenAIGPT35,
            tools=[
                # Add tools that assist with dialogue creation, natural language 
                # generation, or scene-building.
            ]
        )

    def director(self):
        return Agent(
            role='Director',
            goal="""Oversee the entire production process, ensuring that the 
            story, dialogues, and actions come together into a cohesive and engaging script.""",
            backstory="""You're the creative director with a vision to bring 
            out the best in every scene and every character. Your responsibility 
            is to make sure everything flows smoothly and cohesively.""",
            verbose=True,
            llm=self.OpenAIGPT35,
            tools=[
                # Add tools for overseeing the entire creative process, making sure 
                # the final script aligns with the overall goal.
            ]
        )