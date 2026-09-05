"""
Pydantic Schemas

Project: Educational Content Generator AI
Module: Orchestrator Agent (Gateway)
"""

import json
from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, Field, field_validator
try:
    import email_validator
    from pydantic import EmailStr
except ImportError:
    EmailStr = str




# ==========================================================
# User & Authentication Schemas
# ==========================================================

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None


# ==========================================================
# Chat History Schemas
# ==========================================================

class ChatMessageCreate(BaseModel):
    role: str
    content: Optional[str] = None
    comparison_table: Optional[Any] = None  # Dict or List depending on structure
    code: Optional[str] = None
    audio_url: Optional[str] = None


class ChatMessageResponse(BaseModel):
    id: int
    session_id: str
    role: str
    content: Optional[str] = None
    comparison_table: Optional[Any] = None
    code: Optional[str] = None
    audio_url: Optional[str] = None
    created_at: datetime

    @field_validator("comparison_table", mode="before")
    @classmethod
    def parse_comparison_table(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return v
        return v

    class Config:
        from_attributes = True


class ChatSessionCreate(BaseModel):
    id: str
    subject: str
    title: str


class ChatSessionUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)


class ChatSessionResponse(BaseModel):
    id: str
    subject: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessageResponse] = []

    class Config:
        from_attributes = True


# ==========================================================
# Quiz & Progress Tracking Schemas
# ==========================================================

class QuizResultCreate(BaseModel):
    subject: str
    topic: Optional[str] = None
    difficulty: str
    score: int
    total_questions: int
    answers_detail: Optional[Any] = None


class QuizResultResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    subject: str
    topic: Optional[str] = None
    difficulty: str
    score: int
    total_questions: int
    answers_detail: Optional[Any] = None
    created_at: datetime

    @field_validator("answers_detail", mode="before")
    @classmethod
    def parse_answers_detail(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return v
        return v

    class Config:
        from_attributes = True


# ==========================================================
# Flashcard Progress & Attempts Schemas
# ==========================================================

class FlashcardProgressUpdate(BaseModel):
    subject: str
    topic: Optional[str] = None
    card_id: str
    grade: str  # 'easy', 'medium', 'hard'


class FlashcardProgressResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    subject: str
    topic: Optional[str] = None
    card_id: str
    ease_factor: float
    repetitions: int
    interval_days: int
    next_review_at: datetime

    class Config:
        from_attributes = True


class FlashcardAttemptCreate(BaseModel):
    subject: str
    topic: Optional[str] = None
    difficulty: str = "medium"
    total_cards: int
    cards_reviewed: int
    easy_count: int = 0
    medium_count: int = 0
    hard_count: int = 0


class FlashcardAttemptResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    subject: str
    topic: Optional[str] = None
    difficulty: str
    total_cards: int
    cards_reviewed: int
    easy_count: int
    medium_count: int
    hard_count: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==========================================================
# Uploaded Document Schemas
# ==========================================================

class UploadedDocumentCreate(BaseModel):
    filename: str
    file_type: str
    file_size: int = 0
    subject: str
    topic: Optional[str] = None
    chunks_count: int = 0
    status: str = "Indexed"


class UploadedDocumentResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    filename: str
    file_type: str
    file_size: int
    subject: str
    topic: Optional[str] = None
    chunks_count: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

