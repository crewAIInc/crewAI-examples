from textwrap import dedent

from crewai import Task


def create_company_research_task(agent, company_name, suffix_prompt=""):
    """Create a company research task."""
    return Task(
        description=dedent(f"""\
            Conduct a thorough research on the company conducting the interview. 
            Gather information about its history, products, services, reputation, 
            culture, competitors, recent news and any relevant business activities.
            Identify potential red flags that could be relevant to know before the interview.
            
            Don't leave any stone unturned!
            
            Company conducting the interview: {company_name}
            
            {suffix_prompt}
            """),
        expected_output=dedent("""\
            A detailed report highlighting all the key findings about the company on each of the categories researched.
            """),
        async_execution=True,
        agent=agent
    )


def create_industry_research_task(agent, company_name, suffix_prompt=""):
    """Task to research the industry of the company conducting the interview."""
    return Task(
        description=dedent(f"""\
        Analyze the current industry trends, challenges, and opportunities
        relevant to the company. Consider factors such as market growth,
        competition, regulations, and technological advancements to provide a comprehensive
        overview of the industry landscape.
        
        Company Name: {company_name}
        
        {suffix_prompt}
        """),
        expected_output=dedent("""\
        An insightful analysis that identifies major trends, potential challenges and strategic opportunities.
        """),
        agent=agent
    )


def create_write_report_task(agent, suffix_prompt=""):
    """Task to compile all the information into a single report."""
    return Task(
        description=dedent(f"""\
        Compile all the information into one single report. Don't summarize anything,
        just compile all the information you got about the company and the industry.
        If you are missing information for any section, ask the respective agent to provide it.
        """),
        expected_output=dedent(f"""\
        A well structured document with a section for the company information and another for the industry.
        
        For the company, include subsections such as Services, Reputation, Products, Culture,
        Recent News, Competitors, Strengths and Weaknesses, and Potential Red Flags. Inside each subsection,
        discuss the main points and provide examples, references or explanations where necessary.
        
        For the industry, include subsections such as Trends, Challenges, and Opportunities.
        
        Finalize with a section for Insightful Questions about the company and the industry
        that could be asked during the interview to show interest and knowledge.
        YOUR FINAL ANSWER MUST RETURN THE COMPLETE REPORT AND DETAILS, NOT JUST A SUMMARY.
        
        {suffix_prompt}
        """),
        agent=agent
    )
