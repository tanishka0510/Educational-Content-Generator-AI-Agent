from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    subject: str
    question: str
    document_uploaded: bool = False
    filename: Optional[str] = None