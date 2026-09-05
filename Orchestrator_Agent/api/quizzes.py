"""
Quiz Router

Project: Educational Content Generator AI
Module: Orchestrator Agent (Gateway)
"""

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from database.connection import get_db
from database.crud import create_quiz_result, get_user_quizzes
from database.schemas import QuizResultCreate, QuizResultResponse
from database.models import User
from utils.security import get_current_user, get_optional_user

router = APIRouter(prefix="/quiz", tags=["Quiz"])

EDUCATIONAL_AGENT_URL = "http://localhost:8002"
CONTENT_PROCESSING_URL = "http://localhost:8001"
TIMEOUT = 60.0


# Input schema for generating quiz
from pydantic import BaseModel
class QuizGenerateGatewayRequest(BaseModel):
    subject: Optional[str] = None
    unit: Optional[str] = None
    topic: Optional[str] = None
    difficulty: str = "medium"
    number_of_questions: int = 5
    document_uploaded: bool = False


@router.post("/generate")
def generate_quiz_endpoint(
    req: QuizGenerateGatewayRequest,
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Requests the Educational Agent to generate a quiz.
    Allows guest users up to trial limit, as well as authenticated users.
    """
    subject = req.subject.strip() if req.subject else ""
    if not subject and req.topic:
        try:
            with httpx.Client() as client:
                detection_response = client.get(
                    f"{CONTENT_PROCESSING_URL}/detect-subject",
                    params={"question": req.topic},
                    timeout=TIMEOUT,
                )
                if detection_response.status_code == 200:
                    subject = detection_response.json().get("subject") or ""
        except httpx.RequestError:
            pass

    if not subject:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please include a recognizable subject in the topic.",
        )

    url = f"{EDUCATIONAL_AGENT_URL}/quiz/generate"
    payload = {
        "subject": subject,
        "unit": req.unit,
        "topic": req.topic,
        "difficulty": req.difficulty,
        "number_of_questions": req.number_of_questions,
        "document_uploaded": req.document_uploaded
    }
    
    try:
        with httpx.Client() as client:
            response = client.post(url, json=payload, timeout=TIMEOUT)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Educational Agent returned error: {response.text}"
                )
            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Could not connect to Educational Agent: {str(e)}"
        )


@router.post("/submit", response_model=QuizResultResponse)
def submit_quiz_result(
    result: QuizResultCreate,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Logs the user's score in a taken quiz for dashboard statistics and study data persistence.
    """
    user_id = current_user.id if current_user else None
    return create_quiz_result(db=db, result=result, user_id=user_id)


@router.get("/history", response_model=List[QuizResultResponse])
def get_quiz_history(
    subject: Optional[str] = None,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves the quiz history for the authenticated user or guest.
    """
    user_id = current_user.id if current_user else None
    return get_user_quizzes(db=db, user_id=user_id, subject=subject)

