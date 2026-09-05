"""
Chat and Content Processing Router

Project: Educational Content Generator AI
Module: Orchestrator Agent (Gateway)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from uuid import uuid4

from database.connection import get_db
from database.crud import (
    get_user_sessions, get_session_by_id, create_session,
    create_chat_message, delete_session
)
from database.schemas import (
    ChatSessionResponse, ChatMessageCreate,
    ChatSessionCreate, ChatSessionUpdate
)

from database.models import User
from utils.security import get_current_user, SECRET_KEY, ALGORITHM
from agent import run_orchestrator

router = APIRouter(tags=["Chats & Content Processing"])
security_bearer = HTTPBearer(auto_error=False)


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Dependency to retrieve the logged-in user if token is present."""
    if not credentials:
        return None
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str: str = payload.get("sub")
        if not user_id_str:
            return None
        from database.crud import get_user_by_id
        return get_user_by_id(db, int(user_id_str))
    except Exception:
        return None


# Input Schema
from pydantic import BaseModel
class ProcessContentRequest(BaseModel):
    subject: Optional[str] = None
    question: str
    document_uploaded: bool
    session_id: Optional[str] = None
    document_name: Optional[str] = None
    filename: Optional[str] = None


@router.post("/process-content")
def process_content_endpoint(
    req: ProcessContentRequest,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Main entry point for routing user queries. Runs the multi-agent Orchestrator.
    Saves conversation history and session details in the persistent database.
    """
    session_id = req.session_id
    user_id = current_user.id if current_user else None
    
    # 1. Resolve / Create Session details in the database
    storage_subject = req.subject or "GENERAL"
    existing_session = None
    if session_id:
        existing_session = get_session_by_id(db, session_id=session_id, user_id=user_id)

    if not session_id:
        session_id = f"sess-{uuid4().hex[:12]}"
        title = req.question[:45] + "..." if len(req.question) > 45 else req.question
        existing_session = create_session(
            db=db,
            session=ChatSessionCreate(id=session_id, subject=storage_subject, title=title),
            user_id=user_id
        )
    else:
        session = existing_session
        if not session:
            title = req.question[:45] + "..." if len(req.question) > 45 else req.question
            existing_session = create_session(
                db=db,
                session=ChatSessionCreate(id=session_id, subject=storage_subject, title=title),
                user_id=user_id
            )

    # Save User's Question to Database
    create_chat_message(
        db=db,
        message=ChatMessageCreate(role="user", content=req.question),
        session_id=session_id
    )

    # 2. Run Orchestrator Pipeline
    doc_name = req.document_name or req.filename
    orchestrator_response = run_orchestrator(
        query=req.question,
        session_id=session_id or "temp-session",
        subject=req.subject,
        subject_hint=(existing_session.subject if existing_session and existing_session.subject != "GENERAL" else None),
        document_uploaded=req.document_uploaded,
        document_name=doc_name
    )
    
    # 3. Extract outputs
    data = orchestrator_response.get("data", {})
    edu_output = data.get("educational_output", {}) or {}
    processed_content = data.get("processed_content", {}) or {}
    multimedia_output = data.get("multimedia_output", {}) or {}
    resolved_subject = processed_content.get("subject") or edu_output.get("subject") or req.subject
    if resolved_subject and existing_session and existing_session.subject != resolved_subject:
        existing_session.subject = resolved_subject
        db.commit()
    
    # 4. Construct client response
    audio_path = multimedia_output.get("audio_path")
    audio_url = multimedia_output.get("audio_url")
    if not audio_url and audio_path:
        from pathlib import Path
        filename = Path(audio_path).name
        audio_url = f"http://localhost:8003/outputs/audio/{filename}"

    client_response = {
        "answer": edu_output.get("answer") or edu_output.get("summary") or processed_content.get("summary") or "Unable to generate an answer.",
        "summary": processed_content.get("summary"),
        "comparison_table": processed_content.get("comparison_table") or edu_output.get("comparison_table"),
        "learning_objectives": processed_content.get("learning_objectives") or edu_output.get("learning_objectives"),
        "keywords": processed_content.get("keywords") or edu_output.get("keywords"),
        "concepts": processed_content.get("concepts") or edu_output.get("concepts"),
        "difficulty": processed_content.get("difficulty") or edu_output.get("difficulty") or "Medium",
        "topic": processed_content.get("topic") or edu_output.get("topic"),
        "subject": resolved_subject,
        "intent": orchestrator_response.get("intent") or processed_content.get("intent"),
        "response_style": processed_content.get("response_style") or "normal",
        "unit": processed_content.get("unit"),
        "code": edu_output.get("code") or processed_content.get("code"),
        "retrieval_score": processed_content.get("retrieval_score"),
        "sources": processed_content.get("sources") or [],
        "session_id": session_id,
        "audio_path": audio_path,
        "audio_url": audio_url
    }
    
    # 5. Save Assistant's Response in Database
    create_chat_message(
        db=db,
        message=ChatMessageCreate(
            role="assistant",
            content=client_response["answer"],
            comparison_table=client_response["comparison_table"],
            code=client_response["code"],
            audio_url=audio_url
        ),
        session_id=session_id
    )
        
    return client_response


@router.post("/chats/session", response_model=ChatSessionResponse)
def create_new_session_endpoint(
    session_data: ChatSessionCreate,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Explicitly create a new chat session."""
    user_id = current_user.id if current_user else None
    return create_session(db=db, session=session_data, user_id=user_id)


@router.get("/chats", response_model=List[ChatSessionResponse])
def list_chats(
    subject: Optional[str] = None,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Retrieve chat history sessions for the user (or guest sessions)."""
    user_id = current_user.id if current_user else None
    return get_user_sessions(db, user_id=user_id, subject=subject)


@router.get("/chats/{session_id}", response_model=ChatSessionResponse)
def get_chat_session(
    session_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Retrieve all messages within a specific chat session."""
    user_id = current_user.id if current_user else None
    session = get_session_by_id(db, session_id=session_id, user_id=user_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found."
        )
    return session


@router.patch("/chats/{session_id}", response_model=ChatSessionResponse)
def update_chat_session_title(
    session_id: str,
    update_data: ChatSessionUpdate,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Renames a chat session."""
    from database.crud import rename_session
    user_id = current_user.id if current_user else None
    updated = rename_session(db=db, session_id=session_id, new_title=update_data.title, user_id=user_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Session not found.")
    return updated



@router.delete("/chats/{session_id}")
def delete_chat_session(
    session_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Deletes a chat session and all its messages."""
    user_id = current_user.id if current_user else None
    success = delete_session(db, session_id=session_id, user_id=user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found."
        )
    return {"message": "Chat session deleted successfully.", "session_id": session_id}

