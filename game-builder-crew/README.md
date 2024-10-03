# AI Crew for Game Building
## Introduction
This project demonstrates the use of the CrewAI framework to automate the creation of a game. CrewAI orchestrates autonomous AI agents, enabling them to collaborate and execute complex tasks efficiently.

By [@joaomdmoura](https://x.com/joaomdmoura)

- [CrewAI Framework](#crewai-framework)
- [Running the script](#running-the-script)
- [Details & Explanation](#details--explanation)
- [Contributing](#contributing)
- [Support and Contact](#support-and-contact)
- [License](#license)

## CrewAI Framework
CrewAI is designed to facilitate the collaboration of role-playing AI agents. In this example, The agents work together to build a Python-based game by simulating a collaborative software development process. Each agent has a distinct role, from writing the code to reviewing it for errors and ensuring it meets high-quality standards before final approval.


## Running the Script
It uses GPT-4o by default so you should have access to that to run it.

***Disclaimer:** This will use gpt-4o unless you change it to use a different model, and by doing so it may incur in different costs.*

- **Configure Environment**: Copy `.env.example` and set up the environment variables for [OpenAI](https://platform.openai.com/api-keys) and other tools as needed, like [Serper](serper.dev).
- **Install Dependencies**: Run `poetry lock && poetry install`.
- **Customize**: Modify `src/game_builder_crew/main.py` to add custom inputs for your agents and tasks.
- **Customize Further**: Check `src/game_builder_crew/config/agents.yaml` to update your agents and `src/game_builder_crew/config/tasks.yaml` to update your tasks.
- **Execute the Script**: Run `poetry run game_builder_crew` and input your project details.

## Details & Explanation
- **Running the Script**: Execute `poetry run game_builder_crew`. The script will leverage the CrewAI framework to generate a detailed job posting.
- **Key Components**:
  - `src/game_builder_crew/main.py`: Main script file.
  - `src/game_builder_crew/crew.py`: Main crew file where agents and tasks come together, and the main logic is executed.
  - `src/game_builder_crew/config/agents.yaml`: Configuration file for defining agents.
  - `src/game_builder_crew/config/tasks.yaml`: Configuration file for defining tasks.
  - `src/game_builder_crew/tools`: Contains tool classes used by the agents.

## License
This project is released under the MIT License.
