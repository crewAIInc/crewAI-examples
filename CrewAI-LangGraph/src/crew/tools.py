from langchain_community.agent_toolkits import GmailToolkit
from langchain_community.tools.gmail.create_draft import GmailCreateDraft
from langchain.tools import tool

class CreateDraftTool():
  @tool("Create Draft")
  def create_draft(data):
    """
    	Useful to create an email draft.
      The input to this tool should be a pipe (|) separated text
      of length 3 (three), representing who to send the email to,
      the subject of the email and the actual message.
      For example, `lorem@ipsum.com|Nice To Meet You|Hey it was great to meet you.`.
    """
    email, subject, message = data.split('|')
    gmail = GmailToolkit()
    draft = GmailCreateDraft(api_resource=gmail.api_resource)
    resutl = draft({
				'to': [email],
				'subject': subject,
				'message': message
		})
    return f"\nDraft created: {resutl}\n"



