"""
Flashcard Router

Project: Educational Content Generator AI
Module: Orchestrator Agent (Gateway)
"""

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from database.connection import get_db
from database.crud import (
    update_flashcard_progress, get_user_flashcard_progress,
    create_flashcard_attempt, get_user_flashcard_attempts
)
from database.schemas import (
    FlashcardProgressUpdate, FlashcardProgressResponse,
    FlashcardAttemptCreate, FlashcardAttemptResponse
)
from database.models import User
from utils.security import get_current_user, get_optional_user

router = APIRouter(prefix="/flashcards", tags=["Flashcards"])
import os
EDUCATIONAL_AGENT_URL = os.getenv(
    "EDUCATIONAL_AGENT_URL",
    "http://localhost:8002"
)
TIMEOUT = 60.0


# Input schema for generating flashcards
from pydantic import BaseModel
class FlashcardGenerateGatewayRequest(BaseModel):
    subject: str
    unit: Optional[str] = None
    topic: Optional[str] = None
    difficulty: str = "medium"
    number_of_cards: int = 5
    document_uploaded: bool = False


@router.post("/generate")
def generate_flashcards_endpoint(
    req: FlashcardGenerateGatewayRequest,
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Requests the Educational Agent to generate flashcards.
    Allows guest users up to trial limit, as well as authenticated users.
    """
    url = f"{EDUCATIONAL_AGENT_URL}/flashcards/generate"
    payload = {
        "subject": req.subject,
        "unit": req.unit,
        "topic": req.topic,
        "difficulty": req.difficulty,
        "number_of_cards": req.number_of_cards,
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


@router.post("/submit", response_model=FlashcardProgressResponse)
def submit_flashcard_progress(
    update: FlashcardProgressUpdate,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Updates the spaced repetition progress for a specific flashcard.
    Grading Options: 'easy', 'medium', 'hard'.
    """
    user_id = current_user.id if current_user else 1
    return update_flashcard_progress(db=db, update=update, user_id=user_id)


@router.get("/history", response_model=List[FlashcardProgressResponse])
def get_flashcards_history(
    subject: Optional[str] = None,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves the review status of flashcards for the user.
    """
    user_id = current_user.id if current_user else 1
    return get_user_flashcard_progress(db=db, user_id=user_id, subject=subject)


@router.post("/attempt", response_model=FlashcardAttemptResponse)
def record_flashcard_attempt_endpoint(
    attempt: FlashcardAttemptCreate,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Records a completed flashcard deck review session in the database.
    """
    user_id = current_user.id if current_user else None
    return create_flashcard_attempt(db=db, attempt=attempt, user_id=user_id)


@router.get("/attempts", response_model=List[FlashcardAttemptResponse])
def get_flashcard_attempts_endpoint(
    subject: Optional[str] = None,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves all flashcard deck attempt sessions for the user.
    """
    user_id = current_user.id if current_user else None
    return get_user_flashcard_attempts(db=db, user_id=user_id, subject=subject)

