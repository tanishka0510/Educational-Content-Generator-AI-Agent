"""
Text-To-Speech Service

Converts educational text into speech using gTTS.
"""

from pathlib import Path
from uuid import uuid4

from gtts import gTTS


class TextToSpeechService:
    """
    Service responsible for converting text into speech.
    """

    def __init__(self):
        self.output_dir = Path("backend/outputs/audio")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def text_to_speech(self, text: str) -> dict:
        """
        Convert text into an MP3 audio file.

        Args:
            text (str): Input text.

        Returns:
            dict:
            {
                "audio_path": "...",
                "message": "..."
            }
        """

        if not text.strip():
            raise ValueError("Text cannot be empty.")

        filename = f"{uuid4().hex}.mp3"

        audio_path = self.output_dir / filename

        tts = gTTS(
            text=text,
            lang="en",
            slow=False
        )

        tts.save(audio_path)

        return {
            "audio_path": str(audio_path),
            "message": "Audio generated successfully."
        }


# -----------------------------------------------------
# Testing
# -----------------------------------------------------

if __name__ == "__main__":

    service = TextToSpeechService()

    result = service.text_to_speech(
        """
        Artificial Intelligence is transforming education
        by enabling personalized learning experiences.
        """
    )

    print(result)