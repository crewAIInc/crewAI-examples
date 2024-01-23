import datetime
from typing import TypedDict

class EmailsState(TypedDict):
	checked_emails_ids: list[str]
	emails: list[dict]
	action_required_emails: dict