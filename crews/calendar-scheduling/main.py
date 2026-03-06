import os

from crewai import Crew
from crewai_tools import MCPServerAdapter
from dotenv import load_dotenv

from agents import CalendarAgents
from tasks import CalendarTasks

load_dotenv()

# --- Configuration ---
MEETING_TIME = "next Tuesday at 2pm"
MEETING_TITLE = "Team Sync"

# Stdio transport — runs the MCP server locally via npx.
# Authenticate first: npx @temporal-cortex/cortex-mcp auth google
SERVER_PARAMS = {
    "command": "npx",
    "args": ["-y", "@temporal-cortex/cortex-mcp"],
    "env": {
        "GOOGLE_CLIENT_ID": os.getenv("GOOGLE_CLIENT_ID", ""),
        "GOOGLE_CLIENT_SECRET": os.getenv("GOOGLE_CLIENT_SECRET", ""),
        "TIMEZONE": os.getenv("TIMEZONE", ""),
    },
}

# For Platform Mode (managed, no Node.js required), replace SERVER_PARAMS:
# SERVER_PARAMS = {
#     "url": "https://mcp.temporal-cortex.com/mcp",
#     "transport": "sse",
#     "headers": {
#         "Authorization": f"Bearer {os.getenv('TEMPORAL_CORTEX_API_KEY', '')}",
#     },
# }


def main():
    print("## Welcome to the Calendar Scheduling Crew")
    print("-------------------------------------------")

    with MCPServerAdapter(SERVER_PARAMS) as tools:
        print(f"Connected to Temporal Cortex — {len(tools)} tools discovered\n")

        agents = CalendarAgents()
        calendar_tasks = CalendarTasks()

        # Create agents
        temporal_analyst = agents.temporal_analyst(tools)
        calendar_manager = agents.calendar_manager(tools)
        coordinator = agents.scheduling_coordinator(tools)

        # Create tasks with dependencies
        orient = calendar_tasks.orient_in_time(temporal_analyst, MEETING_TIME)
        availability = calendar_tasks.find_availability(calendar_manager)
        booking = calendar_tasks.book_meeting(coordinator, MEETING_TITLE)

        availability.context = [orient]
        booking.context = [orient, availability]

        crew = Crew(
            agents=[temporal_analyst, calendar_manager, coordinator],
            tasks=[orient, availability, booking],
            verbose=True,
        )

        result = crew.kickoff()

        print("\n\n################################################")
        print("## Here is the result")
        print("################################################\n")
        print(result)


if __name__ == "__main__":
    main()
