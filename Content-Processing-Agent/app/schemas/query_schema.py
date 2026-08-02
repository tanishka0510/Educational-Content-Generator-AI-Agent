from typing import Optional
from pydantic import BaseModel

class QueryRequest(BaseModel):
    subject: Optional[str] = None
    question: str