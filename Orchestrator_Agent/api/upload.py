"""
File Upload Gateway Router

Project: Educational Content Generator AI
Module: Orchestrator Agent (Gateway)
"""

from pathlib import Path
from typing import List, Optional
import httpx
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Depends
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import User
from database.crud import (
    create_uploaded_document,
    get_user_documents,
    get_document_by_id,
    delete_uploaded_document
)
from database.schemas import UploadedDocumentCreate, UploadedDocumentResponse
from utils.security import get_optional_user

router = APIRouter(prefix="/upload", tags=["Upload"])
import os

CONTENT_PROCESSING_URL = os.getenv(
    "CONTENT_PROCESSING_URL",
    "http://localhost:8001"
)

TIMEOUT = 120.0


@router.post("/")
async def upload_file_gateway(
    file: UploadFile = File(...),
    subject: Optional[str] = Form(default=None),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Gateway endpoint for document uploading.
    Forwards files as multipart/form-data to Content Processing Agent (Port 8001).
    Persists document metadata in the database for tracking user study materials.
    Subject is optional (defaults to GENERAL) to support Chat document uploads without subject selection.
    """
    url = f"{CONTENT_PROCESSING_URL}/upload/"
    
    try:
        # Read file bytes to forward
        file_content = await file.read()
        file_size = len(file_content)
        file_ext = Path(file.filename).suffix.lstrip(".").lower() or "bin"

        files = {
            "file": (file.filename, file_content, file.content_type)
        }
        data = {}
        if subject and subject.strip():
            data["subject"] = subject.strip()
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url, 
                files=files, 
                data=data, 
                timeout=TIMEOUT
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Content Processing Agent upload failed: {response.text}"
                )
                
            cpa_result = response.json()

            # Persist document metadata in the database
            user_id = current_user.id if current_user else None
            chunks_count = cpa_result.get("chunks_created", 0)

            # Store the explicitly provided subject, or the auto-detected subject from CPA, or default to GENERAL
            final_subject = (
                (subject.strip() if subject and subject.strip() else None)
                or cpa_result.get("subject")
                or "GENERAL"
            )

            doc_create = UploadedDocumentCreate(
                filename=file.filename,
                file_type=file_ext,
                file_size=file_size,
                subject=final_subject,
                topic=cpa_result.get("topic"),
                chunks_count=chunks_count,
                status="Indexed"
            )
            saved_doc = create_uploaded_document(db=db, doc=doc_create, user_id=user_id)

            return {
                **cpa_result,
                "document_id": saved_doc.id,
                "file_size": file_size,
                "created_at": saved_doc.created_at.isoformat()
            }
            
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Could not connect to Content Processing Agent upload service: {str(e)}"
        )


@router.get("/documents", response_model=List[UploadedDocumentResponse])
def list_uploaded_documents(
    subject: Optional[str] = None,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves all uploaded documents for the user, optionally filtered by subject.
    """
    user_id = current_user.id if current_user else None
    return get_user_documents(db=db, user_id=user_id, subject=subject)


@router.delete("/documents/{doc_id}")
def delete_document_endpoint(
    doc_id: int,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Deletes an uploaded document record from the database.
    """
    user_id = current_user.id if current_user else None
    success = delete_uploaded_document(db=db, doc_id=doc_id, user_id=user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found or unauthorized."
        )
    return {"message": "Document deleted successfully.", "document_id": doc_id}

