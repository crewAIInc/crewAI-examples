#!/usr/bin/env python3
"""
Example script for running AgentBayCodeCrew

Usage:
1. Ensure environment variables are set (see instructions below)
2. Modify tasks and input parameters as needed
3. Run: python3 main.py
"""

import os
import sys
from pathlib import Path

# Add project root to path if needed
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentbay_sdk.crew import AgentBayCodeCrew, AgentBayTemporaryCodeCrew


def run_simple_code_task():
    """Example 1: Run a simple code execution task using AgentBayTemporaryCodeCrew"""
    print("=" * 60)
    print("Example 1: Code Execution Task")
    print("=" * 60)

    # Input parameters
    code = "print('Hello from AgentBay!')"
    language = "python"

    print(f"Code: {code}")
    print(f"Language: {language}")
    print("\nStarting execution...")

    # Use AgentBayTemporaryCodeCrew to execute code
    # This approach executes through CrewAI Agent, leveraging LLM decision-making capabilities
    try:
        crew = AgentBayTemporaryCodeCrew().crew()
        inputs = {
            "code": code,
            "language": language,
        }
        result = crew.kickoff(inputs=inputs)
        print(f"\n✅ Execution successful!")
        print(f"Execution result:\n{result}")
    except Exception as e:
        print(f"\n❌ Execution failed: {e}")
        import traceback
        traceback.print_exc()


def run_full_development_pipeline():
    """Example 2: Run the full development pipeline (requirements → design → implementation → deployment → execution → analysis)"""
    import sys
    from datetime import datetime

    # Create output file
    output_dir = Path(__file__).parent / "pipeline_outputs"
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"pipeline_execution_{timestamp}.log"

    # Create a class that outputs to both console and file
    class TeeOutput:
        def __init__(self, *files):
            self.files = files

        def write(self, obj):
            for f in self.files:
                f.write(obj)
                f.flush()

        def flush(self):
            for f in self.files:
                f.flush()

    # Open log file
    log_file = open(output_file, 'w', encoding='utf-8')

    # Save original stdout
    original_stdout = sys.stdout

    # Set output to both console and file
    sys.stdout = TeeOutput(sys.stdout, log_file)

    try:
        print("=" * 60)
        print("Example 2: Full Development Pipeline")
        print(f"📝 Output will be saved to: {output_file}")
        print("=" * 60)

        # Create Crew - need to create a Crew with only development pipeline tasks
        # because crew() includes all tasks, including run_code_task (which requires language parameter)
        from crewai import Crew, Process

        crew_base = AgentBayCodeCrew()

        # Create Crew with only development pipeline tasks
        dev_crew = Crew(
            agents=[
                crew_base.framework_designer(),  # For project design
                crew_base.implementer(),  # For code generation
                crew_base.code_executor(),  # For upload and execution
                crew_base.result_analyst(),  # For result analysis
            ],
            tasks=[
                crew_base.design_project(),  # Combined task: requirements analysis + framework design
                crew_base.generate_project(),
                crew_base.upload_project(),
                crew_base.install_and_run(),
                crew_base.analyze_result(),
            ],
            process=Process.sequential,
            verbose=True,
        )

        # User requirements
        user_requirement = """
        Develop a simple Python Web API service with the following features:
        1. GET /health - Health check endpoint, returns {"status": "ok"}
        2. GET /hello - Returns greeting {"message": "Hello, World!"}
        3. POST /echo - Receives JSON data and echoes it back
        Use FastAPI framework, include requirements.txt file.
        Important: The service must run on port 30123 (must be in range [30100, 30199]), bound to 0.0.0.0 instead of 127.0.0.1.
        Ensure the code can run properly.
        """

        print(f"📝 User Requirements:\n{user_requirement}\n")
        print("=" * 60)

        # Note: CrewAI's sequential mode will execute all tasks in order
        # Each task uses the output from the previous task as context
        # We only need to provide input parameters required by the first task
        print("\nStarting full development pipeline execution...")
        print("CrewAI will execute in order: Project Design → Code Generation → Upload → Install & Run → Result Analysis")
        print("-" * 60)

        # Provide initial inputs (only parameters needed by the first task)
        inputs = {"user_requirement": user_requirement}

        print("\n🚀 Starting Crew execution...\n")
        final_result = dev_crew.kickoff(inputs=inputs)

        print("\n" + "=" * 60)
        print("✅ Full development pipeline execution completed!")
        print("=" * 60)
        print(f"\n📊 Final Result:\n{final_result}")
        print("\n" + "=" * 60)
        print(f"💾 Complete output saved to: {output_file}")
        print("=" * 60)
    finally:
        # Restore original stdout
        sys.stdout = original_stdout
        log_file.close()
        print(f"\n💾 Execution log saved to: {output_file}")


def check_environment():
    """Check if the runtime environment is configured correctly"""
    print("=" * 60)
    print("Environment Check")
    print("=" * 60)

    required_vars = {
        "AGENTBAY_API_KEY": "AgentBay cloud execution API key",
        "OPENAI_API_KEY": "LLM API key (OpenAI/Bailian/Azure)",
    }

    missing = []
    for var, desc in required_vars.items():
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * min(20, len(value))} ({desc})")
        else:
            print(f"❌ {var}: Not set ({desc})")
            missing.append(var)

    optional_vars = {
        "OPENAI_API_BASE": "LLM API endpoint (optional, for Bailian/custom endpoints)",
        "OPENAI_MODEL_NAME": "LLM model name (optional, default: gpt-4o-mini)",
    }

    print("\nOptional Configuration:")
    for var, desc in optional_vars.items():
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: {value}")
        else:
            print(f"  ⚠️  {var}: Not set ({desc})")

    if missing:
        print(f"\n❌ Missing required environment variables: {', '.join(missing)}")
        print("\nPlease create .env file and configure:")
        print("  1. cp env.example .env")
        print("  2. Edit .env file and fill in your API keys")
        return False

    print("\n✅ Environment configuration check passed!")
    return True


def run():
    """Default run function for poetry script entry point."""
    from dotenv import load_dotenv
    load_dotenv()

    # Check environment
    if not check_environment():
        sys.exit(1)

    # Run simple code task by default
    run_simple_code_task()


if __name__ == "__main__":
    # Load .env file
    from dotenv import load_dotenv
    load_dotenv()

    # Check environment
    if not check_environment():
        sys.exit(1)

    print("\n")

    # Select example to run
    print("Please select an example to run:")
    print("1. Simple code execution task (run_code_task)")
    print("2. Full development pipeline (all tasks)")
    print("3. Environment check only")

    choice = input("\nEnter option (1/2/3, default 1): ").strip() or "1"

    try:
        if choice == "1":
            run_simple_code_task()
        elif choice == "2":
            run_full_development_pipeline()
        elif choice == "3":
            print("Environment check completed")
        else:
            print(f"Invalid option: {choice}")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Execution error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

