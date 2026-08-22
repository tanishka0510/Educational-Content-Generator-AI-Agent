from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


# ============================================================
# QUIZ GENERATION REQUEST
# ============================================================

class QuizGenerateRequest(BaseModel):
    """
    Request received from the frontend when generating a quiz.
    """

    subject: str = Field(
        ...,
        min_length=1,
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
        description="Whether the quiz should use the uploaded document"
    )

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, value: str) -> str:

        value = value.strip().lower()

        allowed_difficulties = {
            "easy",
            "medium",
            "hard",
        }

        if value not in allowed_difficulties:
            raise ValueError(
                "Difficulty must be one of: easy, medium, hard"
            )

        return value

    @field_validator("subject")
    @classmethod
    def validate_subject(cls, value: str) -> str:

        value = value.strip()

        if not value:
            raise ValueError(
                "Subject cannot be empty"
            )

        return value

    @field_validator("unit", "topic")
    @classmethod
    def clean_optional_values(
        cls,
        value: Optional[str]
    ) -> Optional[str]:

        if value is None:
            return None

        value = value.strip()

        return value if value else None


# ============================================================
# QUIZ QUESTION
# ============================================================

class QuizQuestionResponse(BaseModel):
    """
    Represents one generated multiple-choice question.
    """

    id: int

    question: str

    options: List[str] = Field(
        ...,
        min_length=4,
        max_length=4,
        description="Exactly four answer options"
    )

    correct_answer: str

    explanation: str

    # Useful metadata for frontend
    topic: Optional[str] = None

    difficulty: str


# ============================================================
# QUIZ RESPONSE
# ============================================================

class QuizGenerateResponse(BaseModel):
    """
    Complete response returned to the frontend.
    """

    quiz_title: str

    subject: str

    unit: Optional[str] = None

    topic: Optional[str] = None

    difficulty: str

    questions: List[QuizQuestionResponse]

    total_questions: int


# ============================================================
# QUIZ ANSWER
# ============================================================

class QuizAnswer(BaseModel):
    """
    Represents the user's answer to one question.
    """

    question_id: int

    selected_answer: str


# ============================================================
# QUIZ SUBMISSION
# ============================================================

class QuizSubmitRequest(BaseModel):
    """
    Request sent by the frontend when the user
    finishes attempting the quiz.
    """

    quiz_title: str

    answers: List[QuizAnswer]


# ============================================================
# RESULT FOR ONE QUESTION
# ============================================================

class QuizAnswerResult(BaseModel):

    question_id: int

    selected_answer: Optional[str] = None

    correct_answer: str

    is_correct: bool

    explanation: str


# ============================================================
# COMPLETE QUIZ RESULT
# ============================================================

class QuizResultResponse(BaseModel):

    quiz_title: str

    total_questions: int

    correct_answers: int

    incorrect_answers: int

    unanswered: int

    score: int

    percentage: float

    results: List[QuizAnswerResult]