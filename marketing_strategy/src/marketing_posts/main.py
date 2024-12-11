#!/usr/bin/env python
import sys
from marketing_posts.crew import MarketingPostsCrew
import json
import os

def run():
    # Replace with your inputs, it will automatically interpolate any tasks and agents information
    inputs = {
        'customer_domain': 'crewai.com',
        'project_description': """
CrewAI, a leading provider of multi-agent systems, aims to revolutionize marketing automation for its enterprise clients. This project involves developing an innovative marketing strategy to showcase CrewAI's advanced AI-driven solutions, emphasizing ease of use, scalability, and integration capabilities. The campaign will target tech-savvy decision-makers in medium to large enterprises, highlighting success stories and the transformative potential of CrewAI's platform.

Customer Domain: AI and Automation Solutions
Project Overview: Creating a comprehensive marketing campaign to boost awareness and adoption of CrewAI's services among enterprise clients.
"""
    }
    MarketingPostsCrew().crew().kickoff(inputs=inputs)


def run_inputs_file():
    file_dir = os.path.dirname(os.path.abspath(__file__))
    inputs_file_path = os.path.join(file_dir, "../../run_inputs.json")
    with open(inputs_file_path) as fp:
        inputs_list = json.load(fp)["inputs_list"]
    crew = MarketingPostsCrew().crew()
    for inputs in inputs_list:
        print ("#Triggering", inputs)
        crew.kickoff(inputs=inputs)
        print ("#Finished")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        'customer_domain': 'crewai.com',
        'project_description': """
CrewAI, a leading provider of multi-agent systems, aims to revolutionize marketing automation for its enterprise clients. This project involves developing an innovative marketing strategy to showcase CrewAI's advanced AI-driven solutions, emphasizing ease of use, scalability, and integration capabilities. The campaign will target tech-savvy decision-makers in medium to large enterprises, highlighting success stories and the transformative potential of CrewAI's platform.

Customer Domain: AI and Automation Solutions
Project Overview: Creating a comprehensive marketing campaign to boost awareness and adoption of CrewAI's services among enterprise clients.
"""
    }
    try:
        MarketingPostsCrew().crew().train(n_iterations=int(sys.argv[1]), inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")
