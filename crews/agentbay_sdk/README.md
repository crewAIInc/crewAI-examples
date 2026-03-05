# AI Crew for AgentBay SDK Integration

## Introduction

This project demonstrates the use of the CrewAI framework integrated with `wuying-agentbay-sdk` to automate cloud code execution and full development workflows. CrewAI orchestrates autonomous AI agents, enabling them to collaborate and execute complex tasks efficiently in secure cloud environments.

- [CrewAI Framework](#crewai-framework)
- [Running the Script](#running-the-script)
- [Details & Explanation](#details--explanation)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [Support and Contact](#support-and-contact)
- [License](#license)

## CrewAI Framework

CrewAI is designed to facilitate the collaboration of role-playing AI agents. In this example, these agents work together to:
- Execute code in secure cloud environments
- Design and implement complete projects
- Deploy and run services in the cloud
- Analyze execution results

## Running the Script

It uses GPT-4o by default so you should have access to that to run it.

***Disclaimer:** This will use gpt-4o unless you change it to use a different model, and by doing so it may incur in different costs.*

- **Configure Environment**: Copy `.env.example` to `.env` and set up the environment variables:
  - `AGENTBAY_API_KEY`: Your AgentBay cloud execution API key
  - `OPENAI_API_KEY`: Your LLM API key
  - `OPENAI_API_BASE`: (Optional) LLM API endpoint for custom providers
  - `OPENAI_MODEL_NAME`: (Optional) LLM model name, default is `gpt-4o-mini`
- **Install Dependencies**: Run `poetry lock && poetry install` (or use `uv`/`pip`).
- **Customize**: Modify `main.py` to add custom inputs for your agents and tasks.
- **Customize Further**: Check `config/agents.yaml` to update your agents and `config/tasks.yaml` to update your tasks.
- **Execute the Script**: Run `python main.py` and follow the prompts.

## Details & Explanation

- **Running the Script**: Execute `python main.py`. The script provides two modes:
  1. Simple code execution task - Execute a single code snippet in the cloud
  2. Full development pipeline - Complete workflow from design to deployment and analysis
- **Key Components**:
  - `crew.py`: Main crew file where agents and tasks come together, and the main logic is executed.
  - `main.py`: Main script file with example usage.
  - `pipeline.py`: Pipeline orchestation utilities.
  - `config/agents.yaml`: Configuration file for defining agents.
  - `config/tasks.yaml`: Configuration file for defining tasks.
  - `tools/`: Contains tool classes used by the agents:
    - `agentbay_tools.py`: AgentBay SDK integration tools
    - `local_tools.py`: Local file system and HTTP verification tools
  - `api/agentbay_temporary_session.py`: Temporary session operations (each call creates/deletes session automatically)
  - `api/agentbay_persistent_session.py`: Persistent session operations (reusable sessions with manual lifecycle management)
  - `tests/`: Test cases for the integration

## Configuration

### Required Environment Variables

- `AGENTBAY_API_KEY`: Your AgentBay cloud execution API key
- `OPENAI_API_KEY`: Your LLM API key

### Optional Environment Variables

- `OPENAI_API_BASE`: Custom LLM API endpoint (e.g., for Alibaba Cloud Bailian: `https://dashscope.aliyuncs.com/compatible-mode/v1`)
- `OPENAI_MODEL_NAME`: LLM model name (default: `gpt-4o-mini`)
  - For Bailian: Use `openai/qwen-plus` (with `openai/` prefix for LiteLLM compatibility)

### Example Configuration

See `.env.example` for detailed configuration examples for different LLM providers:
- OpenAI (default)
- Alibaba Cloud Bailian
- Azure OpenAI
- Custom endpoints

## License

This project is released under the MIT License.

