#!/usr/bin/env python
import sys
from marketing_posts.crew import MarketingPostsCrew


def run():
    # Replace with your inputs, it will automatically interpolate any tasks and agents information
    inputs = {
        "customer_domain": "nvidia.com/en-in/ai/",
        "project_description": """
nvidia, a leading provider of NIMs, aims to revolutionize marketing automation for its enterprise clients. This project involves developing an innovative marketing strategy to showcase nvidia's NIMs, emphasizing ease of use, scalability, and integration capabilities. The campaign will target tech-savvy decision-makers in medium to large enterprises, highlighting success stories and the transformative potential of nvidia's platform.

Customer Domain: AI and Automation Solutions
Project Overview: Creating a comprehensive marketing campaign to boost awareness and adoption of nvidia's services among enterprise clients.
""",
    }
    MarketingPostsCrew().crew().kickoff(inputs=inputs)


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "customer_domain": "nvidia.com",
        "project_description": """
nvidia, a leading provider of gpus, aims to revolutionize marketing automation for its enterprise clients. This project involves developing an innovative marketing strategy to showcase nvidia's advanced gpu, emphasizing ease of use, scalability, and integration capabilities. The campaign will target tech-savvy decision-makers in medium to large enterprises, highlighting success stories and the transformative potential of nvidia's platform.

Customer Domain: AI and Automation Solutions
Project Overview: Creating a comprehensive marketing campaign to boost awareness and adoption of nvidia's services among enterprise clients.
""",
    }
    try:
        MarketingPostsCrew().crew().train(n_iterations=int(sys.argv[1]), inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")
