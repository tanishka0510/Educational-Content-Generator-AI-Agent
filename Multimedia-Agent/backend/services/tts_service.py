"""
Text-To-Speech Service

Converts educational text into speech using Microsoft Edge Neural TTS.
"""

import asyncio
import os
import tempfile
from pathlib import Path
from uuid import uuid4

import edge_tts

EDGE_TTS_VOICE = os.getenv("EDGE_TTS_VOICE", "en-US-AriaNeural")
FALLBACK_TTS_VOICE = "en-US-JennyNeural"
MULTIMEDIA_PUBLIC_URL = os.getenv("MULTIMEDIA_PUBLIC_URL", "http://127.0.0.1:8003")


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
                "audio_url": "...",
                "message": "..."
            }
        """

        if not text.strip():
            raise ValueError("Text cannot be empty.")

        filename = f"{uuid4().hex}.mp3"

        audio_path = self.output_dir / filename

        file_descriptor, temporary_path = tempfile.mkstemp(suffix=".mp3")
        os.close(file_descriptor)
        try:
            try:
                asyncio.run(edge_tts.Communicate(text, EDGE_TTS_VOICE).save(temporary_path))
            except Exception:
                asyncio.run(edge_tts.Communicate(text, FALLBACK_TTS_VOICE).save(temporary_path))
            Path(temporary_path).replace(audio_path)
        finally:
            temporary_file = Path(temporary_path)
            if temporary_file.exists():
                temporary_file.unlink()

        return {
            "audio_url": f"{MULTIMEDIA_PUBLIC_URL}/outputs/audio/{filename}",
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
