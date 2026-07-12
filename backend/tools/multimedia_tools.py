"""
LangChain tools for the Multimedia Agent.

These tools are used by the LangGraph MultimediaAgent.
"""

from langchain_core.tools import tool

from backend.services.summary_service import SummaryService
from backend.services.tts_service import TextToSpeechService
from backend.services.stt_service import SpeechToTextService
from backend.services.question_answer_service import (
    QuestionAnswerService,
)

# ---------------------------------------------------
# Initialize Services
# ---------------------------------------------------

summary_service = SummaryService()

tts_service = TextToSpeechService()

stt_service = SpeechToTextService()

qa_service = QuestionAnswerService()


# ---------------------------------------------------
# Tool 1 : Generate Summary
# ---------------------------------------------------

@tool
def generate_text_summary(text: str) -> str:
    """
    Generate a concise educational summary.

    Args:
        text (str): Educational content.

    Returns:
        str: Summary
    """
    return summary_service.generate_summary(text)


# ---------------------------------------------------
# Tool 2 : Text To Speech
# ---------------------------------------------------

@tool
def text_to_speech(text: str) -> dict:
    """
    Convert text into speech.

    Args:
        text (str)

    Returns:
        dict
    """
    return tts_service.text_to_speech(text)


# ---------------------------------------------------
# Tool 3 : Speech To Text
# ---------------------------------------------------

@tool
def speech_to_text(audio_path: str) -> str:
    """
    Convert speech into text.

    Args:
        audio_path (str)

    Returns:
        str
    """
    return stt_service.speech_to_text(audio_path)


# ---------------------------------------------------
# Tool 4 : Voice Question Answer
# ---------------------------------------------------

@tool
def voice_question_answer(
    question: str,
    context: str
) -> str:
    """
    Answer educational questions.

    Args:
        question (str)
        context (str)

    Returns:
        str
    """

    return qa_service.answer_question(
        question,
        context
    )


# ---------------------------------------------------
# Tool 5 : Audio Summary
# ---------------------------------------------------

@tool
def generate_audio_summary(text: str) -> dict:
    """
    Generate a spoken summary.

    Steps
    -----
    1. Generate summary
    2. Convert summary to speech

    Returns
    -------
    dict
    """

    summary = summary_service.generate_summary(text)

    audio = tts_service.text_to_speech(summary)

    return {
        "summary": summary,
        "audio_path": audio["audio_path"],
        "message": "Audio summary generated successfully."
    }


# ---------------------------------------------------
# Export Tool List
# ---------------------------------------------------

MULTIMEDIA_TOOLS = [
    generate_text_summary,
    text_to_speech,
    speech_to_text,
    voice_question_answer,
    generate_audio_summary,
]