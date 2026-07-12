"""
Chunk Model

Represents one chunk of a document.
"""

from datetime import datetime, UTC
from uuid import uuid4

from pydantic import BaseModel, Field


class Chunk(BaseModel):
    """
    Represents a single document chunk.
    """

    chunk_id: str = Field(default_factory=lambda: str(uuid4()))

    document_id: str

    chunk_index: int

    text: str

    embedding: list[float] = Field(default_factory=list)

    metadata: dict = Field(default_factory=dict)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )