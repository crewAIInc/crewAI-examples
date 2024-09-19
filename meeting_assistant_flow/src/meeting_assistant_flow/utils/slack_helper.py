import os

from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Load environment variables from a .env file
load_dotenv()


def send_message_to_channel(text: str):
    # Get your Slack token and channel ID from the environment variables
    SLACK_TOKEN = os.getenv("SLACK_TOKEN")
    SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")
    client = WebClient(token=SLACK_TOKEN)

    try:
        # Send a message to the channel
        response = client.chat_postMessage(
            channel=SLACK_CHANNEL_ID,
            text=text,
        )
        return response
    except SlackApiError as e:
        print(f"Error sending message: {e.response['error']}")
