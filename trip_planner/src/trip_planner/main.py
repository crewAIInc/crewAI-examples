#!/usr/bin/env python
from trip_planner.crew import TripPlannerCrew


def run():
    # Replace with your inputs, it will automatically interpolate any tasks and agents information
    inputs = {
        'topic': 'AI LLMs'
    }
    TripPlannerCrew().crew().kickoff(inputs=inputs)