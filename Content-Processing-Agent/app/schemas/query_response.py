from pydantic import BaseModel
from typing import List


class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: List[str]