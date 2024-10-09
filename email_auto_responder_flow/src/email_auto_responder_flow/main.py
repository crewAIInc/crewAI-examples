#!/usr/bin/env python
import asyncio
import time
from typing import List

from crewai.flow.flow import Flow, listen, start
from pydantic import BaseModel

from email_auto_responder_flow.types import Email
from email_auto_responder_flow.utils.emails import check_email, format_emails

from .crews.email_filter_crew.email_filter_crew import EmailFilterCrew


class AutoResponderState(BaseModel):
    emails: List[Email] = []
    checked_emails_ids: set[str] = set()


class EmailAutoResponderFlow(Flow[AutoResponderState]):
    initial_state = AutoResponderState

    @start("generate_draft_responses")
    def fetch_new_emails(self):
        print("Kickoff the Email Filter Crew")
        new_emails, updated_checked_email_ids = check_email(
            checked_emails_ids=self.state.checked_emails_ids
        )

        self.state.emails = new_emails
        self.state.checked_emails_ids = updated_checked_email_ids

    @listen(fetch_new_emails)
    def generate_draft_responses(self):
        print("Current email queue: ", len(self.state.emails))
        if len(self.state.emails) > 0:
            print("Writing New emails")
            emails = format_emails(self.state.emails)

            EmailFilterCrew().crew().kickoff(inputs={"emails": emails})

            self.state.emails = []

        print("Waiting for 180 seconds")
        time.sleep(180)


async def run_flow():
    """
    Run the flow.
    """
    email_auto_response_flow = EmailAutoResponderFlow()
    await email_auto_response_flow.kickoff()


async def plot_flow():
    """
    Plot the flow.
    """
    email_auto_response_flow = EmailAutoResponderFlow()
    email_auto_response_flow.plot()


def main():
    asyncio.run(run_flow())


def plot():
    asyncio.run(plot_flow())


if __name__ == "__main__":
    main()
