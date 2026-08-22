"""
Quiz API Router

Provides the endpoint used by the Educational Content
Generator to retrieve source material for quiz generation.
"""

from fastapi import APIRouter, HTTPException

from app.schemas.quiz_retrieval_schema import QuizRetrievalRequest
from app.services.quiz_retrieval import retrieve_quiz_context


# ============================================================
# Router
# ============================================================

router = APIRouter(
    prefix="/quiz",
    tags=["Quiz"],
)


# ============================================================
# Generate Quiz Context
# ============================================================

@router.post("/retrieve")
def retrieve_quiz(request: QuizRetrievalRequest):

    try:

        result = retrieve_quiz_context(
            subject=request.subject,
            unit=request.unit,
            topic=request.topic,
            difficulty=request.difficulty,
            number_of_questions=request.number_of_questions,
            document_uploaded=request.document_uploaded,
        )

        return result

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:

        print("\n========== QUIZ RETRIEVAL ERROR ==========")
        print(e)
        print("===========================================\n")

        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve quiz context.",
        )