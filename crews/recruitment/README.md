# AI Crew for Recruitment

**DISCALIMER** This example uses cookies to authenticate to LinkedIn, and it's meant only as an example or the selenium tool, using this for real-world applications may violate LinkedIn's terms of service and could lead to your account being banned. We do not endorse or encourage the use of this tool for any real-world applications.

## Introduction
This project demonstrates the use of the CrewAI framework to automate the recruitment process. CrewAI orchestrates autonomous AI agents, enabling them to collaborate and execute complex tasks efficiently.

By [@joaomdmoura](https://x.com/joaomdmoura)

- [CrewAI Framework](#crewai-framework)
- [Running the script](#running-the-script)
- [Details & Explanation](#details--explanation)
- [Contributing](#contributing)
- [Support and Contact](#support-and-contact)
- [License](#license)

## CrewAI Framework
CrewAI is designed to facilitate the collaboration of role-playing AI agents. In this example, these agents work together to streamline the recruitment process, ensuring the best fit between candidates and job roles.

## Running the Script
It uses GPT-4o by default so you should have access to that to run it.

***DISCALIMER:** This example uses cookies to authenticate to LinkedIn, and it's meant only as an example or the selenium tool, using this for real-world applications may violate LinkedIn's terms of service and could lead to your account being banned. We do not endorse or encourage the use of this tool for any real-world applications.*

***Disclaimer:** This will use gpt-4o unless you change it to use a different model, and by doing so it may incur different costs.*

- **Configure Environment**: Copy `.env.example` and set up the environment variables for [OpenAI](https://platform.openai.com/api-keys) and other tools as needed.
- **Install Dependencies**: Run `poetry lock && poetry install`.
- **Customize**: Modify `src/recruitment/main.py` to add custom inputs for your agents and tasks.
- **Customize Further**: Check `src/recruitment/config/agents.yaml` to update your agents and `src/recruitment/config/tasks.yaml` to update your tasks.
- **Custom Tools**: You can find custom tools at `recruitment/src/recruitment/tools/`.
- **Execute the Script**: Run `poetry run recruitment` and input your project details.

### Steps to get Linkedin Cookie (LI_AT)
- Navigate to www.linkedin.com and log in
- Open browser developer tools (Ctrl-Shift-I or right click -> inspect element)
- Select the appropriate tab for your browser (Application on Chrome, Storage on Firefox)
- Click the Cookies dropdown on the left-hand menu, and select the www.linkedin.com option
- Find and copy the li_at value and add it to your .env file
- Be sure to fetch the cookies again if selenium doesnt login to linkedin after a while

## Details & Explanation
- **Running the Script**: Execute `poetry run recruitment`. The script will leverage the CrewAI framework to automate recruitment tasks and generate a detailed report.
- **Running Training**: Execute `poetry run train n` where n is the number of training iterations.
- **Key Components**:
  - `src/recruitment/main.py`: Main script file.
  - `src/recruitment/crew.py`: Main crew file where agents and tasks come together, and the main logic is executed.
  - `src/recruitment/config/agents.yaml`: Configuration file for defining agents.
  - `src/recruitment/config/tasks.yaml`: Configuration file for defining tasks.
  - `src/recruitment/tools`: Contains tool classes used by the agents.

## License
This project is released under the MIT License.
