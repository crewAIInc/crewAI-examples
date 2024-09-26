# Lead Score Flow

Welcome to the Lead Score Flow project, powered by [crewAI](https://crewai.com). This example demonstrates how you can leverage Flows from crewAI to automate the process of scoring leads, including data collection, analysis, and scoring. By utilizing Flows, the process becomes much simpler and more efficient.

## Overview

This flow will guide you through the process of setting up an automated lead scoring system. Here's a brief overview of what will happen in this flow:

1. **Load Leads**: The flow starts by loading lead data from a CSV file named `leads.csv`.

2. **Score Leads**: The `LeadScoreCrew` is kicked off to score the loaded leads based on predefined criteria.

3. **Human in the Loop**: The top 3 candidates are presented for human review, allowing for additional feedback or proceeding with writing emails.

4. **Write and Save Emails**: Emails are generated and saved for all leads, with special attention to the top 3 candidates.

By following this flow, you can efficiently automate the process of scoring leads, leveraging the power of multiple AI agents to handle different aspects of the lead scoring workflow.

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

### Customizing & Dependencies

**Add your `OPENAI_API_KEY` into the `.env` file**  
**Add your `SERPER_API_KEY` into the `.env` file**

To customize the behavior of the lead score flow, you can update the agents and tasks defined in the `LeadDataCollectionCrew`, `LeadAnalysisCrew`, and `LeadScoringCrew`. If you want to adjust the flow itself, you will need to modify the flow in `main.py`.

- **Agents and Tasks**: Modify `src/lead_score_flow/config/agents.yaml` to define your agents and `src/lead_score_flow/config/tasks.yaml` to define your tasks. This is where you can customize how lead data is collected, analyzed, and scored.

- **Flow Adjustments**: Modify `src/lead_score_flow/main.py` to adjust the flow. This is where you can change how the flow orchestrates the different crews and tasks.

## Running the Project

To kickstart your crew of AI agents and begin task execution, run this from the root folder of your project:

```bash
crewai run
```

This command initializes the lead_score_flow, assembling the agents and assigning them tasks as defined in your configuration.

When you kickstart the flow, it will orchestrate multiple crews to perform the tasks. The flow will first collect lead data, then analyze the data, score the leads, save the scores to a CSV file, and generate email drafts.

## Understanding Your Flow

The lead_score_flow is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your flow.

### Flow Structure

1. **Collect Lead Data**: This step collects lead data from various sources.

2. **Analyze Lead Data**: The `LeadAnalysisCrew` is kicked off to analyze the collected lead data.

3. **Score Leads**: The analyzed data is then used to score the leads based on predefined criteria.

4. **Save Lead Scores**: The lead scores are saved to a CSV file named `lead_scores.csv`.

5. **Write and Save Emails**: Emails are generated and saved for all leads, with special attention to the top 3 candidates.

By understanding the flow structure, you can see how multiple crews are orchestrated to work together, each handling a specific part of the lead scoring process. This modular approach allows for efficient and scalable lead scoring automation.

## Support

For support, questions, or feedback regarding the Lead Score Flow or crewAI:

- Visit our [documentation](https://docs.crewai.com)
- Reach out to us through our [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join our Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with our docs](https://chatg.pt/DWjSBZn)

Let's create wonders together with the power and simplicity of crewAI.
