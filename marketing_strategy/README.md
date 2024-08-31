
# AI Crew for Marketing Strategy
## Introduction
This project demonstrates the use of the CrewAI framework to automate the creation of a marketing strategy. CrewAI orchestrates autonomous AI agents, enabling them to collaborate and execute complex tasks efficiently.

By [@joaomdmoura](https://x.com/joaomdmoura)

- [CrewAI Framework](#crewai-framework)
- [Running the script](#running-the-script)
- [Details & Explanation](#details--explanation)
- [Contributing](#contributing)
- [Support and Contact](#support-and-contact)
- [License](#license)

## CrewAI Framework
CrewAI is designed to facilitate the collaboration of role-playing AI agents. In this example, these agents work together to create a comprehensive marketing strategy and develop compelling marketing content.

## Running the Script
It uses GPT-4o by default so you should have access to that to run it.

***Disclaimer:** This will use gpt-4o unless you change it to use a different model, and by doing so it may incur in different costs.*

- **Configure Environment**: Copy `.env.example` and set up the environment variables for [OpenAI](https://platform.openai.com/api-keys) and other tools as needed, like [Serper](serper.dev).
- **Install Dependencies**: Run `poetry lock && poetry install`.
- **Customize**: Modify `src/marketing_posts/main.py` to add custom inputs for your agents and tasks.
- **Customize Further**: Check `src/marketing_posts/config/agents.yaml` to update your agents and `src/marketing_posts/config/tasks.yaml` to update your tasks.
- **Execute the Script**: Run `poetry run marketing_posts` and input your project details.

## Details & Explanation
- **Running the Script**: Execute `poetry run marketing_posts`. The script will leverage the CrewAI framework to generate a detailed marketing strategy.
- **Key Components**:
  - `src/marketing_posts/main.py`: Main script file.
  - `src/marketing_posts/crew.py`: Main crew file where agents and tasks come together, and the main logic is executed.
  - `src/marketing_posts/config/agents.yaml`: Configuration file for defining agents.
  - `src/marketing_posts/config/tasks.yaml`: Configuration file for defining tasks.
  - `src/marketing_posts/tools`: Contains tool classes used by the agents.

## License
This project is released under the MIT License.
