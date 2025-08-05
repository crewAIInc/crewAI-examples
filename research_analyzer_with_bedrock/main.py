from crewai import Crew
from agents import ResearchAgents
from tasks import ResearchTasks
from utils.PdfReader import PdfReader
import sys


class ResearchAnalyzerCrew:
    """
    Orchestrates the research paper analysis process using a crew of AI agents.
    Manages the workflow of technical analysis, literature review, summarization,
    and final report generation.
    """

    def __init__(self, paper_content: str):
        """
        Initialize the analyzer with research paper content.

        Args:
            paper_content (str): The extracted text content of the research paper
        """
        self.paper_content = paper_content

    def run(self) -> str:
        """
        Executes the complete research paper analysis workflow.

        The workflow consists of four main steps:
        1. Technical analysis of the paper's methodology and results
        2. Literature review and context analysis
        3. Creation of a comprehensive summary
        4. Generation of a final report with insights and recommendations

        Returns:
            str: The final analysis report
        """
        # Initialize factory classes for agents and tasks
        agents = ResearchAgents()
        tasks = ResearchTasks()

        # Initialize specialized agents for different aspects of analysis
        research_director = agents.get_research_director()
        technical_expert = agents.get_technical_expert()
        literature_specialist = agents.get_literature_specialist()
        summary_writer = agents.get_summary_writer()

        # Define sequential analysis tasks with dependencies
        technical_analysis_task = tasks.analyze_technical_components(
            agent=technical_expert,
            paper_content=self.paper_content
        )

        literature_review_task = tasks.review_literature_context(
            agent=literature_specialist,
            paper_content=self.paper_content,
            technical_analysis="{{ technical_analysis_task.output }}"  # Depends on technical analysis
        )

        summary_task = tasks.create_research_summary(
            agent=summary_writer,
            technical_analysis="{{ technical_analysis_task.output }}",
            literature_review="{{ literature_review_task.output }}"  # Depends on both previous tasks
        )

        final_report_task = tasks.create_final_report(
            agent=research_director,
            summary="{{ summary_task.output }}",
            technical_analysis="{{ technical_analysis_task.output }}",
            literature_review="{{ literature_review_task.output }}"  # Integrates all previous outputs
        )

        # Configure the CrewAI workflow with agents and their tasks
        crew = Crew(
            agents=[
                research_director,
                technical_expert,
                literature_specialist,
                summary_writer
            ],
            tasks=[
                technical_analysis_task,
                literature_review_task,
                summary_task,
                final_report_task
            ],
            verbose=True  # Enable detailed logging of the analysis process
        )

        # Execute the analysis workflow
        result = crew.kickoff()
        return result


if __name__ == "__main__":
    print("## Welcome to Research Analyzer AI")
    print("----------------------------------")

    # Validate command line arguments
    if len(sys.argv) != 2:
        print("Usage: python main.py <path_to_pdf>")
        print("Example: python main.py research_paper.pdf")
        sys.exit(1)

    pdf_path = sys.argv[1]
    print(f"\nReading PDF file: {pdf_path}")

    try:
        # Extract and process PDF content
        pdf_reader = PdfReader(pdf_path)
        paper_content = pdf_reader.read()

        print("\nPDF content extracted successfully!")
        print(f"Content length: {len(paper_content)} characters")

        # Initialize and execute the analysis workflow
        print("\nStarting analysis...")
        research_crew = ResearchAnalyzerCrew(paper_content)
        result = research_crew.run()

        # Display analysis results
        print("\n\n########################")
        print("## Research Analysis Results:")
        print("########################\n")
        print(result)

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
