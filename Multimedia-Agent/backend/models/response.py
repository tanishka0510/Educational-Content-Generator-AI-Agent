"""
Response models for the Multimedia Agent.
"""

from typing import Optional

from pydantic import BaseModel, Field


class SummaryResponse(BaseModel):
    """
    Response returned after generating a text summary.
    """

    success: bool = True

    summary: str = Field(
        ...,
        description="Generated summary."
    )


class AudioResponse(BaseModel):
    """
    Response returned after generating audio.
    """

    success: bool = True

    audio_path: str = Field(
        ...,
        description="Path to generated audio file."
    )

    message: str = "Audio generated successfully."


class TranscriptResponse(BaseModel):
    """
    Response returned after speech-to-text conversion.
    """

    success: bool = True

    transcript: str = Field(
        ...,
        description="Transcript extracted from audio."
    )


class QuestionAnswerResponse(BaseModel):
    """
    Response returned after answering a question.
    """

    success: bool = True

    answer: str = Field(
        ...,
        description="Answer generated from educational context."
    )


class AudioSummaryResponse(BaseModel):
    """
    Response returned after generating an audio summary.
    """

    success: bool = True

    summary: str = Field(
        ...,
        description="Generated text summary."
    )

    audio_path: str = Field(
        ...,
        description="Generated audio file path."
    )


class ErrorResponse(BaseModel):
    """
    Standard error response.
    """

    success: bool = False

    error: str = Field(
        ...,
        description="Error message."
    )


class HealthResponse(BaseModel):
    """
    Health check response.
    """

    success: bool = True

    status: str = "Running"

    service: str = "Multimedia Agent"