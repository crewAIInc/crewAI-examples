import os
from typing import List

import requests
from dotenv import load_dotenv

from meeting_assistant_flow.types import MeetingTask

# Load environment variables from .env file
load_dotenv()

# Your Trello API credentials loaded from environment variables
API_KEY = os.getenv("TRELLO_API_KEY")
TOKEN = os.getenv("TRELLO_TOKEN")

# The ID of the Trello board and list where you want to add the cards
BOARD_ID = os.getenv("TRELLO_BOARD_ID")
LIST_ID = os.getenv("TRELLO_LIST_ID")


def create_trello_card(task_title, task_description):
    """
    Create a new card in Trello for the given task.

    :param task_title: Title of the task (will be the title of the Trello card)
    :param task_description: Detailed description of the task (will be the body of the Trello card)
    :return: Response object from Trello API call
    """
    url = "https://api.trello.com/1/cards"

    query = {
        "key": API_KEY,
        "token": TOKEN,
        "idList": LIST_ID,
        "name": task_title,
        "desc": task_description,
    }

    response = requests.post(url, params=query)

    if response.status_code == 200:
        print(f"Task '{task_title}' successfully created in Trello.")
    else:
        print(f"Failed to create task '{task_title}' in Trello.")
        print(response.text)

    return response


def save_tasks_to_trello(tasks: List[MeetingTask]):
    """
    Save a list of tasks to Trello. Each task is a dictionary with 'title' and 'body'.

    :param tasks: List of tasks, where each task is a dict with 'title' and 'body'
    """
    for task in tasks:
        if task.name and task.description:
            create_trello_card(task.name, task.description)
        else:
            print("Task is missing a title or description. Skipping...")


# Example usage
if __name__ == "__main__":
    tasks = [
        {
            "title": "Add Token Count Progress Indicator to Website",
            "body": "I received a suggestion from a colleague to enhance the token count exceeded feature on our website...",
        },
        {
            "title": "Improve Mobile Responsiveness for Dashboard",
            "body": "We need to improve the mobile layout of the dashboard for better usability. The sidebar should collapse automatically...",
        },
    ]

    save_tasks_to_trello(tasks)
