"""DevOps governance crew.

A CrewAI crew that demonstrates SidClaw governance across three tools
with different risk profiles:
  - check_service_health  → allow
  - deploy_to_production  → approval_required
  - run_db_migration      → deny
"""

import os
from typing import Any

from crewai import Agent, Crew, Task
from crewai.tools import BaseTool
from dotenv import load_dotenv

from sidclaw import ActionDeniedError, SidClaw
from sidclaw.middleware.crewai import govern_crewai_tool

load_dotenv()


# ---------------------------------------------------------------------------
# SidClaw client
# ---------------------------------------------------------------------------

sidclaw = SidClaw(
    api_key=os.environ["SIDCLAW_API_KEY"],
    agent_id=os.environ.get("SIDCLAW_AGENT_ID", "devops-crew"),
    api_url=os.environ.get("SIDCLAW_API_URL", "https://api.sidclaw.com"),
)


# ---------------------------------------------------------------------------
# Tools (undecorated — governance is added via govern_crewai_tool)
# ---------------------------------------------------------------------------

class CheckServiceHealthTool(BaseTool):
    name: str = "check_service_health"
    description: str = "Check the health of all production services."

    def _run(self, **kwargs: Any) -> str:
        # In production: call your health-check endpoint
        return "All services healthy. API: OK, DB: OK, Cache: OK"


class DeployToProductionTool(BaseTool):
    name: str = "deploy_to_production"
    description: str = "Deploy the latest build to the production environment."

    def _run(self, version: str = "latest", **kwargs: Any) -> str:
        # In production: trigger your CI/CD pipeline
        return f"Deployed version {version} to production successfully."


class RunDbMigrationTool(BaseTool):
    name: str = "run_db_migration"
    description: str = "Run pending database migrations against the production database."

    def _run(self, migration_id: str = "all", **kwargs: Any) -> str:
        # In production: execute migrations
        return f"Migration {migration_id} completed."


# ---------------------------------------------------------------------------
# Apply governance
#
# govern_crewai_tool wraps the tool's _run method. Before execution, SidClaw
# evaluates the action against your policies. The data_classification hint
# influences which policy rules apply.
# ---------------------------------------------------------------------------

health_tool = govern_crewai_tool(
    CheckServiceHealthTool(),
    client=sidclaw,
    data_classification="internal",
)

deploy_tool = govern_crewai_tool(
    DeployToProductionTool(),
    client=sidclaw,
    data_classification="confidential",
)

migration_tool = govern_crewai_tool(
    RunDbMigrationTool(),
    client=sidclaw,
    data_classification="restricted",
)


# ---------------------------------------------------------------------------
# Agent and crew
# ---------------------------------------------------------------------------

devops_agent = Agent(
    role="DevOps Engineer",
    goal="Ensure services are healthy, deploy the latest build, and run any pending migrations.",
    backstory=(
        "You are a senior DevOps engineer responsible for maintaining production reliability. "
        "All deployment and database actions require governance approval."
    ),
    tools=[health_tool, deploy_tool, migration_tool],
    verbose=True,
)

devops_task = Task(
    description=(
        "1. Check all service health.\n"
        "2. Deploy the latest build to production.\n"
        "3. Run any pending database migrations."
    ),
    expected_output="A summary of each action taken and its outcome.",
    agent=devops_agent,
)


def build_crew() -> Crew:
    return Crew(agents=[devops_agent], tasks=[devops_task], verbose=True)
