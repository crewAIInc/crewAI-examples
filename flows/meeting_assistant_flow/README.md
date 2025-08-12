# Meeting Assistant Flow

Welcome to the Meeting Assistant Flow project, powered by [crewAI](https://crewai.com). This example demonstrates how you can leverage Flows from crewAI to automate the process of managing meetings, including scheduling, note-taking, and follow-up actions. By utilizing Flows, the process becomes much simpler and more efficient.

## Overview

This flow will guide you through the process of setting up an automated meeting assistant. Here's a brief overview of what will happen in this flow:

1. **Load Meeting Notes**: The flow starts by loading the meeting notes from a file named `meeting_notes.txt`.

2. **Generate Tasks from Meeting Transcript**: The `MeetingAssistantCrew` is kicked off to generate tasks from the meeting transcript.

3. **Add Tasks to Trello**: The generated tasks are added to a Trello board.

4. **Save New Tasks to CSV**: The new tasks are saved to a CSV file named `new_tasks.csv`.

5. **Send Slack Notification**: A Slack notification is sent to a specified channel, informing about the new tasks added to Trello.

By following this flow, you can efficiently automate the process of managing meetings, leveraging the power of multiple AI agents to handle different aspects of the meeting workflow.


## Installation

Ensure you have Python >=3.10 <=3.13 installed on your system. First, if you haven't already, install CrewAI:

```bash
pip install crewai==0.130.0
```

Next, navigate to your project directory and install the dependencies:

1. First lock the dependencies and then install them:

```bash
crewai install
```

### Customizing & Dependencies

**Add your `OPENAI_API_KEY` into the `.env` file**  
**Add your `SERPER_API_KEY` into the `.env` file**  
**Add your `TRELLO_API_KEY`, `TRELLO_TOKEN`, `TRELLO_BOARD_ID`, and `TRELLO_LIST_ID` into the `.env` file**  
**Add your `SLACK_TOKEN` and `SLACK_CHANNEL_ID` into the `.env` file**

To customize the behavior of the meeting assistant flow, you can update the agents and tasks defined in the `MeetingSchedulerCrew`, `NoteTakingCrew`, and `FollowUpCrew`. If you want to adjust the flow itself, you will need to modify the flow in `main.py`.

- **Agents and Tasks**: Modify `src/meeting_assistant_flow/config/agents.yaml` to define your agents and `src/meeting_assistant_flow/config/tasks.yaml` to define your tasks. This is where you can customize how meetings are scheduled, notes are taken, and follow-up actions are managed.

- **Flow Adjustments**: Modify `src/meeting_assistant_flow/main.py` to adjust the flow. This is where you can change how the flow orchestrates the different crews and tasks.

### Setting Up Trello

To enable the meeting assistant flow to interact with Trello, follow these steps to set up your Trello API credentials:

1. **Generate Trello API Key**:

   - Visit the [Trello API Key page](https://trello.com/power-ups/admin/new) and log in with your Trello account.
   - Click on the "Create a Power-Up" button.
   - Fill in the required details for your Power-Up and click "Create".
   - Once created, you will see your API key. Copy this key and add it to your `.env` file as `TRELLO_API_KEY`.

2. **Generate Trello Token**:

   - Visit the [Trello Power Up page](https://developer.atlassian.com/cloud/trello/) to learn how to create a Power-Up and generate your token.
   - Scroll down to the "OAuth" section and click on the "Token" link.
   - Authorize the application to access your Trello account.
   - You will be provided with a token. Copy this token and add it to your `.env` file as `TRELLO_TOKEN`.

3. **Find Trello Board ID**:

   - Open Trello and navigate to the board you want to use.
   - The board ID is part of the URL. For example, in `https://trello.com/b/BOARD_ID/board-name`, `BOARD_ID` is your board ID.
   - Copy this ID and add it to your `.env` file as `TRELLO_BOARD_ID`.

4. **Find Trello List ID**:

   - On your Trello board, click on the list where you want to add tasks.
   - Click on the three dots (menu) on the top right of the list and select "Copy Link".
   - The list ID is part of the URL. For example, in `https://trello.com/c/BOARD_ID/LIST_ID/card-name`, `LIST_ID` is your list ID.
   - Copy this ID and add it to your `.env` file as `TRELLO_LIST_ID`.

5. **Set Up Environment Variables**:
   - Add the following variables to your `.env` file:
     ```plaintext
     TRELLO_API_KEY=your_trello_api_key
     TRELLO_TOKEN=your_trello_token
     TRELLO_BOARD_ID=your_trello_board_id
     TRELLO_LIST_ID=your_trello_list_id
     ```

By following these steps, you will have set up your Trello API credentials correctly, allowing the meeting assistant flow to interact with your Trello board and lists.

### Setting Up Slack

To enable the meeting assistant flow to send notifications to Slack, follow these steps to set up your Slack API credentials:

1. **Create a Slack App**: Visit the [Slack API page](https://api.slack.com/apps) and create a new app.

2. **Generate Slack Token**: Under the "OAuth & Permissions" section, generate a token with the necessary permissions.

3. **Find Slack Channel ID**: To find your Slack channel ID, open Slack, go to the channel, and click on the channel name. The channel ID will be in the URL.

4. **Invite Slack Bot to Channel**: Invite the Slack bot to the channel by typing `/invite @your-bot-name` in the channel.

5. **Set Up Environment Variables**: Add the following variables to your `.env` file:
   - `SLACK_TOKEN`
   - `SLACK_CHANNEL_ID`

## Running the Project

To kickstart your crew of AI agents and begin task execution, run this from the root folder of your project:

```bash
crewai run
```

This command initializes the meeting_assistant_flow, assembling the agents and assigning them tasks as defined in your configuration.

When you kickstart the flow, it will orchestrate multiple crews to perform the tasks. The flow will first load meeting notes, then generate tasks from the transcript, add tasks to Trello, save tasks to a CSV file, and send a Slack notification.

## Understanding Your Flow

The meeting_assistant_flow is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your flow.

### Flow Structure

1. **Load Meeting Notes**: This step loads the meeting notes from a file named `meeting_notes.txt`.

2. **Generate Tasks from Meeting Transcript**: The `MeetingAssistantCrew` is kicked off to generate tasks from the meeting transcript.

3. **Add Tasks to Trello**: The generated tasks are added to a Trello board.

4. **Save New Tasks to CSV**: The new tasks are saved to a CSV file named `new_tasks.csv`.

5. **Send Slack Notification**: A Slack notification is sent to a specified channel, informing about the new tasks added to Trello.

By understanding the flow structure, you can see how multiple crews are orchestrated to work together, each handling a specific part of the meeting management process. This modular approach allows for efficient and scalable meeting automation.

## Support

For support, questions, or feedback regarding the Meeting Assistant Flow or crewAI:

- Visit our [documentation](https://docs.crewai.com)
- Reach out to us through our [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join our Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with our docs](https://chatg.pt/DWjSBZn)

Let's create wonders together with the power and simplicity of crewAI.
