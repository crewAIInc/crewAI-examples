import os
import sys
from pathlib import Path
import pytest

# Allow running tests directly without package installation: add subproject src to sys.path
# tests/ is at crews/agentbay_sdk/tests/, so we need to go up 1 level to get to crews/agentbay_sdk/
# Then add src/ to get to crews/agentbay_sdk/src/ where the package is located
PROJECT_ROOT = Path(__file__).resolve().parent.parent  # crews/agentbay_sdk/
PROJECT_SRC = PROJECT_ROOT / "src"  # crews/agentbay_sdk/src/
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from agentbay_sdk.crew import AgentBayTemporaryCodeCrew


@pytest.mark.skipif(
    not os.getenv("AGENTBAY_API_KEY") or not os.getenv("OPENAI_API_KEY"),
    reason="AGENTBAY_API_KEY or OPENAI_API_KEY not set"
)
def test_run_python_code_flow():
    """Start an Agent that uses Tool to execute simple Python code in the cloud.

    This test requires:
    - AGENTBAY_API_KEY: for AgentBay SDK to create sessions
    - OPENAI_API_KEY: for CrewAI Agent to make LLM decisions
    """
    inputs = {
        "code": "print('hello from agentbay')",
        "language": "python",
    }

    # Use AgentBayTemporaryCodeCrew for simple code execution
    crew = AgentBayTemporaryCodeCrew().crew()
    result = crew.kickoff(inputs=inputs)
    assert "hello from agentbay" in str(result)


# Allow running tests directly with python3 command
if __name__ == "__main__":
    import traceback

    # Check environment variables
    missing_vars = []
    if not os.getenv("AGENTBAY_API_KEY"):
        missing_vars.append("AGENTBAY_API_KEY")
    if not os.getenv("OPENAI_API_KEY"):
        missing_vars.append("OPENAI_API_KEY")

    if missing_vars:
        print("❌ Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set them before running tests:")
        print("  export AGENTBAY_API_KEY=your_agentbay_api_key")
        print("  export OPENAI_API_KEY=your_openai_api_key")
        sys.exit(1)

    print("=" * 60)
    print("Running AgentBay Code Flow Test")
    print("=" * 60)
    print(f"✅ AGENTBAY_API_KEY: {'*' * min(20, len(os.getenv('AGENTBAY_API_KEY', '')))}")
    print(f"✅ OPENAI_API_KEY: {'*' * min(20, len(os.getenv('OPENAI_API_KEY', '')))}")
    print()

    # Run the test
    print("Running: Python Code Flow Test...", end=" ")
    try:
        test_run_python_code_flow()
        print("✅ PASSED")
        print()
        print("=" * 60)
        print("Test Summary")
        print("=" * 60)
        print("✅ Passed:  1")
        print("❌ Failed:  0")
        print("📊 Total:   1")
        print("=" * 60)
        print("🎉 All tests passed!")
        sys.exit(0)
    except AssertionError as e:
        print("❌ FAILED")
        print(f"   AssertionError: {e}")
        print()
        print("=" * 60)
        print("Test Summary")
        print("=" * 60)
        print("✅ Passed:  0")
        print("❌ Failed:  1")
        print("📊 Total:   1")
        print("=" * 60)
        sys.exit(1)
    except Exception as e:
        print("❌ ERROR")
        print(f"   {type(e).__name__}: {e}")
        traceback.print_exc()
        print()
        print("=" * 60)
        print("Test Summary")
        print("=" * 60)
        print("✅ Passed:  0")
        print("❌ Failed:  1")
        print("📊 Total:   1")
        print("=" * 60)
        sys.exit(1)
