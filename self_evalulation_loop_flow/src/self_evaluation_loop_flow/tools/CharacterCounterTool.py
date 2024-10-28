from typing import Type

from crewai_tools import BaseTool
from pydantic import BaseModel, Field


class CharacterCounterInput(BaseModel):
    """Input schema for CharacterCounterTool."""

    text: str = Field(..., description="The string to count characters in.")


class CharacterCounterTool(BaseTool):
    name: str = "Character Counter Tool"
    description: str = "Counts the number of characters in a given string."
    args_schema: Type[BaseModel] = CharacterCounterInput

    def _run(self, text: str) -> str:
        character_count = len(text)
        return f"The input string has {character_count} characters."
