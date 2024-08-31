
# AI Crew for Surprise Travel Planning
## Introduction
This project demonstrates the use of the CrewAI framework to automate the creation of surprise travel plans. CrewAI orchestrates autonomous AI agents, enabling them to collaborate and execute complex tasks efficiently.

By [@joaomdmoura](https://x.com/joaomdmoura)

- [CrewAI Framework](#crewai-framework)
- [Running the script](#running-the-script)
- [Details & Explanation](#details--explanation)
- [Contributing](#contributing)
- [Support and Contact](#support-and-contact)
- [License](#license)

## CrewAI Framework
CrewAI is designed to facilitate the collaboration of role-playing AI agents. In this example, these agents work together to create a comprehensive surprise travel plan, ensuring a seamless and exciting travel experience.

## Running the Script
It uses GPT-4 by default so you should have access to that to run it.

***Disclaimer:** This will use gpt-4 unless you change it to use a different model, and by doing so it may incur different costs.*

- **Configure Environment**: Copy `.env.example` and set up the environment variables for [OpenAI](https://platform.openai.com/api-keys) and other tools as needed.
- **Install Dependencies**: Run `poetry lock && poetry install`.
- **Customize**: Modify `src/surprise_travel/main.py` to add custom inputs for your agents and tasks.
- **Customize Further**: Check `src/surprise_travel/config/agents.yaml` to update your agents and `src/surprise_travel/config/tasks.yaml` to update your tasks.
- **Execute the Script**: Run `poetry run surprise_travel` and input your project details.

## Details & Explanation
- **Running the Script**: Execute `poetry run surprise_travel`. The script will leverage the CrewAI framework to generate a detailed surprise travel plan.
- **Key Components**:
  - `src/surprise_travel/main.py`: Main script file.
  - `src/surprise_travel/crew.py`: Main crew file where agents and tasks come together, and the main logic is executed.
  - `src/surprise_travel/config/agents.yaml`: Configuration file for defining agents.
  - `src/surprise_travel/config/tasks.yaml`: Configuration file for defining tasks.
  - `src/surprise_travel/tools`: Contains tool classes used by the agents.

## License
This project is released under the MIT License.
