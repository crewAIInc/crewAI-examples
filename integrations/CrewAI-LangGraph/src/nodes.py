import os
import time

from langchain_community.agent_toolkits import GmailToolkit
from langchain_community.tools.gmail.search import GmailSearch

class Nodes():
	def __init__(self):
		self.gmail = GmailToolkit()

	def check_email(self, state):
		print("# Checking for new emails")
		search = GmailSearch(api_resource=self.gmail.api_resource)
		emails = search('after:newer_than:1d')
		checked_emails = state['checked_emails_ids'] if state['checked_emails_ids'] else []
		thread = []
		new_emails = []
		for email in emails:
			if (email['id'] not in checked_emails) and (email['threadId'] not in thread) and ( os.environ['MY_EMAIL'] not in email['sender']):
				thread.append(email['threadId'])
				new_emails.append(
					{
						"id": email['id'],
						"threadId": email['threadId'],
						"snippet": email['snippet'],
						"sender": email["sender"]
					}
				)
		checked_emails.extend([email['id'] for email in emails])
		return {
			**state,
			"emails": new_emails,
			"checked_emails_ids": checked_emails
		}

	def wait_next_run(self, state):
		print("## Waiting for 180 seconds")
		time.sleep(180)
		return state

	def new_emails(self, state):
		if len(state['emails']) == 0:
			print("## No new emails")
			return "end"
		else:
			print("## New emails")
			return "continue"

