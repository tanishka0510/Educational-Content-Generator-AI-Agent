"""
Main Entry Point

This file creates the FastAPI application
and registers all API routes.
"""

from fastapi import FastAPI
from app.api.upload import router as upload_router
from app.core.config import settings
from app.api.search import router as search_router
from app.schemas.query_schema import QueryRequest
from app.schemas.query_response import QueryResponse
from app.services.rag_service import ask_question
from app.schemas.processed_content_response import ProcessedContentResponse
from app.services.rag_service import process_question
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

app.include_router(upload_router)
app.include_router(search_router)

# =====================================================
# Root Endpoint
# =====================================================

@app.get("/", tags=["Home"])
async def root():
    return {
        "message": f"{settings.PROJECT_NAME} is running successfully.",
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
    
@app.post("/ask", response_model=QueryResponse)
def ask(request: QueryRequest):

    result = ask_question(request.question)

    return result

@app.post("/process-content", response_model=ProcessedContentResponse)
def process(request: QueryRequest):

    return process_question(request.question)