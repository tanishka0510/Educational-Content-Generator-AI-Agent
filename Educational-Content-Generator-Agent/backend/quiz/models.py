from typing import List, Optional

from pydantic import BaseModel, Field


# ============================================================
# QUIZ GENERATION REQUEST
# ============================================================

class QuizRequest(BaseModel):
    subject: str = Field(
        ...,
        description="Selected academic subject"
    )

    unit: Optional[str] = Field(
        default=None,
        description="Selected unit or chapter"
    )

    topic: Optional[str] = Field(
        default=None,
        description="Selected topic"
    )

    difficulty: str = Field(
        ...,
        description="Quiz difficulty: easy, medium, or hard"
    )

    number_of_questions: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of questions to generate"
    )

    document_uploaded: bool = Field(
        default=False,
        description="Whether quiz should use the uploaded document"
    )


# ============================================================
# QUIZ QUESTION
# ============================================================

class QuizQuestion(BaseModel):

    id: int

    question: str

    options: List[str] = Field(
        ...,
        min_length=4,
        max_length=4
    )

    correct_answer: str

    explanation: str


# ============================================================
# QUIZ RESPONSE
# ============================================================

class QuizResponse(BaseModel):

    quiz_title: str

    subject: str

    unit: Optional[str] = None

    topic: Optional[str] = None

    difficulty: str

    questions: List[QuizQuestion]