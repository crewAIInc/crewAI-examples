# PDF Knowledge Example

This project demonstrates how to create a Crew of AI agents and tasks using crewAI. It uses a PDF knowledge source to answer user questions based on the content of the PDF. The PDF is loaded from a file and the knowledge source is initialized with it. The project also includes a custom task that uses the knowledge source to answer user questions. You can modify the question in the `main.py` file.

## Installation

Ensure you have Python >=3.10 <=3.13 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install uv:

```bash
pip install uv
```

Next, navigate to your project directory and install the dependencies:

(Optional) Lock the dependencies and install them by using the CLI command:
```bash
crewai install
```
### Customizing

**Add your `OPENAI_API_KEY` into the `.env` file**

- Modify `src/meta_quest_knowledge/config/agents.yaml` to define your agents
- Modify `src/meta_quest_knowledge/config/tasks.yaml` to define your tasks
- Modify `src/meta_quest_knowledge/crew.py` to add your own logic, tools and specific args
- Modify `src/meta_quest_knowledge/main.py` to add custom inputs for your agents and tasks

## Running the Project

To kickstart your crew of AI agents and begin task execution, run this from the root folder of your project:

```bash
$ crewai run
```

This command initializes the Crew, assembling the agents and assigning them tasks as defined in your configuration.

## Additional Knowledge Sources

Explore [Knowledge](https://docs.crewai.com/concepts/knowledge) documentation for more information on how to use different knowledge sources.
You can select from multiple different knowledge sources such as:
* Text files
* PDFs
* CSV & Excel files
* JSON files
* Sources supported by [docling](https://github.com/DS4SD/docling)
