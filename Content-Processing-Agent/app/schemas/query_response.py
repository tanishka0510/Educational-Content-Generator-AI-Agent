from typing import List, Optional
from pydantic import BaseModel


class VideoResponse(BaseModel):
    title: str
    channel: str
    description: str
    url: str
    thumbnail: str
    published_at: str


class ResourceResponse(BaseModel):
    title: str
    description: str
    url: str
    provider: str


class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: List[str]
    retrieval_score: float | None = None

    videos: Optional[List[VideoResponse]] = None
    khan: Optional[List[ResourceResponse]] = None
    nptel: Optional[List[ResourceResponse]] = None