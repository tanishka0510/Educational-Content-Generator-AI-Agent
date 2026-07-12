from fastapi import APIRouter
import os

from models.chat_model import ChatRequest
from services.pdf_reader import extract_text
from services.text_cleaner import clean_text
from services.chat_service import chat_with_document

router = APIRouter()

UPLOAD_FOLDER = "uploads"


@router.post("/chat")
async def chat(request: ChatRequest):

    file_path = os.path.join(UPLOAD_FOLDER, request.filename)

    if not os.path.exists(file_path):
        return {
            "error": "File not found."
        }

    text = extract_text(file_path)

    text = clean_text(text)

    answer = chat_with_document(
        text,
        request.question
    )

    return {
        "question": request.question,
        "answer": answer
    }