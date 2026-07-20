from typing import List
from pydantic import BaseModel


class ProcessedContentResponse(BaseModel):
    summary: str
    learning_objectives: List[str]
    keywords: List[str]
    concepts: List[str]
    difficulty: str
    sources: List[str]