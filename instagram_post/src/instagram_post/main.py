#!/usr/bin/env python
from instagram_post.crew import InstagramPostCrew


def run():
    # Replace with your inputs, it will automatically interpolate any tasks and agents information
    inputs = {
        'topic': 'AI LLMs'
    }
    InstagramPostCrew().crew().kickoff(inputs=inputs)