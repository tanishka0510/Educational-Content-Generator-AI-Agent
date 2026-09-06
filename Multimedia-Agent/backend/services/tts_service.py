"""
Text-To-Speech Service

Converts educational text into speech using Microsoft Edge Neural TTS.
"""

import asyncio
import os
import shutil
import tempfile
from pathlib import Path
from uuid import uuid4

import edge_tts


# -----------------------------------------------------
# Configuration
# -----------------------------------------------------

EDGE_TTS_VOICE = os.getenv(
    "EDGE_TTS_VOICE",
    "en-US-AriaNeural"
)

FALLBACK_TTS_VOICE = "en-US-JennyNeural"

MULTIMEDIA_PUBLIC_URL = os.getenv(
    "MULTIMEDIA_PUBLIC_URL",
    "http://127.0.0.1:8003"
)


class TextToSpeechService:
    """
    Service responsible for converting text into speech.
    """

    def __init__(self):
        # Store generated audio files inside the Multimedia Agent.
        self.output_dir = Path("backend/outputs/audio")

        # Create the directory if it does not already exist.
        self.output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

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

        # -------------------------------------------------
        # Validate input
        # -------------------------------------------------

        if not text or not text.strip():
            raise ValueError("Text cannot be empty.")

        # -------------------------------------------------
        # Generate unique output filename
        # -------------------------------------------------

        filename = f"{uuid4().hex}.mp3"

        audio_path = self.output_dir / filename

        # -------------------------------------------------
        # Create temporary file
        # -------------------------------------------------

        file_descriptor, temporary_path = tempfile.mkstemp(
            suffix=".mp3"
        )

        # Close the descriptor because edge_tts will write
        # to the file itself.
        os.close(file_descriptor)

        temporary_file = Path(temporary_path)

        try:
            # -------------------------------------------------
            # Try primary Edge TTS voice
            # -------------------------------------------------

            try:
                asyncio.run(
                    edge_tts.Communicate(
                        text,
                        EDGE_TTS_VOICE
                    ).save(temporary_path)
                )

            # -------------------------------------------------
            # Fallback voice
            # -------------------------------------------------

            except Exception:
                asyncio.run(
                    edge_tts.Communicate(
                        text,
                        FALLBACK_TTS_VOICE
                    ).save(temporary_path)
                )

            # -------------------------------------------------
            # IMPORTANT:
            #
            # Do NOT use:
            # Path(temporary_path).replace(audio_path)
            #
            # Render may place /tmp and the application
            # directory on different filesystems.
            #
            # shutil.copy2() works across filesystems.
            # -------------------------------------------------

            shutil.copy2(
                temporary_path,
                audio_path
            )

        finally:
            # -------------------------------------------------
            # Remove temporary file
            # -------------------------------------------------

            if temporary_file.exists():
                temporary_file.unlink()

        # -------------------------------------------------
        # Create public audio URL
        # -------------------------------------------------

        audio_url = (
            f"{MULTIMEDIA_PUBLIC_URL}"
            f"/outputs/audio/{filename}"
        )

        # -------------------------------------------------
        # Return result
        # -------------------------------------------------

        return {
            "audio_url": audio_url,
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