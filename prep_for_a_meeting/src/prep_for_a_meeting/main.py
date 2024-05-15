#!/usr/bin/env python
from prep_for_a_meeting.crew import PrepForAMeetingCrew


def run():
    # Replace with your inputs, it will automatically interpolate any tasks and agents information
    inputs = {
        'topic': 'AI LLMs'
    }
    PrepForAMeetingCrew().crew().kickoff(inputs=inputs)