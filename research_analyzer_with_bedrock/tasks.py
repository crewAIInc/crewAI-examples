from textwrap import dedent
from crewai import Task


class ResearchTasks:
    """
    Defines the task structure for research paper analysis workflow.
    Each task represents a specific phase of the analysis process,
    with defined inputs, expectations, and quality guidelines.
    """

    def __tip_section(self) -> str:
        """
        Private method to provide motivation prompt for agents.
        Used across all tasks to encourage high-quality output.

        Returns:
            str: Motivation message for the AI agents
        """
        return "If you do your BEST WORK, I'll give you a $10,000 commission!"

    def analyze_technical_components(self, agent, paper_content: str) -> Task:
        """
        Creates a task for technical analysis of the research paper.
        Focuses on methodology, statistical analysis, and key findings.

        Args:
            agent: The technical expert agent assigned to this task
            paper_content (str): The full text content of the research paper

        Returns:
            Task: Configured task for technical analysis
        """
        return Task(
            description=dedent(
                f"""
                Analyze the research paper and identify key technical components including:
                - Research methodology
                - Statistical analysis
                - Key findings and results
                - Technical tools and frameworks used

                Paper content: {paper_content}

                {self.__tip_section()}

                Make sure to:
                - Be thorough in your technical analysis
                - Identify any potential limitations in the methodology
                - Validate statistical significance of results
                - Highlight innovative technical approaches
                """
            ),
            expected_output="A detailed technical analysis report including methodology assessment, statistical "
                            "validation, and key findings",
            agent=agent,
        )

    def review_literature_context(self, agent, paper_content: str, technical_analysis: str) -> Task:
        """
        Creates a task for analyzing the paper's context within existing literature.
        Incorporates insights from the technical analysis to inform the review.

        Args:
            agent: The literature specialist agent assigned to this task
            paper_content (str): The full text content of the research paper
            technical_analysis (str): Output from the technical analysis task

        Returns:
            Task: Configured task for literature review
        """
        return Task(
            description=dedent(
                f"""
                Review the paper's context within the broader field considering:
                - Related works
                - Current state of the field
                - Research gaps addressed
                - Potential future directions

                Paper content: {paper_content}
                Technical analysis provided: {technical_analysis}

                {self.__tip_section()}

                Make sure to:
                - Connect findings to existing literature
                - Identify research gaps
                - Evaluate the paper's contribution to the field
                - Suggest potential future research directions
                """
            ),
            expected_output="A comprehensive literature review report connecting the paper to existing research and identifying its contributions",
            agent=agent,
        )

    def create_research_summary(self, agent, technical_analysis: str, literature_review: str) -> Task:
        """
        Creates a task for synthesizing the technical analysis and literature review
        into a clear, comprehensive summary.

        Args:
            agent: The summary writer agent assigned to this task
            technical_analysis (str): Output from the technical analysis task
            literature_review (str): Output from the literature review task

        Returns:
            Task: Configured task for creating research summary
        """
        return Task(
            description=dedent(
                f"""
                Create a clear and comprehensive summary based on:
                Technical Analysis: {technical_analysis}
                Literature Review: {literature_review}

                {self.__tip_section()}

                Make sure to:
                - Synthesize key findings
                - Highlight main contributions
                - Express complex concepts clearly
                - Include practical implications
                """
            ),
            expected_output="A clear, concise summary that combines technical insights with broader research context",
            agent=agent,
        )

    def create_final_report(self, agent, summary: str, technical_analysis: str, literature_review: str) -> Task:
        """
        Creates a task for generating the final comprehensive report that integrates
        all previous analyses and provides actionable insights.

        Args:
            agent: The research director agent assigned to this task
            summary (str): Output from the summary task
            technical_analysis (str): Output from the technical analysis task
            literature_review (str): Output from the literature review task

        Returns:
            Task: Configured task for creating final report
        """
        return Task(
            description=dedent(
                f"""
                Create a final comprehensive report incorporating:
                Summary: {summary}
                Technical Analysis: {technical_analysis}
                Literature Review: {literature_review}

                {self.__tip_section()}

                Make sure to:
                - Provide executive summary
                - Include key recommendations
                - Highlight critical insights
                - Suggest practical applications
                - Include future research directions
                """
            ),
            expected_output="A comprehensive final report with executive summary, insights, and recommendations",
            agent=agent,
        )
