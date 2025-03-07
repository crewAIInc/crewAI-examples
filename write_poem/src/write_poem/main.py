#!/usr/bin/env python
import os
import sys
import warnings

from datetime import datetime

import dotenv
from crewai.agent import agentops

from .crew import WritePoem

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")
dotenv.load_dotenv()

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    # agentops.init(
    #     api_key=os.environ.get("AGENTOPS_API_KEY"),
    # )

    """
    Run the crew.
    """
    inputs = {
        'topic': 'love',
        'current_year': str(datetime.now().year)
    }
    
    try:
        crew = WritePoem()
        final_poem = crew.iterate_poem(inputs=inputs, iterations=3)
        print("Final Poem:")
        print(final_poem)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")
    finally:
        # agentops.end_session("Success")
        pass


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "love"
    }
    try:
        WritePoem().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        WritePoem().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "love"
    }
    try:
        WritePoem().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")
