"""
Main Entry Point

This file creates the FastAPI application
and registers all API routes.
"""

from fastapi import FastAPI, HTTPException

from app.api.upload import router as upload_router
from app.api.retrieve import router as retrieve_router
from app.api.search import router as search_router

from app.core.config import settings

from app.schemas.query_schema import QueryRequest
from app.schemas.query_response import QueryResponse
from app.schemas.processed_content_response import ProcessedContentResponse

from app.services.rag_service import (
    ask_question,
    process_question,
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
# Register Routers
# =====================================================

app.include_router(upload_router)
app.include_router(search_router)
app.include_router(retrieve_router)


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

        return process_question(
            subject=request.subject,
            question=request.question,
            document_uploaded=request.document_uploaded,
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )