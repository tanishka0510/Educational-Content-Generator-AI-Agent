"""
Image Generation Service

Generates educational images using Pollinations AI.
"""

import os
from urllib.parse import quote

import requests
from dotenv import load_dotenv


load_dotenv()


class ImageService:
    """
    Service responsible for generating images.
    """

    _BASE_URL = "https://gen.pollinations.ai"
    _PRIMARY_MODEL = "ideogram-v4-quality"
    _FALLBACK_MODEL = "gptimage"

    def _educational_prompt(self, prompt: str) -> str:
        return (
            "Create a professional university-level computer-science educational "
            "diagram based on this request: "
            f"{prompt}. Use a clean vector infographic style, high resolution, "
            "sharp readable typography, accurate spelling, a simple uncluttered "
            "layout, high contrast, logically connected arrows, and clearly "
            "separated sections. Include only necessary labels and use diagrams, "
            "flowcharts, architecture diagrams, concept maps, or process diagrams "
            "when appropriate instead of photorealistic imagery. Do not include "
            "decorative or random text, watermarks, logos, irrelevant objects, or "
            "misspelled labels. Make it suitable for a university computer-science "
            "educational platform and professionally designed like a textbook "
            "illustration."
        )

    @staticmethod
    def _safe_error(error: Exception) -> str:
        message = str(error)
        api_key = os.getenv("POLLINATIONS_API_KEY")
        if api_key:
            message = message.replace(api_key, "[REDACTED]")
        return message

    def _request_image(self, prompt: str, model: str, api_key: str) -> str:
        encoded_prompt = quote(prompt, safe="")
        image_url = f"{self._BASE_URL}/image/{encoded_prompt}?model={model}"
        response = requests.get(
            image_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=90,
        )
        if response.status_code != 200:
            raise RuntimeError(
                f"Pollinations returned HTTP {response.status_code} for model {model}."
            )
        return image_url

    def generate_image(self, prompt: str) -> dict:
        """
        Generate an image from a text prompt.

        Args:
            prompt (str): Image generation prompt.

        Returns:
            dict
        """

        api_key = os.getenv("POLLINATIONS_API_KEY")
        if not api_key:
            raise RuntimeError("POLLINATIONS_API_KEY is not configured.")

        educational_prompt = self._educational_prompt(prompt)
        try:
            image_url = self._request_image(educational_prompt, self._PRIMARY_MODEL, api_key)
        except Exception as primary_error:
            print(f"Primary Pollinations image model failed: {self._safe_error(primary_error)}")
            image_url = self._request_image(educational_prompt, self._FALLBACK_MODEL, api_key)

        return {"image_url": image_url, "message": "Image generated successfully."}


# ---------------------------------------------
# Testing
# ---------------------------------------------

if __name__ == "__main__":

    service = ImageService()

    result = service.generate_image(
        "Solar System educational diagram"
    )

    print(result)
