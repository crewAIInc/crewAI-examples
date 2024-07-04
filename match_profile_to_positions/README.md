
# AI Crew for Matching CVs to Job Proposals
## Introduction
This project demonstrates the use of the CrewAI framework to automate the process of matching CVs to job proposals. CrewAI orchestrates autonomous AI agents, enabling them to collaborate and execute complex tasks efficiently.

By [@joaomdmoura](https://x.com/joaomdmoura)

- [CrewAI Framework](#crewai-framework)
- [Running the script](#running-the-script)
- [Details & Explanation](#details--explanation)
- [Contributing](#contributing)
- [Support and Contact](#support-and-contact)
- [License](#license)

## CrewAI Framework
CrewAI is designed to facilitate the collaboration of role-playing AI agents. In this example, these agents work together to extract relevant information from CVs and match them to job opportunities, ensuring the best fit between candidates and job roles.

## Running the Script
It uses GPT-4o by default so you should have access to that to run it.

***Disclaimer:** This will use gpt-4o unless you change it to use a different model, and by doing so it may incur different costs.*

- **Configure Environment**: Copy `.env.example` and set up the environment variables for [OpenAI](https://platform.openai.com/api-keys) and other tools as needed.
- **Install Dependencies**: Run `poetry lock && poetry install`.
- **Customize**: Modify `src/match_to_proposal/main.py` to add custom inputs for your agents and tasks.
- **Customize Further**: Check `src/match_to_proposal/config/agents.yaml` to update your agents and `src/match_to_proposal/config/tasks.yaml` to update your tasks.
- **Execute the Script**: Run `poetry run match_to_proposal` and input your project details.

## Details & Explanation
- **Running the Script**: Execute `poetry run match_to_proposal`. The script will leverage the CrewAI framework to match CVs to job proposals and generate a detailed report.
- **Key Components**:
  - `src/match_to_proposal/main.py`: Main script file.
  - `src/match_to_proposal/crew.py`: Main crew file where agents and tasks come together, and the main logic is executed.
  - `src/match_to_proposal/config/agents.yaml`: Configuration file for defining agents.
  - `src/match_to_proposal/config/tasks.yaml`: Configuration file for defining tasks.
  - `src/match_to_proposal/tools`: Contains tool classes used by the agents.

## License
This project is released under the MIT License.
