from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
import requests
import os

class LinkedInImagePostInput(BaseModel):
    """Input schema for LinkedIn Image Posting Tool."""
    message: str = Field(..., description="Text message to post with the image")

class LinkedInImagePostTool(BaseTool):
    name: str = "LinkedIn Image Poster"
    description: str = "A tool that posts images with text to LinkedIn. It handles the entire process including image upload and post creation."

    args_schema: Type[BaseModel] = LinkedInImagePostInput

    def _run(self,message: str, visibility: str = "PUBLIC") -> str:
        """Execute the LinkedIn image posting tool."""
        try:
            access_token = os.getenv("Linkedin_access_token")
            image_path = "./image.png"
            # Check if image file exists
            if not os.path.exists(image_path):
                return f"Error: Image file not found at path: {image_path}"

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0"
            }

            # Step 1: Get user info
            userinfo_url = "https://api.linkedin.com/v2/userinfo"
            user_response = requests.get(userinfo_url, headers={"Authorization": f"Bearer {access_token}"})

            if user_response.status_code != 200:
                return f"Failed to get user info: HTTP {user_response.status_code}"

            user_info = user_response.json()
            person_urn = f"urn:li:person:{user_info['sub']}"

            # Step 2: Register image upload
            register_upload_data = {
                "registerUploadRequest": {
                    "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                    "owner": person_urn,
                    "serviceRelationships": [{
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent"
                    }]
                }
            }

            register_url = "https://api.linkedin.com/v2/assets?action=registerUpload"
            register_response = requests.post(register_url, headers=headers, json=register_upload_data)

            if register_response.status_code != 200:
                return f"Failed to register upload: HTTP {register_response.status_code} - {register_response.text}"

            register_result = register_response.json()
            upload_url = register_result['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
            asset_id = register_result['value']['asset']

            # Step 3: Upload the image
            with open(image_path, 'rb') as image_file:
                files = {'file': image_file}
                upload_response = requests.post(upload_url, files=files)

            if upload_response.status_code not in [200, 201]:
                return f"Failed to upload image: HTTP {upload_response.status_code} - {upload_response.text}"

            # Step 4: Create the post
            post_data = {
                "author": person_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {"text": message},
                        "shareMediaCategory": "IMAGE",
                        "media": [{
                            "status": "READY",
                            "description": {"text": "Shared image"},
                            "media": asset_id,
                            "title": {"text": "Image"}
                        }]
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": visibility
                }
            }

            post_url = "https://api.linkedin.com/v2/ugcPosts"
            post_response = requests.post(post_url, headers=headers, json=post_data)

            if post_response.status_code == 201:
                return f"Success! Image posted to LinkedIn. Post ID: {post_response.json().get('id')}"
            else:
                return f"Failed to create post: HTTP {post_response.status_code} - {post_response.text}"

        except Exception as e:
            return f"An error occurred while posting to LinkedIn: {str(e)}"
