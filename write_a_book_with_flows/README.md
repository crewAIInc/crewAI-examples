# Write a Book Flow

Welcome to the Book Writing Flow, powered by [crewAI](https://crewai.com). This template is designed to help you set up a multi-agent AI system with ease, leveraging the powerful and flexible framework provided by crewAI. Our goal is to enable your agents to collaborate effectively on complex tasks, maximizing their collective intelligence and capabilities.

## Overview

This flow will guide you through the process of writing a book by leveraging multiple AI agents, each with specific roles. Here's a brief overview of what will happen in this flow:

1. **Generate Book Outline**: The flow starts by using the `OutlineCrew` to create a comprehensive outline for your book. This crew will search the internet, define the structure, and main topics of the book based on the provided goal and topic.

2. **Write Book Chapters**: Once the outline is ready, the flow will kick off a new crew, `WriteBookChapterCrew`, for each chapter outlined in the previous step. Each crew will be responsible for writing a specific chapter, ensuring that the content is detailed and coherent.

3. **Join and Save Chapters**: In the final step, the flow will combine all the chapters into a single markdown file, creating a complete book. This file will be saved in the root folder of your project.

By following this flow, you can efficiently produce a well-structured and comprehensive book, leveraging the power of multiple AI agents to handle different aspects of the writing process.

## Installation

Ensure you have Python >=3.10 <=3.13 installed on your system. This project uses [Poetry](https://python-poetry.org/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install Poetry:

```bash
pip install poetry
```

Next, navigate to your project directory and install the dependencies:

1. First lock the dependencies and then install them:

```bash
crewai install
```

### Customizing

**Add your `OPENAI_API_KEY` into the `.env` file**
**Add your `SERPER_API_KEY` into the `.env` file**

- Modify `src/write_a_book_with_flows/config/agents.yaml` to define your agents
- Modify `src/write_a_book_with_flows/config/tasks.yaml` to define your tasks
- Modify `src/write_a_book_with_flows/crew.py` to add your own logic, tools and specific args
- Modify `src/write_a_book_with_flows/main.py` to add custom inputs for your agents and tasks

## Running the Project

To kickstart your crew of AI agents and begin task execution, run this from the root folder of your project:

```bash
crewai run
```

This command initializes the write_a_book_with_flows Crew, assembling the agents and assigning them tasks as defined in your configuration.

When you kickstart the flow, it will orchestrate multiple crews to perform the tasks. The flow will first generate a book outline, then create and run a crew for each chapter, and finally join all the chapters into a single markdown file.

## Understanding Your Crew

The write_a_book_with_flows Flow is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your flow.

### Flow Structure

1. **OutlineCrew**: This crew is responsible for generating the book outline. It defines the structure and main topics of the book based on the provided goal and topic.

2. **WriteBookChapterCrew**: For each chapter outlined by the `OutlineCrew`, a new `WriteBookChapterCrew` is created. Each of these crews is responsible for writing a specific chapter, ensuring detailed and coherent content.

3. **Join and Save**: After all chapters are written, the flow combines them into a single markdown file, creating a complete book.

By understanding the flow structure, you can see how multiple crews are orchestrated to work together, each handling a specific part of the book writing process. This modular approach allows for efficient and scalable book production.

## Support

For support, questions, or feedback regarding the {{crew_name}} Crew or crewAI.

- Visit our [documentation](https://docs.crewai.com)
- Reach out to us through our [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join our Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with our docs](https://chatg.pt/DWjSBZn)

Let's create wonders together with the power and simplicity of crewAI.
