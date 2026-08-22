"""
Database ORM Models

Project: Educational Content Generator AI
Module: Orchestrator Agent (Gateway)
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship

from database.connection import Base


class User(Base):
    """Stores user registration and authentication details."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    quizzes = relationship("QuizResult", back_populates="user", cascade="all, delete-orphan")
    flashcards = relationship("FlashcardProgress", back_populates="user", cascade="all, delete-orphan")


class ChatSession(Base):
    """Groups message history by subject and user."""
    __tablename__ = "chat_sessions"

    id = Column(String(50), primary_key=True, index=True)  # uniquely generated session ID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    """Individual chat exchanges within a session."""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=True)
    comparison_table = Column(Text, nullable=True)  # JSON-stringified comparison table data
    code = Column(Text, nullable=True)  # optional generated code
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="messages")


class QuizResult(Base):
    """Logs the results of taken quizzes for progress reports."""
    __tablename__ = "quiz_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject = Column(String(50), nullable=False)
    topic = Column(String(100), nullable=True)
    difficulty = Column(String(20), nullable=False)
    score = Column(Integer, nullable=False)
    total_questions = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="quizzes")


class FlashcardProgress(Base):
    """Tracks card reviews for study progress and spaced repetition."""
    __tablename__ = "flashcard_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject = Column(String(50), nullable=False)
    topic = Column(String(100), nullable=True)
    card_id = Column(String(100), nullable=False)
    ease_factor = Column(Float, default=2.5)
    repetitions = Column(Integer, default=0)
    interval_days = Column(Integer, default=0)
    next_review_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="flashcards")
