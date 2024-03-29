from textwrap import dedent

from crewai import Crew
from langchain_community.llms.ollama import Ollama
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import Tool

import agents
import tasks

if __name__ == "__main__":
    print("## Welcome to the Interview Prep Crew")
    print('-------------------------------')
    company_name = input("What's the name of the company conducting the interview?\n")

    # Tools
    search_tool = Tool.from_function(
        func=DuckDuckGoSearchRun().run,
        name="Search",
        description="Internet Search Engine useful for when you need to search the internet for information"
    )

    # LLM Model
    llm = Ollama(model="mixtral:8x7b-instruct-v0.1-q6_K", temperature=0.2, num_ctx="8192")

    # Agents
    researcher_agent = agents.create_research_agent(llm, [search_tool])
    industry_analyst_agent = agents.create_industry_analysis_agent(llm, [search_tool])
    report_writer_agent = agents.create_report_writer_agent(llm, [])

    # Tasks
    suffix_prompt = dedent(f"""\
        IMPORTANT: Don't forget to include all the URLs and titles to the sources from where you got the information.
        You'll get a $1000 tip if you do your best work!""")
    company_research_task = tasks.create_company_research_task(researcher_agent, company_name, suffix_prompt)
    industry_research_task = tasks.create_industry_research_task(industry_analyst_agent, company_name, suffix_prompt)
    write_report_task = tasks.create_write_report_task(report_writer_agent, suffix_prompt)

    write_report_task.context = [company_research_task, industry_research_task]

    report_crew = Crew(
        agents=[
            researcher_agent,
            industry_analyst_agent,
            report_writer_agent,
        ],
        tasks=[
            company_research_task,
            industry_research_task,
            write_report_task,
        ],
    )

    report = report_crew.kickoff()

    print("\n\n################################################")
    print("## Here is the report")
    print("################################################\n")
    print(report)
    print("################################################\n")
