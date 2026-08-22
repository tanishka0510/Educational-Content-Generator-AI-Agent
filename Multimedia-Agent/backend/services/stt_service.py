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
        self.groq_key = Settings.GROQ_API_KEY
        if self.groq_key:
            self.client = Groq(api_key=self.groq_key)
        else:
            self.client = None

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

        # Fallback to Gemini if Groq key is not provided
        if not self.groq_key:
            import os
            from google import genai
            
            gemini_key = os.getenv("GEMINI_API_KEY")
            if not gemini_key:
                raise ValueError("Neither GROQ_API_KEY nor GEMINI_API_KEY was found in environment.")
                
            print("Groq API key not found. Transcribing audio via Gemini model...")
            client = genai.Client(api_key=gemini_key)
            
            # Upload the file to Gemini storage
            uploaded_file = client.files.upload(file=audio_file)
            
            try:
                # Transcribe using Gemini 2.5 Flash
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[
                        uploaded_file,
                        "Provide the exact transcription of this audio. Return ONLY the spoken text, without any added explanation, greeting, or meta-comments."
                    ]
                )
                return response.text.strip()
            finally:
                # Ensure we clean up the file from Gemini storage
                try:
                    client.files.delete(name=uploaded_file.name)
                except Exception as e:
                    print(f"Failed to delete temporary Gemini file: {e}")

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