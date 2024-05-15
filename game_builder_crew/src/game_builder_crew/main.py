#!/usr/bin/env python
from game_builder_crew.crew import GameBuilderCrewCrew


def run():
    # Replace with your inputs, it will automatically interpolate any tasks and agents information
    inputs = {
        'topic': 'AI LLMs'
    }
    GameBuilderCrewCrew().crew().kickoff(inputs=inputs)