from crewai_tools import MCPServerAdapter
from src.gestell_mcp import server_params
from src.crews.create import GestellCreateCrew

with MCPServerAdapter(server_params) as tools:
    result = GestellCreateCrew(tools=tools).crew().kickoff()
    print(result)
