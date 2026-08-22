from typing import Optional

from pydantic import BaseModel, Field


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
        description="Number of questions required"
    )

    document_uploaded: bool = Field(
        default=False,
        description="Whether an uploaded document should be used"
    )