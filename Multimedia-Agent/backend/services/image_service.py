"""
Image Generation Service

Generates educational images using Pollinations AI.
"""

import os
import uuid
import requests
from pathlib import Path


class ImageService:
    """
    Service responsible for generating images.
    """

    def __init__(self):

        self.output_dir = Path("backend/outputs/images")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_image(self, prompt: str) -> dict:
        """
        Generate an image from a text prompt.

        Args:
            prompt (str): Image generation prompt.

        Returns:
            dict
        """

        filename = f"{uuid.uuid4().hex}.png"

        image_path = self.output_dir / filename

        url = f"https://image.pollinations.ai/prompt/{prompt}"

        response = requests.get(url)

        if response.status_code != 200:
            raise Exception("Failed to generate image.")

        with open(image_path, "wb") as file:
            file.write(response.content)

        return {
            "image_path": str(image_path),
            "message": "Image generated successfully."
        }


# ---------------------------------------------
# Testing
# ---------------------------------------------

if __name__ == "__main__":

    service = ImageService()

    result = service.generate_image(
        "Solar System educational diagram"
    )

    print(result)