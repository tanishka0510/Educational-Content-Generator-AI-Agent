print("upload.py loaded")

from fastapi import APIRouter, UploadFile, File
import shutil
import os

from services.pdf_reader import extract_text
from services.text_cleaner import clean_text
from services.quiz_generator import generate_quiz

router = APIRouter()

UPLOAD_FOLDER = "uploads"

# Create uploads folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    # Save uploaded PDF
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract text from PDF
    text = extract_text(file_path)

    # Clean the extracted text
    cleaned_text = clean_text(text)

    # Generate quiz using Gemini
    quiz = generate_quiz(cleaned_text)

    return {
        "message": "Quiz generated successfully!",
        "filename": file.filename,
        "quiz": quiz
    }