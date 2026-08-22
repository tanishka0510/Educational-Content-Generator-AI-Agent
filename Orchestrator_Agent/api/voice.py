"""
Voice Q&A Router

Project: Educational Content Generator AI
Module: Orchestrator Agent (Gateway)
"""

import httpx
import os
from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional

from database.connection import get_db
from database.models import User
from api.chats import get_optional_user, process_content_endpoint, ProcessContentRequest

router = APIRouter(prefix="/voice", tags=["Voice Q&A"])

MULTIMEDIA_AGENT_URL = "http://localhost:8003"
TIMEOUT = 60.0


@router.post("/qa")
async def voice_qa(
    file: UploadFile = File(...),
    subject: str = Form(...),
    session_id: Optional[str] = Form(None),
    document_uploaded: bool = Form(False),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Handles Voice Q&A.
    1. Transcribes uploaded voice recording via Multimedia Agent STT.
    2. Routes transcription text through the Orchestrator.
    3. Synthesizes response text back to voice via Multimedia Agent TTS.
    """
    # Create temp directory for incoming voice uploads
    temp_dir = Path("uploads/audio_temp")
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Save the uploaded file temporarily
    file_ext = Path(file.filename).suffix or ".wav"
    temp_file_name = f"{uuid4().hex}{file_ext}"
    temp_file_path = temp_dir / temp_file_name
    
    try:
        with open(temp_file_path, "wb") as f:
            content = await file.read()
            f.write(content)
            
        absolute_path = str(temp_file_path.resolve())
        
        # 1. Call Speech-To-Text on Multimedia Agent
        stt_url = f"{MULTIMEDIA_AGENT_URL}/multimedia/stt"
        async with httpx.AsyncClient() as client:
            stt_response = await client.post(
                stt_url, 
                json={"audio_path": absolute_path}, 
                timeout=TIMEOUT
            )
            
            if stt_response.status_code != 200:
                raise HTTPException(
                    status_code=stt_response.status_code,
                    detail=f"STT Service failed: {stt_response.text}"
                )
                
            transcript = stt_response.json().get("transcript", "").strip()
            
        if not transcript:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not transcribe audio. Please speak clearly."
            )
            
        # 2. Run the dynamic orchestrator on the transcribed text
        # We can directly reuse the endpoint logic
        req = ProcessContentRequest(
            subject=subject,
            question=transcript,
            document_uploaded=document_uploaded,
            session_id=session_id
        )
        
        chat_response = process_content_endpoint(
            req=req,
            current_user=current_user,
            db=db
        )
        
        # If the orchestrator generated a TTS path, we extract it.
        # Otherwise, we call TTS explicitly.
        audio_url = None
        audio_path_raw = chat_response.get("audio_path")
        
        if not audio_path_raw:
            # Explicitly call TTS
            tts_url = f"{MULTIMEDIA_AGENT_URL}/multimedia/tts"
            async with httpx.AsyncClient() as client:
                tts_response = await client.post(
                    tts_url, 
                    json={"text": chat_response["answer"]}, 
                    timeout=TIMEOUT
                )
                if tts_response.status_code == 200:
                    audio_path_raw = tts_response.json().get("audio_path")
                    
        if audio_path_raw:
            # Construct accessible URL link
            # Multimedia static server maps backend/outputs -> /outputs
            filename = Path(audio_path_raw).name
            audio_url = f"{MULTIMEDIA_AGENT_URL}/outputs/audio/{filename}"
            
        # Return merged voice responses
        return {
            "transcript": transcript,
            "answer": chat_response["answer"],
            "session_id": chat_response["session_id"],
            "audio_url": audio_url,
            "comparison_table": chat_response.get("comparison_table"),
            "code": chat_response.get("code")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Voice Q&A execution error: {str(e)}"
        )
        
    finally:
        # Clean up temporary file
        if temp_file_path.exists():
            try:
                os.remove(temp_file_path)
            except Exception:
                pass
