from pydantic import BaseModel


class MeetingTask(BaseModel):
    name: str
    desc: str


class MeetingTaskList(BaseModel):
    tasks: list[MeetingTask]
