from typing import Optional
from pydantic import BaseModel

class QueryRequest(BaseModel):

    subject: Optional[str] = None
    question: str
    document_uploaded: bool = False
    filename: Optional[str] = None
    document_name: Optional[str] = None
    subject_hint: Optional[str] = None
