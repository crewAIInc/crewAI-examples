#!/usr/bin/env python
import sys
from surprise_travel.crew import SurpriseTravelCrew


def run():
    # Replace with your inputs, it will automatically interpolate any tasks and agents information
    inputs = {
        'origin': 'São Paulo, GRU',
        'destination': 'New York, JFK',
        'age': 31,
        'hotel_location': 'Brooklyn',
        'flight_information': 'GOL 1234, leaving at June 30th, 2024, 10:00',
        'trip_duration': '14 days'
    }
    result = SurpriseTravelCrew().crew().kickoff(inputs=inputs)
    print(result)


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        'origin': 'São Paulo, GRU',
        'destination': 'New York, JFK',
        'age': 31,
        'hotel_location': 'Brooklyn',
        'flight_information': 'GOL 1234, leaving at June 30th, 2024, 10:00',
        'trip_duration': '14 days'
    }
    try:
        SurpriseTravelCrew().crew().train(n_iterations=int(sys.argv[1]), inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")
