"""
WritBase Task Backend for CrewAI

Fetches tasks assigned to this agent from WritBase, processes them with a
CrewAI crew (researcher + writer), and writes results back.

Usage:
    cp .env.example .env   # fill in your values
    pip install -r requirements.txt
    python main.py
"""

import json
import sys

import httpx
from crewai import Agent, Crew, Process, Task
from dotenv import load_dotenv
import os

load_dotenv()

WRITBASE_URL = os.environ["WRITBASE_URL"]
WRITBASE_AGENT_KEY = os.environ["WRITBASE_AGENT_KEY"]
MCP_ENDPOINT = f"{WRITBASE_URL}/functions/v1/mcp-server"


# ---------------------------------------------------------------------------
# WritBase MCP helpers
# ---------------------------------------------------------------------------

def mcp_call(method: str, params: dict, request_id: int = 1) -> dict:
    """Send a JSON-RPC 2.0 request to the WritBase MCP endpoint."""
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": request_id,
    }
    headers = {
        "Content-Type": "application/json",
        "X-Agent-Key": WRITBASE_AGENT_KEY,
    }
    response = httpx.post(MCP_ENDPOINT, json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    result = response.json()
    if "error" in result:
        raise RuntimeError(f"MCP error: {result['error']}")
    return result.get("result", {})


def fetch_todo_tasks() -> list[dict]:
    """Fetch tasks assigned to this agent with status 'todo'."""
    result = mcp_call(
        method="tools/call",
        params={
            "name": "get_tasks",
            "arguments": {"status": "todo", "assigned_to_me": True},
        },
    )
    # MCP tool results come as content blocks; parse the text block
    content = result.get("content", [])
    for block in content:
        if block.get("type") == "text":
            data = json.loads(block["text"])
            return data.get("tasks", data) if isinstance(data, dict) else data
    return []


def update_task(task_id: str, version: int, status: str, notes: str) -> dict:
    """Update a task's status and notes in WritBase."""
    return mcp_call(
        method="tools/call",
        params={
            "name": "update_task",
            "arguments": {
                "task_id": task_id,
                "version": version,
                "status": status,
                "notes": notes,
            },
        },
    )


# ---------------------------------------------------------------------------
# CrewAI crew definition
# ---------------------------------------------------------------------------

researcher = Agent(
    role="Researcher",
    goal="Analyze the task description and gather key information",
    backstory=(
        "You are a meticulous researcher who breaks down task descriptions "
        "into actionable insights. You identify what needs to be done and "
        "gather the relevant context."
    ),
    verbose=True,
)

writer = Agent(
    role="Writer",
    goal="Produce a clear, concise result summary for the task",
    backstory=(
        "You are a skilled writer who takes research findings and produces "
        "well-structured summaries. You focus on clarity and actionability."
    ),
    verbose=True,
)


def build_crew(task_description: str) -> Crew:
    """Build a CrewAI crew to process a single WritBase task."""
    research_task = Task(
        description=(
            f"Analyze the following task and identify the key requirements, "
            f"constraints, and any relevant context:\n\n{task_description}"
        ),
        expected_output="A structured analysis of the task requirements.",
        agent=researcher,
    )

    writing_task = Task(
        description=(
            "Based on the research analysis, produce a clear and actionable "
            "result summary. Include specific recommendations or deliverables."
        ),
        expected_output="A concise result summary with actionable items.",
        agent=writer,
    )

    return Crew(
        agents=[researcher, writer],
        tasks=[research_task, writing_task],
        process=Process.sequential,
        verbose=True,
    )


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def main():
    print("Fetching tasks from WritBase...")
    tasks = fetch_todo_tasks()

    if not tasks:
        print("No tasks assigned. Nothing to do.")
        return

    print(f"Found {len(tasks)} task(s) to process.\n")

    for wb_task in tasks:
        task_id = wb_task["id"]
        version = wb_task["version"]
        description = wb_task.get("description", "(no description)")

        print(f"--- Processing task: {description[:60]} (id: {task_id}) ---")

        # Mark as in_progress (version increments after each update)
        update_task(task_id, version=version, status="in_progress", notes="CrewAI processing started")
        version += 1

        try:
            crew = build_crew(description)
            result = crew.kickoff()

            # Write result back to WritBase
            update_task(task_id, version=version, status="done", notes=str(result))
            print(f"Task {task_id} completed.\n")

        except Exception as exc:
            error_msg = f"CrewAI processing failed: {exc}"
            update_task(task_id, version=version, status="failed", notes=error_msg)
            print(f"Task {task_id} failed: {exc}\n", file=sys.stderr)


if __name__ == "__main__":
    main()
