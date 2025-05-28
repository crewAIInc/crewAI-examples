from typing import List, Dict
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
from dotenv import load_dotenv
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

load_dotenv()

class YouTubeTool(BaseTool):
    name: str = "YouTube Search Tool"
    description: str = "A tool to search for educational YouTube videos on specific topics"
    api_key: str = Field(default_factory=lambda: os.getenv('YOUTUBE_API_KEY'))
    youtube: any = None

    def __init__(self):
        super().__init__()
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)

    def _run(self, topic: str) -> str:
        """
        Search for educational videos on a specific topic.
        
        Args:
            topic (str): The topic to search for
            
        Returns:
            str: Formatted string containing video information
        """
        try:
            # Search for videos
            search_response = self.youtube.search().list(
                q=f"{topic} tutorial education",
                part="snippet",
                maxResults=3,
                type="video",
                relevanceLanguage="en",
                videoDuration="medium",  # Filter for medium length videos (4-20 minutes)
                videoEmbeddable="true",
                videoSyndicated="true",
                order="relevance"  # Sort by relevance
            ).execute()

            videos = []
            for item in search_response.get("items", []):
                video_info = {
                    "title": item["snippet"]["title"],
                    "channel": item["snippet"]["channelTitle"],
                    "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                    "description": item["snippet"]["description"]
                }
                videos.append(video_info)

            # Format the output as a markdown string
            output = f"## Videos for {topic}\n\n"
            for video in videos:
                output += f"### {video['title']}\n"
                output += f"- **Channel**: {video['channel']}\n"
                output += f"- **URL**: {video['url']}\n"
                output += f"- **Description**: {video['description'][:200]}...\n\n"

            return output

        except HttpError as e:
            return f"An HTTP error occurred: {str(e)}"
        except Exception as e:
            return f"An error occurred: {str(e)}" 