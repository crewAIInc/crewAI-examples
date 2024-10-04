from pydantic import BaseModel


class Email(BaseModel):
    id: str
    threadId: str
    snippet: str
    sender: str
