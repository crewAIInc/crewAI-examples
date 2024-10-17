# WordpressPublisher Crew

Welcome to the WordpressPublisher Crew project, powered by [crewAI](https://crewai.com). This template is designed to help you set up a multi-agent AI system with ease, leveraging the powerful and flexible framework provided by crewAI. Our goal is to enable your agents to collaborate effectively on complex tasks, maximizing their collective intelligence and capabilities.

## Installation

Ensure you have Python >=3.10 <=3.13 installed on your system. This project uses [Poetry](https://python-poetry.org/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install Poetry:

```bash
pip install poetry
```

Next, navigate to your project directory and install the dependencies:

1. First lock the dependencies and install them by using the CLI command:
```bash
crewai install
```
### Customizing

- Modify `src/agencia_noticias/config/agents.yaml` to define your agents
- Modify `src/agencia_noticias/config/tasks.yaml` to define your tasks
- Modify `src/agencia_noticias/crew.py` to add your own logic, tools and specific args
- Modify `src/agencia_noticias/main.py` to add custom inputs for your agents and tasks

## Running the Project

To kickstart your crew of AI agents and begin task execution, run this from the root folder of your project:

```bash
$ crewai run
```

This command initializes the agencia_noticias Crew, assembling the agents and assigning them tasks as defined in your configuration.

This example, unmodified, will run the create a `report_ptbr.md` file with the output of a research on LLMs in the root folder.

## Understanding Your Crew

The agencia_noticias Crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your crew.

## About this Crew
This crew simulates a Content News Agency, with content research, report, translating and publishing news from any subject.

Agents:
- researcher
- reporting_analyst
- translator (in this case, translating for Brazilian pt-br)
- blog_publisher (in this case, specific for WP)

Tasks:
- research_task
- reporting_task
- translate_task
- publish_task

Tools:
- wp_publisher: for the task that will be executed by the publisher agent.

## You will need
- Openai Api Key [OpenAIDocs](https://platform.openai.com/api-keys)
- Serper API Key [Serper](https://serper.dev/)
- Wordpress Rest API Token -- Follow steps in the Plugin link [WPToken](https://br.wordpress.org/plugins/jwt-authentication-for-wp-rest-api/)

**Add your `KEYS` into the `.env` file**

## Support

For support, questions, or feedback regarding the AgenciaNoticias Crew or crewAI.
- Visit our [documentation](https://docs.crewai.com)

Let's create wonders together with the power and simplicity of crewAI.