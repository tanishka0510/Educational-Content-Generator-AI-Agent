from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    subject: Optional[str] = None
    question: str
    document_uploaded: bool = False
    filename: Optional[str] = None