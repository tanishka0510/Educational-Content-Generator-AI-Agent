from datetime import datetime, UTC
from pydantic import BaseModel, Field
from uuid import uuid4
from app.models.chunk import Chunk
class Document(BaseModel):
    document_id: str = Field(default_factory=lambda: str(uuid4()))

    filename: str
    file_path: str
    file_type: str

    source: str = "file"
    status: str = "uploaded"

    raw_text: str = ""             # text extract
    cleaned_text: str = ""         # clean text

# Analysis of the clean text

    subject: str = ""
    topics: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)

    language: str = "English"

    chunks: list[Chunk] = Field(default_factory=list)

    metadata: dict = Field(default_factory=dict)

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))