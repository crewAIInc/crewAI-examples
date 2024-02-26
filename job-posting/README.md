# AI Crew for Jobs postings
## Introduction
This project is an example using the CrewAI framework to automate the process of coming up with an Jobs postings. CrewAI orchestrates autonomous AI agents, enabling them to collaborate and execute complex tasks efficiently.

This example is also available online at [JobDescriptionCrew.com](https://jobdescriptioncrew.com/)

#### Jobs postings
[![Jobs postings](https://img.youtube.com/vi/u98wEMz-9to/0.jpg)](https://www.youtube.com/watch?v=u98wEMz-9to "Jobs postings")

By [@joaomdmoura](https://x.com/joaomdmoura)

- [CrewAI Framework](#crewai-framework)
- [Running the script](#running-the-script)
- [Details & Explanation](#details--explanation)
- [License](#license)

## CrewAI Framework
CrewAI is designed to facilitate the collaboration of role-playing AI agents. In this example, these agents work together to give a complete stock analysis and investment recommendation

## Running the Script
- **Configure Environment**: Copy ``.env.example` and set up the environment variables for OpenAI and [Serper](https://serper.dev/).
- **Install Dependencies**: Run `pip install -r requirements.txt`.
- **Execute the Script**: Run `python main.py` and input your idea.

## Details & Explanation
- **Running the Script**: Execute `python main.py`` and input the requested information when prompted. The script will leverage the CrewAI framework to create the job posting for you
- **Key Components**:
  - `./main.py`: Main script file.
  - `./tasks.py`: Main file with the tasks prompts.
  - `./agents.py`: Main file with the agents creation.
  - `./job_description_example.md`: Example of a job description the crew will use as inspiration.


## License
This project is released under the MIT License.
