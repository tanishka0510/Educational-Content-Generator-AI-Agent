"""
Flashcards API Router

Project: Educational Content Generator AI
Module: Educational Agent
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional

from services.flashcard_generator import generate_flashcards

router = APIRouter(prefix="/flashcards", tags=["Flashcards"])


class FlashcardRequest(BaseModel):
    subject: str
    unit: Optional[str] = None
    topic: Optional[str] = None
    difficulty: str = "medium"
    number_of_cards: int = 5
    document_uploaded: bool = False


@router.post("/generate")
def generate_flashcards_endpoint(req: FlashcardRequest):
    """
    Endpoint that generates flashcards based on subject RAG context.
    """
    try:
        cards = generate_flashcards(
            subject=req.subject,
            unit=req.unit,
            topic=req.topic,
            difficulty=req.difficulty,
            number_of_cards=req.number_of_cards,
            document_uploaded=req.document_uploaded
        )
        
        if "error" in cards:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=cards["error"]
            )
            
        return cards
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Flashcard generation failed: {str(e)}"
        )
