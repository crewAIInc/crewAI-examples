#!/usr/bin/env python
import asyncio
import csv
import os
from typing import List

from crewai.flow.flow import Flow, listen, start
from pydantic import BaseModel

from meeting_assistant_flow.crews.meeting_assistant_crew.meeting_assistant_crew import (
    MeetingAssistantCrew,
)
from meeting_assistant_flow.types import MeetingTask
from meeting_assistant_flow.utils.slack_helper import send_message_to_channel
from meeting_assistant_flow.utils.trello_helper import save_tasks_to_trello


class MeetingState(BaseModel):
    transcript: str = "Meeting transcript goes here"
    tasks: List[MeetingTask] = []


class MeetingFlow(Flow[MeetingState]):
    initial_state = MeetingState

    @start()
    def load_meeting_notes(self):
        print("Loading Meeting Notes")
        print("Current working directory:", os.getcwd())

        with open("meeting_notes.txt", "r") as file:
            self.state.transcript = file.read()

    @listen(load_meeting_notes)
    def generate_tasks_from_meeting_transcript(self):
        print("Kickoff the Meeting Assistant Crew")
        output = (
            MeetingAssistantCrew()
            .crew()
            .kickoff(inputs={"transcript": self.state.transcript})
        )

        tasks = output["tasks"]
        print("TASKS:", tasks)
        self.state.tasks = tasks

    @listen(generate_tasks_from_meeting_transcript)
    def add_tasks_to_trello(self):
        print("Adding Tasks to Trello")
        save_tasks_to_trello(self.state.tasks)

    @listen(generate_tasks_from_meeting_transcript)
    def save_new_tasks_to_csv(self):
        print("Saving New Tasks to CSV")
        with open("new_tasks.csv", "w", newline="") as file:
            writer = csv.writer(file)
            # Write the header row
            writer.writerow(["Name", "Description"])
            # Write the task data
            for task in self.state.tasks:
                writer.writerow([task.name, task.description])

    @listen(generate_tasks_from_meeting_transcript)
    def send_slack_notification(self):
        print("Sending Slack Notification")
        message = f"{len(self.state.tasks)} New tasks have been added to Trello!"
        send_message_to_channel(message)


async def run_flow():
    """
    Run the flow.
    """
    meeting_flow = MeetingFlow()
    meeting_flow.kickoff()


async def plot_flow():
    """
    Plot the flow.
    """
    meeting_flow = MeetingFlow()
    meeting_flow.plot()


def main():
    asyncio.run(run_flow())


def plot():
    asyncio.run(plot_flow())


if __name__ == "__main__":
    main()
