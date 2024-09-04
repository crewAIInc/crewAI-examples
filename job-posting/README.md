# AI Crew for Job Posting
## Introduction
This project demonstrates the use of the CrewAI framework to automate the creation of job posting. CrewAI orchestrates autonomous AI agents, enabling them to collaborate and execute complex tasks efficiently.

By [@joaomdmoura](https://x.com/joaomdmoura)

- [CrewAI Framework](#crewai-framework)
- [Running the script](#running-the-script)
- [Details & Explanation](#details--explanation)
- [Contributing](#contributing)
- [Support and Contact](#support-and-contact)
- [License](#license)

## CrewAI Framework
CrewAI is designed to facilitate the collaboration of role-playing AI agents. In this example, these agents work together to analyze company culture and identify role requirements to create comprehensive job postings and industry analysis.

## Running the Script
It uses GPT-4o by default so you should have access to that to run it.

***Disclaimer:** This will use gpt-4o unless you change it to use a different model, and by doing so it may incur in different costs.*

- **Configure Environment**: Copy `.env.example` and set up the environment variables for [OpenAI](https://platform.openai.com/api-keys) and other tools as needed, like [Serper](serper.dev).
- **Install Dependencies**: Run `poetry lock && poetry install`.
- **Customize**: Modify `src/job_posting/main.py` to add custom inputs for your agents and tasks.
- **Customize Further**: Check `src/job_posting/config/agents.yaml` to update your agents and `src/job_posting/config/tasks.yaml` to update your tasks.
- **Execute the Script**: Run `poetry run job_posting` and input your project details.

## Details & Explanation
- **Running the Script**: Execute `poetry run job_posting`. The script will leverage the CrewAI framework to generate a detailed job posting.
- **Key Components**:
  - `src/job_posting/main.py`: Main script file.
  - `src/job_posting/crew.py`: Main crew file where agents and tasks come together, and the main logic is executed.
  - `src/job_posting/config/agents.yaml`: Configuration file for defining agents.
  - `src/job_posting/config/tasks.yaml`: Configuration file for defining tasks.
  - `src/job_posting/tools`: Contains tool classes used by the agents.

## License
This project is released under the MIT License.
