"""
Speech-To-Text Service

Transcribes audio files using Groq Whisper.
"""

from pathlib import Path
import os

from groq import Groq

from backend.config import Settings


class SpeechToTextService:
    """
    Service responsible for converting speech into text.
    """

    def __init__(self):
        self.client = Groq(api_key=Settings.GROQ_API_KEY)

    def speech_to_text(self, audio_path: str) -> str:
        """
        Convert an audio file to text.

        Args:
            audio_path (str): Path to the audio file.

        Returns:
            str: Transcript.
        """

        audio_file = Path(audio_path)

        if not audio_file.exists():
            raise FileNotFoundError(
                f"Audio file not found: {audio_path}"
            )

        with open(audio_file, "rb") as file:

            transcription = self.client.audio.transcriptions.create(
                file=file,
                model="whisper-large-v3"
            )

        return transcription.text


# -----------------------------------------------------
# Testing
# -----------------------------------------------------

if __name__ == "__main__":

    service = SpeechToTextService()

    transcript = service.speech_to_text(
        "backend/outputs/audio/sample.mp3"
    )

    print("\nTranscript:\n")

    print(transcript)