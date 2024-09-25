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

    @start("wait_next_run")
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

    @listen(generate_draft_responses)
    def save_to_a_excel(self):
        print("Saving to excel")

        pass


async def run():
    """
    Run the flow.
    """
    email_auto_response_flow = EmailAutoResponderFlow()
    await email_auto_response_flow.kickoff()


def main():
    asyncio.run(run())
    # emails = """
    #     EMAILS ID: 191fb61dc03a7c47
    #     - Thread ID: 191fb10965995fa5
    #     - Snippet: @monami44 pushed 1 commit. ba31f59 simple stuck, lock — View it on GitHub or unsubscribe. You are receiving this because you are subscribed to this thread. Message ID: &lt;bhancockio/fullstack-ai-
    #     - From: Maksym <notifications@github.com>
    #     --------
    #     ID: 191fb22a49692a31
    #     - Thread ID: 191fb22a49692a31
    #     - Snippet: Hi Brandon, I&#39;m excited to share something revolutionary in the AI space with you. Our latest video dives deep into the capabilities of advanced AI bots and how they can transform your business.
    #     - From: James Hurst <james@jameshurst.ddxweb.com>
    #     --------
    #     ID: 191f856c481fc45b
    #     - Thread ID: 191f7338692ab387
    #     - Snippet: Meeting summary with AI Companion now supports additional languages in preview. Learn More Meeting summary for Brandon Hancock&#39;s Zoom Meeting (09/16/2024) Quick recap Brandon and Maksym discussed
    #     - From: Meeting Summary with AI Companion <no-reply@zoom.us>
    #     --------
    # """

    # EmailFilterCrew().crew().kickoff(inputs={"emails": emails})


if __name__ == "__main__":
    main()
