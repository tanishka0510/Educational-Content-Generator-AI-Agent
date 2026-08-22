"""
Quiz Retrieval Schemas

Schemas used by the Content Processing Agent
to receive quiz-retrieval requests from the
Educational Content Generator.
"""

from typing import Optional

from pydantic import BaseModel, Field, field_validator


# ============================================================
# QUIZ RETRIEVAL REQUEST
# ============================================================

class QuizRetrievalRequest(BaseModel):
    """
    Request received from the Educational Content Generator
    when it needs study material for quiz generation.
    """

    subject: str = Field(
        ...,
        min_length=1,
        description="Selected academic subject",
    )

    unit: Optional[str] = Field(
        default=None,
        description="Selected unit or chapter",
    )

    topic: Optional[str] = Field(
        default=None,
        description="Selected topic",
    )

    difficulty: str = Field(
        ...,
        description="Quiz difficulty: easy, medium, or hard",
    )

    number_of_questions: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of questions required",
    )

    document_uploaded: bool = Field(
        default=False,
        description="Whether an uploaded document should be used",
    )

    # ========================================================
    # VALIDATE DIFFICULTY
    # ========================================================

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

    # ========================================================
    # VALIDATE SUBJECT
    # ========================================================

    @field_validator("subject")
    @classmethod
    def validate_subject(cls, value: str) -> str:

        value = value.strip()

        if not value:
            raise ValueError(
                "Subject cannot be empty"
            )

        return value

    # ========================================================
    # CLEAN OPTIONAL VALUES
    # ========================================================

    @field_validator("unit", "topic")
    @classmethod
    def clean_optional_values(
        cls,
        value: Optional[str],
    ) -> Optional[str]:

        if value is None:
            return None

        value = value.strip()

        return value if value else None