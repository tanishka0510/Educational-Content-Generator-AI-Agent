"""
File Upload Gateway Router

Project: Educational Content Generator AI
Module: Orchestrator Agent (Gateway)
"""

import httpx
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from typing import Optional

router = APIRouter(prefix="/upload", tags=["Upload"])

CONTENT_PROCESSING_URL = "http://localhost:8001"
TIMEOUT = 120.0


@router.post("/")
async def upload_file_gateway(
    file: UploadFile = File(...),
    subject: str = Form(...)
):
    """
    Gateway endpoint for document uploading.
    Forwards files as multipart/form-data to Content Processing Agent (Port 8001).
    """
    url = f"{CONTENT_PROCESSING_URL}/upload/"
    
    try:
        # Read file bytes to forward
        file_content = await file.read()
        files = {
            "file": (file.filename, file_content, file.content_type)
        }
        data = {
            "subject": subject
        }
        
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
                
            return response.json()
            
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Could not connect to Content Processing Agent upload service: {str(e)}"
        )
