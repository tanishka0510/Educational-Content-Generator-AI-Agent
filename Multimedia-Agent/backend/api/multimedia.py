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
    MultimediaPipelineRequest,
)

from backend.models.response import (
    SummaryResponse,
    AudioResponse,
    TranscriptResponse,
    QuestionAnswerResponse,
    MultimediaPipelineResponse,
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

# ==================================================
# ADD THE NEW /process ENDPOINT HERE
# ==================================================

@router.post(
    "/process",
    response_model=MultimediaPipelineResponse
)
def process_multimedia(request: MultimediaPipelineRequest):

    try:

        summary = None
        audio_path = None
        image_path = None

        # Generate Summary
        if request.generate_summary:
            summary = summary_service.generate_summary(
                request.text
            )

        # Generate Audio
        if request.generate_audio:

            text_for_audio = summary if summary else request.text

            audio_result = tts_service.text_to_speech(
                text_for_audio
            )

            audio_path = audio_result["audio_path"]

        # Generate Educational Image
        if request.generate_image:

            image_result = image_service.generate_image(
                request.text
            )

            # Adjust this key according to image_service.py
            image_path = image_result.get("image_path")

        return MultimediaPipelineResponse(
            success=True,
            summary=summary,
            audio_path=audio_path,
            image_path=image_path
        )

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