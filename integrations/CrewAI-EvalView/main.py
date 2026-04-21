"""CrewAI + EvalView — regression testing example.

Demonstrates how to use EvalView to snapshot and regression-test a CrewAI crew.

Usage:
    # First run: capture baseline
    evalview snapshot --path tests/

    # After changes: check for regressions
    evalview check --path tests/

    # Or run this script directly for a demo:
    python main.py
"""
from __future__ import annotations

import os
import sys


def main() -> None:
    """Run the EvalView regression check against the example crew."""
    try:
        from evalview import gate
    except ImportError:
        print("EvalView is not installed. Run: pip install evalview")
        sys.exit(1)

    try:
        from crew import crew  # noqa: F401
    except ImportError:
        print("Could not import crew. Make sure crew.py is in the current directory.")
        sys.exit(1)

    if not os.environ.get("OPENAI_API_KEY"):
        print("Set OPENAI_API_KEY to run this example.")
        print("  export OPENAI_API_KEY=sk-...")
        sys.exit(1)

    # Run regression check
    result = gate(test_dir="tests/", quick=True)

    if result.passed:
        print(f"All {result.summary.total} tests passed.")
    else:
        print(f"Regressions detected:")
        for diff in result.diffs:
            if not diff.passed:
                print(f"  {diff.status.value}: {diff.test_name}")
                if diff.tool_changes > 0:
                    print(f"    {diff.tool_changes} tool change(s)")
        sys.exit(1)


if __name__ == "__main__":
    main()
