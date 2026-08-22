"""
Database CRUD Operations

Project: Educational Content Generator AI
Module: Orchestrator Agent (Gateway)
"""

import json
from datetime import datetime, timedelta
from typing import List, Optional
import bcrypt
from sqlalchemy.orm import Session

from database.models import User, ChatSession, ChatMessage, QuizResult, FlashcardProgress
from database.schemas import UserCreate, ChatSessionCreate, ChatMessageCreate, QuizResultCreate, FlashcardProgressUpdate


# ==========================================================
# Password Hashing Setup (Direct bcrypt)
# ==========================================================

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against the stored bcrypt hash."""
    try:
        pwd_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(pwd_bytes, hashed_bytes)
    except Exception:
        return False


# ==========================================================
# User CRUD
# ==========================================================

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, user: UserCreate) -> User:
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# ==========================================================
# Chat History CRUD
# ==========================================================

def get_user_sessions(db: Session, user_id: int, subject: Optional[str] = None) -> List[ChatSession]:
    query = db.query(ChatSession).filter(ChatSession.user_id == user_id)
    if subject:
        query = query.filter(ChatSession.subject == subject)
    return query.order_by(ChatSession.updated_at.desc()).all()


def get_session_by_id(db: Session, session_id: str, user_id: int) -> Optional[ChatSession]:
    return db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == user_id
    ).first()


def create_session(db: Session, session: ChatSessionCreate, user_id: int) -> ChatSession:
    db_session = ChatSession(
        id=session.id,
        user_id=user_id,
        subject=session.subject,
        title=session.title
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


def create_chat_message(db: Session, message: ChatMessageCreate, session_id: str) -> ChatMessage:
    comparison_table_str = None
    if message.comparison_table is not None:
        comparison_table_str = json.dumps(message.comparison_table)

    db_message = ChatMessage(
        session_id=session_id,
        role=message.role,
        content=message.content,
        comparison_table=comparison_table_str,
        code=message.code
    )
    db.add(db_message)
    
    # Update parent session's update time
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if session:
        session.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(db_message)
    return db_message


def delete_session(db: Session, session_id: str, user_id: int) -> bool:
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == user_id
    ).first()
    if session:
        db.delete(session)
        db.commit()
        return True
    return False


# ==========================================================
# Quiz Results CRUD
# ==========================================================

def create_quiz_result(db: Session, result: QuizResultCreate, user_id: int) -> QuizResult:
    db_result = QuizResult(
        user_id=user_id,
        subject=result.subject,
        topic=result.topic,
        difficulty=result.difficulty,
        score=result.score,
        total_questions=result.total_questions
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result


def get_user_quizzes(db: Session, user_id: int, subject: Optional[str] = None) -> List[QuizResult]:
    query = db.query(QuizResult).filter(QuizResult.user_id == user_id)
    if subject:
        query = query.filter(QuizResult.subject == subject)
    return query.order_by(QuizResult.created_at.desc()).all()


# ==========================================================
# Flashcard Progress (Spaced Repetition) CRUD
# ==========================================================

def get_flashcard_progress(db: Session, user_id: int, card_id: str) -> Optional[FlashcardProgress]:
    return db.query(FlashcardProgress).filter(
        FlashcardProgress.user_id == user_id,
        FlashcardProgress.card_id == card_id
    ).first()


def update_flashcard_progress(db: Session, update: FlashcardProgressUpdate, user_id: int) -> FlashcardProgress:
    """
    Implements a simple SM-2 styled Spaced Repetition Algorithm.
    Grades:
    - 'hard': ease_factor decreases, schedule next review in 1 day
    - 'medium': keep ease_factor, schedule review in 3-6 days
    - 'easy': ease_factor increases, schedule review in 7-14 days
    """
    db_progress = get_flashcard_progress(db, user_id, update.card_id)
    
    if not db_progress:
        db_progress = FlashcardProgress(
            user_id=user_id,
            subject=update.subject,
            topic=update.topic,
            card_id=update.card_id,
            ease_factor=2.5,
            repetitions=0,
            interval_days=0
        )
        db.add(db_progress)

    # Apply algorithm based on student feedback grade
    grade = update.grade.lower()
    
    if grade == "hard":
        db_progress.ease_factor = max(1.3, db_progress.ease_factor - 0.2)
        db_progress.repetitions = 0
        db_progress.interval_days = 1
    elif grade == "medium":
        db_progress.repetitions += 1
        if db_progress.repetitions == 1:
            db_progress.interval_days = 3
        elif db_progress.repetitions == 2:
            db_progress.interval_days = 6
        else:
            db_progress.interval_days = int(db_progress.interval_days * db_progress.ease_factor)
    elif grade == "easy":
        db_progress.ease_factor = db_progress.ease_factor + 0.15
        db_progress.repetitions += 1
        if db_progress.repetitions == 1:
            db_progress.interval_days = 7
        elif db_progress.repetitions == 2:
            db_progress.interval_days = 14
        else:
            db_progress.interval_days = int(db_progress.interval_days * db_progress.ease_factor * 1.2)
    else:
        # Default fallback
        db_progress.interval_days = 1

    db_progress.next_review_at = datetime.utcnow() + timedelta(days=db_progress.interval_days)
    
    db.commit()
    db.refresh(db_progress)
    return db_progress


def get_user_flashcard_progress(db: Session, user_id: int, subject: Optional[str] = None) -> List[FlashcardProgress]:
    query = db.query(FlashcardProgress).filter(FlashcardProgress.user_id == user_id)
    if subject:
        query = query.filter(FlashcardProgress.subject == subject)
    return query.all()
