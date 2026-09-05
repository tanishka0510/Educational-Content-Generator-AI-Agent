"""
Main Entry Point

This file creates the FastAPI application
and registers all API routes.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.api.quiz import router as quiz_router
from app.api.upload import router as upload_router
from app.api.retrieve import router as retrieve_router
from app.api.search import router as search_router

from app.core.config import settings

from app.schemas.query_schema import QueryRequest
from app.schemas.query_response import QueryResponse
from app.schemas.processed_content_response import (
    ProcessedContentResponse
)

from app.services.rag_service import (
    ask_question,
    process_question,
)

from app.services.subject_validator import (
    validate_question_subject,
    detect_question_subject,
    get_subject_validation_message,
)

# =====================================================
# Create FastAPI Application
# =====================================================

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description=(
        "Content Processing Agent for the Educational "
        "Content Generator Multi-Agent System."
    ),
)


# =====================================================
# CORS Configuration
# =====================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# =====================================================
# Register Routers
# =====================================================

app.include_router(upload_router)
app.include_router(search_router)
app.include_router(retrieve_router)
app.include_router(quiz_router)

# =====================================================
# Root Endpoint
# =====================================================

@app.get("/", tags=["Home"])
async def root():

    return {
        "message": (
            f"{settings.PROJECT_NAME} "
            "is running successfully."
        ),

        "version": settings.PROJECT_VERSION,

        "api_version": settings.API_VERSION,
    }


# =====================================================
# Health Check
# =====================================================

@app.get("/health", tags=["Health"])
async def health_check():

    return {
        "status": "healthy",

        "service": settings.PROJECT_NAME,

        "debug": settings.DEBUG,
    }


@app.get("/detect-subject", tags=["Subject Detection"])
def detect_subject(question: str):
    subject, score = detect_question_subject(question)
    return {
        "subject": subject if score > 0 else None,
        "score": score,
    }


# =====================================================
# Ask Question
# =====================================================

@app.post(
    "/ask",

    response_model=QueryResponse,

    response_model_exclude_none=True,
)
def ask(request: QueryRequest):

    try:

        return ask_question(
            request.subject,
            request.question,
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


# =====================================================
# Process Educational Content
# =====================================================

@app.post(
    "/process-content",
    response_model=ProcessedContentResponse,
    response_model_exclude_none=True,
)
def process(request: QueryRequest):

    try:
        selected_subject = request.subject

        if not selected_subject:
            detected_subject, detected_score = detect_question_subject(request.question)
            if detected_score > 0:
                selected_subject = detected_subject
            elif request.subject_hint and any(
                marker in request.question.lower()
                for marker in ("its ", "their ", "these ", "those ", "four necessary", "why is it", "how does it")
            ):
                selected_subject = request.subject_hint

        # =====================================================
        # STEP 1: Validate Question Against Selected Subject
        # =====================================================

        if selected_subject and not request.document_uploaded:
            is_valid, detected_subject = validate_question_subject(
                selected_subject=selected_subject,
                question=request.question,
            )
        else:
            is_valid, detected_subject = True, "Unknown"

        print("\n========== SUBJECT VALIDATION ==========")
        print("Selected Subject :", selected_subject)
        print("Question         :", request.question)
        print("Detected Subject :", detected_subject)
        print("Valid             :", is_valid)
        print("=======================================\n")

        # =====================================================
        # STEP 2: Reject Question If It Belongs To Another Subject
        # =====================================================

        if not is_valid:

            return {
                "summary": get_subject_validation_message(
                    selected_subject or "the requested topic"
                ),
                "learning_objectives": [],
                "keywords": [],
                "concepts": [],
                "difficulty": "Unknown",
                "topic": None,
                "intent": "invalid_subject",
                "response_style": "normal",
                "unit": None,
                "sources": [],
                "retrieval_score": None,
            }

        # =====================================================
        # STEP 3: Question Is Valid
        # Continue With Normal RAG Processing
        # =====================================================

        result = process_question(
            subject=selected_subject,
            question=request.question,
            document_uploaded=request.document_uploaded,
            filename=request.filename or request.document_name,
        )
        result["subject"] = selected_subject
        return result

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
