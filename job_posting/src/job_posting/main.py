#!/usr/bin/env python
from job_posting.crew import JobPostingCrew


def run():
    # Replace with your inputs, it will automatically interpolate any tasks and agents information
    inputs = {
        'topic': 'AI LLMs'
    }
    JobPostingCrew().crew().kickoff(inputs=inputs)