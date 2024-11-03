# Self Evaluation Loop Flow

Welcome to the Self Evaluation Loop Flow project, powered by [crewAI](https://crewai.com). This project showcases a powerful pattern in AI workflows: automatic self-evaluation. By leveraging crewAI's multi-agent system, this flow demonstrates how to set up a Crew that evaluates the responses of other Crews, iterating with feedback to improve results.

## Overview

This flow guides you through setting up an automated self-evaluation system using two main Crews: the `ShakespeareanXPostCrew` and the `XPostReviewCrew`. The process involves the following steps:

1. **Generate Initial Output**: The `ShakespeareanXPostCrew` generates an initial Shakespearean-style post (X post) on a given topic, such as "Flying cars". This post is crafted to be humorous and playful, adhering to specific character limits and style guidelines.

2. **Evaluate Output**: The `XPostReviewCrew` evaluates the generated post to ensure it meets the required criteria, such as character count and absence of emojis. The crew provides feedback on the post's validity and quality.

3. **Iterate with Feedback**: If the post does not meet the criteria, the flow iterates by regenerating the post with the feedback provided. This iterative process continues until the post is valid or a maximum retry limit is reached.

4. **Finalize and Save**: Once the post is validated, it is finalized and saved for further use. If the maximum retry count is exceeded without achieving a valid post, the flow exits with the last generated post and feedback.

This pattern of automatic self-evaluation is crucial for developing robust AI systems that can adapt and improve over time, ensuring high-quality outputs through iterative refinement.

## Installation

Ensure you have Python >=3.10 <=3.13 installed on your system.

To install CrewAI, run the following command:

```bash
pip install crewai
```

This command will install CrewAI and its necessary dependencies, allowing you to start building and managing AI agents efficiently.

### Customizing

**Add your `OPENAI_API_KEY` into the `.env` file**

- Modify `src/flow_self_evalulation_loop/config/agents.yaml` to define your agents.
- Modify `src/flow_self_evalulation_loop/config/tasks.yaml` to define your tasks.
- Modify `src/flow_self_evalulation_loop/crew.py` to add your own logic, tools, and specific arguments.
- Modify `src/flow_self_evalulation_loop/main.py` to add custom inputs for your agents and tasks.

## Running the Project

To kickstart your crew of AI agents and begin task execution, run this from the root folder of your project:
    
```bash
crewai flow kickoff 
```


This command initializes the self-evaluation loop flow, assembling the agents and assigning them tasks as defined in your configuration.

The unmodified example will generate a `report.md` file with the output of a research on LLMs in the root folder.

## Understanding Your Flow

The self-evaluation loop flow is composed of 2 Crews. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your flow.

This flow is centered around two major Crews: the `ShakespeareanXPostCrew` and the `XPostReviewCrew`. The `ShakespeareanXPostCrew` is responsible for generating a Shakespearean-style post (X post) on a given topic, while the `XPostReviewCrew` evaluates the generated post to ensure it meets specific criteria. The process is iterative, using feedback from the review to refine the post until it is valid or a maximum retry limit is reached.

### Flow Structure

1. **Generate Initial Output**: A Crew generates the initial output based on predefined criteria.

2. **Evaluate Output**: Another Crew evaluates the output, providing feedback on its validity and quality.

3. **Iterate with Feedback**: If necessary, the initial Crew is re-run with feedback to improve the output.

4. **Finalize and Save**: Once validated, the output is saved for further use.

By understanding the flow structure, you can see how multiple Crews are orchestrated to work together, each handling a specific part of the self-evaluation process. This modular approach allows for efficient and scalable automation.

## Support

For support, questions, or feedback regarding the Self Evaluation Loop Flow or crewAI:

- Visit our [documentation](https://docs.crewai.com)
- Reach out to us through our [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join our Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with our docs](https://chatg.pt/DWjSBZn)

Let's create wonders together with the power and simplicity of crewAI.
