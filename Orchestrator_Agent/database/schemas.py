"""
Pydantic Schemas

Project: Educational Content Generator AI
Module: Orchestrator Agent (Gateway)
"""

from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, EmailStr, Field


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


class ChatMessageResponse(BaseModel):
    id: int
    session_id: str
    role: str
    content: Optional[str] = None
    comparison_table: Optional[Any] = None
    code: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ChatSessionCreate(BaseModel):
    id: str
    subject: str
    title: str


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


class QuizResultResponse(BaseModel):
    id: int
    user_id: int
    subject: str
    topic: Optional[str] = None
    difficulty: str
    score: int
    total_questions: int
    created_at: datetime

    class Config:
        from_attributes = True


class FlashcardProgressUpdate(BaseModel):
    subject: str
    topic: Optional[str] = None
    card_id: str
    grade: str  # 'easy', 'medium', 'hard'


class FlashcardProgressResponse(BaseModel):
    id: int
    user_id: int
    subject: str
    topic: Optional[str] = None
    card_id: str
    ease_factor: float
    repetitions: int
    interval_days: int
    next_review_at: datetime

    class Config:
        from_attributes = True
