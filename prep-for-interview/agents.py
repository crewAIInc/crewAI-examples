from textwrap import dedent

from crewai import Agent
from langchain_community.llms.ollama import Ollama
from langchain_core.tools import Tool


def create_research_agent(llm: Ollama, tools: list[Tool]) -> Agent:
    """Create a Research Specialist agent."""
    return Agent(
        role='Research Specialist',
        goal='Conduct thorough research on the company that is doing the interview.',
        llm=llm,
        tools=tools,
        backstory=dedent(f"""\
                    As a Research Specialist, you know how to use an Internet Search Engine to find
                    information about the company you are investigating. You reflect on the information you find and decide if it is
                    relevant and enough to the task at hand or if you need to change your search direction.
                    """),
        allow_delegation=True,
        verbose=True
    )


def create_industry_analysis_agent(llm: Ollama, tools: list[Tool]) -> Agent:
    """Create an Industry Analyst agent."""
    return Agent(
        role='Industry Analyst',
        goal='Conduct thorough research on the industry the company interviewing operates in.',
        llm=llm,
        tools=tools,
        backstory=dedent(f"""\
                As an Industry Analyst, you know how to use an Internet Search Engine to find
                information about the industry the company operates in.
                You know how to identify if the information you have about the industry is 
                relevant and enough to the task at hand or if you need to change your search direction.  
                """),
        allow_delegation=True,
        verbose=True
    )


def create_report_writer_agent(llm: Ollama, tools: list[Tool]) -> Agent:
    """Create an Insightful Writer agent."""
    return Agent(
        role='Insightful Writer',
        goal='Write a well structured report about the company and the industry with all the information gathered including the sources.',
        llm=llm,
        tools=tools,
        backstory=dedent(f"""\
                    As an Insightful Writer, you know how to write a well structured report, with clear sections and
                    all the information you have gathered about the company and the industry. You don't summarize anything,
                    just structure the information in a way that is easy to read and understand and include the sources.
                    """),
        allow_delegation=True,
        verbose=True,
    )
