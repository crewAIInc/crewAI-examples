from typing import List

from pydantic import BaseModel


class ChapterOutline(BaseModel):
    title: str
    description: str


class BookOutline(BaseModel):
    chapters: List[ChapterOutline]


class Chapter(BaseModel):
    title: str
    content: str
