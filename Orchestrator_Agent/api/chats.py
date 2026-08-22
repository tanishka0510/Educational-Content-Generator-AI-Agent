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
from database.schemas import ChatSessionResponse, ChatMessageCreate
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
    subject: str
    question: str
    document_uploaded: bool
    session_id: Optional[str] = None


@router.post("/process-content")
def process_content_endpoint(
    req: ProcessContentRequest,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Main entry point for routing user queries. Runs the multi-agent Orchestrator.
    Saves conversation history if the user is authenticated.
    """
    session_id = req.session_id
    
    # 1. Resolve Session details if user is authenticated
    if current_user:
        if not session_id:
            # Generate a new session
            session_id = f"sess-{uuid4().hex[:12]}"
            title = req.question[:45] + "..." if len(req.question) > 45 else req.question
            from database.schemas import ChatSessionCreate
            create_session(
                db=db,
                session=ChatSessionCreate(id=session_id, subject=req.subject, title=title),
                user_id=current_user.id
            )
        else:
            # Verify session belongs to user
            session = get_session_by_id(db, session_id=session_id, user_id=current_user.id)
            if not session:
                # If session doesn't exist for user, create it
                title = req.question[:45] + "..." if len(req.question) > 45 else req.question
                from database.schemas import ChatSessionCreate
                create_session(
                    db=db,
                    session=ChatSessionCreate(id=session_id, subject=req.subject, title=title),
                    user_id=current_user.id
                )
                
        # Save User's Question
        create_chat_message(
            db=db,
            message=ChatMessageCreate(role="user", content=req.question),
            session_id=session_id
        )

    # 2. Run Orchestrator Pipeline
    # The Orchestrator calls Content Processing, Educational, and Multimedia Agents.
    orchestrator_response = run_orchestrator(
        query=req.question,
        session_id=session_id or "temp-session",
        subject=req.subject,
        document_uploaded=req.document_uploaded
    )
    
    # 3. Extract outputs
    data = orchestrator_response.get("data", {})
    edu_output = data.get("educational_output", {}) or {}
    processed_content = data.get("processed_content", {}) or {}
    multimedia_output = data.get("multimedia_output", {}) or {}
    
    # 4. Construct flat client response for backwards compatibility
    client_response = {
        "answer": edu_output.get("answer") or edu_output.get("summary") or processed_content.get("summary") or "Unable to generate an answer.",
        "summary": processed_content.get("summary"),
        "comparison_table": processed_content.get("comparison_table") or edu_output.get("comparison_table"),
        "learning_objectives": processed_content.get("learning_objectives") or edu_output.get("learning_objectives"),
        "keywords": processed_content.get("keywords") or edu_output.get("keywords"),
        "concepts": processed_content.get("concepts") or edu_output.get("concepts"),
        "difficulty": processed_content.get("difficulty") or edu_output.get("difficulty") or "Medium",
        "topic": processed_content.get("topic") or edu_output.get("topic"),
        "intent": orchestrator_response.get("intent") or processed_content.get("intent"),
        "response_style": processed_content.get("response_style") or "normal",
        "unit": processed_content.get("unit"),
        "code": edu_output.get("code") or processed_content.get("code"),
        "retrieval_score": processed_content.get("retrieval_score"),
        "sources": processed_content.get("sources") or [],
        "session_id": session_id,
        "audio_path": multimedia_output.get("audio_path")
    }
    
    # 5. Save Assistant's Response if user is authenticated
    if current_user and session_id:
        create_chat_message(
            db=db,
            message=ChatMessageCreate(
                role="assistant",
                content=client_response["answer"],
                comparison_table=client_response["comparison_table"],
                code=client_response["code"]
            ),
            session_id=session_id
        )
        
    return client_response


@router.get("/chats", response_model=List[ChatSessionResponse])
def list_chats(
    subject: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve chat history sessions for the authenticated user."""
    return get_user_sessions(db, user_id=current_user.id, subject=subject)


@router.get("/chats/{session_id}", response_model=ChatSessionResponse)
def get_chat_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve all messages within a specific chat session."""
    session = get_session_by_id(db, session_id=session_id, user_id=current_user.id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found."
        )
    return session


@router.delete("/chats/{session_id}")
def delete_chat_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deletes a chat session and all its messages."""
    success = delete_session(db, session_id=session_id, user_id=current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found."
        )
    return {"message": "Chat session deleted successfully."}
