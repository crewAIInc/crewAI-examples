"""CrewAI agent with Decision Anchor MCP integration.

Connects CrewAI agents to Decision Anchor's remote MCP server
using MCPServerAdapter for external accountability proof.

Use case: a crew handling delegated tasks records each handoff
boundary via DA, so that responsibility disputes between agents
have externally-anchored proof.

Requirements:
    pip install crewai crewai-tools[mcp]

Usage:
    export OPENAI_API_KEY=your_key
    python main.py
"""

from crewai import Agent, Crew, Process, Task

from crewai_tools import MCPServerAdapter

# Decision Anchor's remote MCP server — no API key needed
da_server_params = {
    "url": "https://mcp.decision-anchor.com/mcp",
    "transport": "streamable_http",
}


def main():
    with MCPServerAdapter(da_server_params) as da_tools:
        accountability_agent = Agent(
            role="Accountability Recorder",
            goal=(
                "Record decision boundaries for actions "
                "that involve external effects"
            ),
            backstory=(
                "You ensure that every payment, delegation, or "
                "external action has its accountability scope "
                "recorded externally via Decision Anchor. "
                "This protects the team when disputes arise later."
            ),
            tools=da_tools,
            verbose=True,
        )

        record_task = Task(
            description=(
                "1. Register as a new agent on Decision Anchor "
                "with name 'crewai-demo-agent'. "
                "2. Create a Decision Declaration (DD) with "
                "action_type 'execute' and summary "
                "'Delegated data processing task to specialist agent'. "
                "Use retention short, integrity basic, "
                "disclosure internal, responsibility minimal. "
                "3. Report the DD ID and anchored timestamp."
            ),
            expected_output=(
                "DD ID and timestamp confirming the decision "
                "was externally anchored."
            ),
            agent=accountability_agent,
        )

        crew = Crew(
            agents=[accountability_agent],
            tasks=[record_task],
            process=Process.sequential,
            verbose=True,
        )

        result = crew.kickoff()
        print("\n=== Result ===")
        print(result)


if __name__ == "__main__":
    main()
