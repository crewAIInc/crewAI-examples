from dotenv import load_dotenv
load_dotenv()

from langgraph.graph import StateGraph

from .state import EmailsState
from .nodes import Nodes
from .crew.crew import EmailFilterCrew

class WorkFlow():
	def __init__(self):
		nodes = Nodes()
		workflow = StateGraph(EmailsState)

		workflow.add_node("check_new_emails", nodes.check_email)
		workflow.add_node("wait_next_run", nodes.wait_next_run)
		workflow.add_node("draft_responses", EmailFilterCrew().kickoff)

		workflow.set_entry_point("check_new_emails")
		workflow.add_conditional_edges(
				"check_new_emails",
				nodes.new_emails,
				{
					"continue": 'draft_responses',
					"end": 'wait_next_run'
				}
		)
		workflow.add_edge('draft_responses', 'wait_next_run')
		workflow.add_edge('wait_next_run', 'check_new_emails')
		self.app = workflow.compile()