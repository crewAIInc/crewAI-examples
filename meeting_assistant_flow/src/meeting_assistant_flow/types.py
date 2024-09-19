from pydantic import BaseModel


class MeetingTask(BaseModel):
    name: str
    description: str


class MeetingTaskList(BaseModel):
    tasks: list[MeetingTask]
