import os

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Optional
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import base64

class GeminiImageGenerationInput(BaseModel):
    """Input schema for Gemini Image Generation Tool."""
    prompt: str = Field(..., description="Detailed text description of the image to generate")

class GeminiImageGenerator(BaseTool):
    name: str = "Gemini Image Generator"
    description: str = "A tool that generates images from text prompts using Google's Gemini AI models. The tool can create various types of images based on detailed text descriptions."

    args_schema: Type[BaseModel] = GeminiImageGenerationInput




    def _run(self, prompt: str, model: str = "gemini-2.0-flash-preview-image-generation",
             save_path: str = "image.png") -> str:
        """Execute the Gemini image generation tool."""
        try:
            client = genai.Client(
                api_key = os.getenv("GEMINI_API_KEY")
            )
            # Generate content using Gemini
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=['TEXT', 'IMAGE']
                )
            )

            results = []

            # Process the response
            for part in response.candidates[0].content.parts:
                if part.text is not None:
                    results.append(f"Generated text description: {part.text}")
                elif part.inline_data is not None:
                    # Save the generated image
                    image = Image.open(BytesIO(part.inline_data.data))
                    image.save(save_path)
                    results.append(f"Image successfully generated and saved to {save_path}")

            return "\n".join(results) if results else "No content generated"

        except Exception as e:
            return f"An error occurred during image generation: {str(e)}"
