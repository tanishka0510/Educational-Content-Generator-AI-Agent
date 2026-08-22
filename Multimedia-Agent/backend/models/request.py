"""
Request models for the Multimedia Agent.
"""

from typing import Optional

from pydantic import BaseModel, Field


class SummaryRequest(BaseModel):
    """
    Request for generating a text summary.
    """
    text: str = Field(
        ...,
        description="Educational content to summarize."
    )


class TextToSpeechRequest(BaseModel):
    """
    Request for converting text into speech.
    """
    text: str = Field(
        ...,
        description="Educational text to convert into audio."
    )


class SpeechToTextRequest(BaseModel):
    """
    Request for transcribing an audio file.
    """
    audio_path: str = Field(
        ...,
        description="Path to the uploaded audio file."
    )


class VoiceQuestionRequest(BaseModel):
    """
    Request for answering a question using educational context.
    """
    question: str = Field(
        ...,
        description="Question asked by the user."
    )

    context: str = Field(
        ...,
        description="Educational context used to answer the question."
    )


class AudioSummaryRequest(BaseModel):
    """
    Request for generating an audio summary.
    """
    text: str = Field(
        ...,
        description="Educational content to summarize and convert to audio."
    )

class OCRRequest(BaseModel):
    """
    Request for extracting text from an image.
    """

    image_path: str = Field(
        ...,
        description="Path to the image for OCR processing."
    )

class MultimediaPipelineRequest(BaseModel):
    """
    Request for generating complete multimedia educational content.
    """

    text: str = Field(
        ...,
        description="Educational content to process."
    )

    generate_summary: bool = True
    generate_audio: bool = True
    generate_image: bool = False


class MultimediaRequest(BaseModel):
    """
    Generic request model for the Multimedia Agent.
    Useful for future LangGraph integration.
    """

    text: Optional[str] = None

    question: Optional[str] = None

    context: Optional[str] = None

    audio_path: Optional[str] = None

    image_path: Optional[str] = None

    generate_summary: Optional[bool] = None

    generate_audio: Optional[bool] = None

    generate_image: Optional[bool] = None