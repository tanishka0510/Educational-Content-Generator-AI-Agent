"""
Video Service

Generates educational video scripts.
"""

from backend.config import get_llm


class VideoService:
    """
    Service responsible for preparing educational
    video content.
    """

    def __init__(self):

        self.llm = get_llm()

    def generate_video_script(self, topic: str) -> str:
        """
        Generate an educational video narration script.

        Args:
            topic (str)

        Returns:
            str
        """

        prompt = f"""
Create a 2-minute educational narration
about the following topic.

Topic:
{topic}

The narration should:

- be engaging
- be accurate
- be suitable for students
- include an introduction,
  explanation,
  and conclusion.
"""

        response = self.llm.invoke(prompt)

        return response.content.strip()


# ---------------------------------------------
# Testing
# ---------------------------------------------

if __name__ == "__main__":

    service = VideoService()

    script = service.generate_video_script(
        "Machine Learning"
    )

    print(script)