from typing import List, Optional
from pydantic import BaseModel


# ==========================================================
# YouTube Response
# ==========================================================

class VideoResponse(BaseModel):

    title: str
    channel: str
    description: str
    url: str
    thumbnail: str
    published_at: str


# ==========================================================
# External Educational Resource
# ==========================================================

class ResourceResponse(BaseModel):

    title: str
    description: str
    url: str
    provider: str


# ==========================================================
# Comparison Table
# ==========================================================

class ComparisonTableResponse(BaseModel):

    columns: List[str]
    rows: List[List[str]]


# ==========================================================
# Processed Content Response
# ==========================================================

class ProcessedContentResponse(BaseModel):

    summary: str

    code: Optional[str] = None

    comparison_table: Optional[
        ComparisonTableResponse
    ] = None

    learning_objectives: List[str]

    keywords: List[str]

    concepts: List[str]

    difficulty: str

    sources: List[str]

    retrieval_score: Optional[float] = None

    videos: Optional[
        List[VideoResponse]
    ] = None

    khan: Optional[
        List[ResourceResponse]
    ] = None

    nptel: Optional[
        List[ResourceResponse]
    ] = None