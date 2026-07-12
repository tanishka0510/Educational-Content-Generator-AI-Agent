"""
Multimedia API Routes

FastAPI endpoints for the Multimedia Agent.
"""

from fastapi import APIRouter, HTTPException

from backend.models.request import (
    SummaryRequest,
    TextToSpeechRequest,
    SpeechToTextRequest,
    VoiceQuestionRequest,
)

from backend.models.response import (
    SummaryResponse,
    AudioResponse,
    TranscriptResponse,
    QuestionAnswerResponse,
)

from backend.services.summary_service import SummaryService
from backend.services.tts_service import TextToSpeechService
from backend.services.stt_service import SpeechToTextService
from backend.services.question_answer_service import (
    QuestionAnswerService,
)
from backend.services.image_service import ImageService
from backend.services.video_service import VideoService

router = APIRouter(
    prefix="/multimedia",
    tags=["Multimedia Agent"]
)

# --------------------------------------------------
# Initialize Services
# --------------------------------------------------

summary_service = SummaryService()
tts_service = TextToSpeechService()
stt_service = SpeechToTextService()
qa_service = QuestionAnswerService()
image_service = ImageService()
video_service = VideoService()


# --------------------------------------------------
# Generate Summary
# --------------------------------------------------

@router.post(
    "/summary",
    response_model=SummaryResponse
)
def generate_summary(request: SummaryRequest):

    try:

        summary = summary_service.generate_summary(
            request.text
        )

        return SummaryResponse(
            summary=summary
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# --------------------------------------------------
# Text To Speech
# --------------------------------------------------

@router.post(
    "/tts",
    response_model=AudioResponse
)
def text_to_speech(request: TextToSpeechRequest):

    try:

        result = tts_service.text_to_speech(
            request.text
        )

        return AudioResponse(
            audio_path=result["audio_path"],
            message=result["message"]
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# --------------------------------------------------
# Speech To Text
# --------------------------------------------------

@router.post(
    "/stt",
    response_model=TranscriptResponse
)
def speech_to_text(request: SpeechToTextRequest):

    try:

        transcript = stt_service.speech_to_text(
            request.audio_path
        )

        return TranscriptResponse(
            transcript=transcript
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# --------------------------------------------------
# Voice Question Answer
# --------------------------------------------------

@router.post(
    "/ask",
    response_model=QuestionAnswerResponse
)
def ask_question(request: VoiceQuestionRequest):

    try:

        answer = qa_service.answer_question(
            request.question,
            request.context
        )

        return QuestionAnswerResponse(
            answer=answer
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# --------------------------------------------------
# Generate Educational Image
# --------------------------------------------------

@router.post("/image")
def generate_image(prompt: str):

    try:

        return image_service.generate_image(prompt)

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# --------------------------------------------------
# Generate Video Script
# --------------------------------------------------

@router.post("/video")
def generate_video(topic: str):

    try:

        script = video_service.generate_video_script(
            topic
        )

        return {
            "script": script
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# --------------------------------------------------
# Health Check
# --------------------------------------------------

@router.get("/health")
def health():

    return {
        "status": "running",
        "service": "Multimedia Agent"
    }