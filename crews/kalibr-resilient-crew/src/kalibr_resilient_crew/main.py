# IMPORTANT: kalibr must be the first import.
# It monkey-patches OpenAI and Anthropic SDK clients so that every
# LLM call in this process is automatically traced, routed, and scored.
import kalibr  # noqa: F401 — must be first

import sys
from dotenv import load_dotenv
from kalibr_resilient_crew.crew import KalibrResilientJobPostingCrew

load_dotenv()


def run():
    """
    Run the Kalibr-resilient job posting crew.

    Kalibr automatically routes each LLM call to the optimal model based on
    live outcome signals. If GPT-4o degrades, calls route to Claude Sonnet.
    No code changes needed — routing adapts in real time.
    """
    inputs = {
        'company_domain': 'careers.wbd.com',
        'company_description': (
            "Warner Bros. Discovery is a premier global media and entertainment company, "
            "offering audiences the world's most differentiated and complete portfolio of "
            "content, brands and franchises across television, film, sports, news, "
            "streaming and gaming."
        ),
        'hiring_needs': 'Production Assistant, for a TV production set in Los Angeles in June 2025',
        'specific_benefits': 'Weekly Pay, Employee Meals, healthcare',
    }
    KalibrResilientJobPostingCrew().crew().kickoff(inputs=inputs)


def train():
    """Train the crew for a given number of iterations."""
    inputs = {
        'company_domain': 'careers.wbd.com',
        'company_description': (
            "Warner Bros. Discovery is a premier global media and entertainment company."
        ),
        'hiring_needs': 'Production Assistant, for a TV production set in Los Angeles',
        'specific_benefits': 'Weekly Pay, Employee Meals, healthcare',
    }
    try:
        KalibrResilientJobPostingCrew().crew().train(
            n_iterations=int(sys.argv[1]),
            inputs=inputs,
        )
    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")
