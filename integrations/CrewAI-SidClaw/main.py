"""Entry point for the CrewAI + SidClaw governance example.

Run:
    python main.py
"""

from sidclaw import ActionDeniedError
from crew import build_crew


if __name__ == "__main__":
    crew = build_crew()

    try:
        result = crew.kickoff()
        print("\n--- Crew result ---")
        print(result)
    except ActionDeniedError as e:
        print(f"\n[SidClaw] Action blocked by policy: {e}")
        print("Check the audit trace at https://app.sidclaw.com/dashboard/audit")
