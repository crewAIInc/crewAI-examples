import os
import time
from typing import List

from langchain_community.agent_toolkits import GmailToolkit
from langchain_community.tools.gmail.search import GmailSearch

from email_auto_responder_flow.types import Email


def check_email(checked_emails_ids: set[str]) -> tuple[list[Email], set[str]]:
    print("# Checking for new emails")

    gmail = GmailToolkit()
    search = GmailSearch(api_resource=gmail.api_resource)
    emails = search("after:newer_than:1d")
    thread = []
    new_emails: List[Email] = []
    for email in emails:
        if (
            (email["id"] not in checked_emails_ids)
            and (email["threadId"] not in thread)
            and (os.environ["MY_EMAIL"] not in email["sender"])
        ):
            thread.append(email["threadId"])
            new_emails.append(
                {
                    "id": email["id"],
                    "threadId": email["threadId"],
                    "snippet": email["snippet"],
                    "sender": email["sender"],
                }
            )
    checked_emails_ids.update([email["id"] for email in emails])
    return new_emails, checked_emails_ids


def wait_next_run(state):
    print("## Waiting for 180 seconds")
    time.sleep(180)
    return state


def new_emails(state):
    if len(state["emails"]) == 0:
        print("## No new emails")
        return "end"
    else:
        print("## New emails")
        return "continue"


def format_emails(emails):
    emails_string = []
    for email in emails:
        print(email)
        arr = [
            f"ID: {email['id']}",
            f"- Thread ID: {email['threadId']}",
            f"- Snippet: {email['snippet']}",
            f"- From: {email['sender']}",
            "--------",
        ]
        emails_string.append("\n".join(arr))
    return "\n".join(emails_string)
