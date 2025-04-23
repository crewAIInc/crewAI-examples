from crewai import Agent
from utils.Bedrock import load_bedrock_llm

# Initialize Bedrock LLM instances for all agents
bedrock_llm = load_bedrock_llm()


class ResearchAgents:
    """
    Factory class for creating specialized research analysis agents.
    Each agent is configured with specific roles, goals, and expertise
    for different aspects of research paper analysis.
    """

    @staticmethod
    def get_research_director() -> Agent:
        """
        Creates a Research Director agent responsible for overseeing the entire
        analysis process and ensuring quality of outputs.

        Returns:
            Agent: Configured Research Director agent instance
        """
        return Agent(
            role='Research Director',
            goal='Coordinate research analysis and ensure high-quality comprehensive output',
            backstory='Former Research Director at top universities with 15+ years of experience in managing research teams and projects',
            verbose=True,
            llm=bedrock_llm
        )

    @staticmethod
    def get_technical_expert() -> Agent:
        """
        Creates a Technical Expert agent specialized in analyzing methodologies,
        statistical approaches, and technical aspects of research papers.

        Returns:
            Agent: Configured Technical Expert agent instance
        """
        return Agent(
            role='Technical Analysis Expert',
            goal='Analyze technical methodologies, results, and statistical significance in research papers',
            backstory='PhD in Data Science with 10+ years experience in research analysis and statistical methods',
            verbose=True,
            llm=bedrock_llm
        )

    @staticmethod
    def get_literature_specialist() -> Agent:
        """
        Creates a Literature Specialist agent focused on contextualizing research
        within the broader academic landscape and identifying connections.

        Returns:
            Agent: Configured Literature Specialist agent instance
        """
        return Agent(
            role='Literature Review Specialist',
            goal='Analyze research context and identify connections with existing literature',
            backstory='Academic librarian with expertise in systematic reviews and meta-analyses',
            verbose=True,
            llm=bedrock_llm
        )

    @staticmethod
    def get_summary_writer() -> Agent:
        """
        Creates a Summary Writer agent specialized in distilling complex
        research into clear, accessible summaries.

        Returns:
            Agent: Configured Summary Writer agent instance
        """
        return Agent(
            role='Summary Writer',
            goal='Create clear, concise summaries of complex research papers',
            backstory='Science communication expert with experience in top scientific journals',
            verbose=True,
            llm=bedrock_llm
        )
