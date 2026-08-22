"""
Quiz Router

This file exposes the quiz generation API endpoint.

Flow:

Frontend
    ↓
POST /quiz/generate
    ↓
Quiz Router
    ↓
Quiz Service
    ↓
Content Processing Agent
    ↓
Gemini
    ↓
Quiz Response
"""

from fastapi import APIRouter, HTTPException

from quiz.schemas import (
    QuizGenerateRequest,
    QuizGenerateResponse,
)

from quiz.service import generate_quiz


# ============================================================
# Create Router
# ============================================================

router = APIRouter(
    prefix="/quiz",
    tags=["Quiz"],
)


# ============================================================
# Generate Quiz
# ============================================================

@router.post(
    "/generate",
    response_model=QuizGenerateResponse,
)
def generate_quiz_endpoint(
    request: QuizGenerateRequest,
):

    """
    Generate a quiz based on:

    - Subject
    - Unit / Chapter
    - Topic
    - Difficulty
    - Number of questions
    - Uploaded document
    """

    try:

        result = generate_quiz(request)

        return result

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:

        print(
            "\n========== QUIZ GENERATION ERROR =========="
        )

        print(
            "Error:",
            str(e),
        )

        print(
            "============================================"
        )

        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during quiz generation.",
        )