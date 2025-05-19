from crewai_tools import MCPServerAdapter, FileReadTool
from src.gestell_mcp import server_params
from src.crews.research import GestellResearchCrew
from pathlib import Path

collection_file = Path.cwd() / "agent/collection.md"

with MCPServerAdapter(server_params) as tools:
    filtered_tools = [
        tool
        for tool in tools
        if hasattr(tool, "name")
        and tool.name in ["promptCollectionSimple", "searchCollectionSimple"]
    ]

    result = (
        GestellResearchCrew(
            tools=filtered_tools + [FileReadTool(file_path=str(collection_file))]
        )
        .crew()
        .kickoff()
    )
    print(result)
