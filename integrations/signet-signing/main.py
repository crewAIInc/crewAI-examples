"""CrewAI + Signet: Sign every tool call with Ed25519."""

from crewai import Agent, Crew, Task
from crewai.tools import tool
from signet_auth import SigningAgent
from signet_auth.crewai import install_hooks, uninstall_hooks, get_receipts


@tool("search")
def search_tool(query: str) -> str:
    """Search for information."""
    return f"Results for: {query}"


@tool("write_file")
def write_tool(filename: str, content: str) -> str:
    """Write content to a file."""
    return f"Written to {filename}"


def main():
    # 1. Create a Signet identity
    signer = SigningAgent.create("crew-bot", owner="demo", unencrypted=True)

    # 2. Install signing hooks (3 lines!)
    install_hooks(signer, audit=True)

    # 3. Run your crew as usual
    researcher = Agent(
        role="Researcher",
        goal="Find information about AI agent security",
        backstory="You are a security researcher.",
        tools=[search_tool],
    )

    writer = Agent(
        role="Writer",
        goal="Write a summary of the research",
        backstory="You are a technical writer.",
        tools=[write_tool],
    )

    task1 = Task(
        description="Research MCP server security best practices",
        expected_output="A list of security recommendations",
        agent=researcher,
    )

    task2 = Task(
        description="Write a summary of the security research",
        expected_output="A written summary",
        agent=writer,
    )

    crew = Crew(agents=[researcher, writer], tasks=[task1, task2])
    crew.kickoff()

    # 4. Check signed receipts
    receipts = get_receipts()
    print(f"\n{'='*60}")
    print(f"Signed {len(receipts)} tool calls:")
    for r in receipts:
        print(f"  {r.ts}  {r.action.tool}  sig={r.sig[:30]}...")

    # 5. Clean up
    uninstall_hooks()

    print(f"\nVerify with: signet audit --since 1h --verify")


if __name__ == "__main__":
    main()
