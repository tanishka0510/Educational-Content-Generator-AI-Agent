"""
Orchestrator API Gateway Entrance

Project: Educational Content Generator AI
Module: Orchestrator Agent (Gateway)
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.connection import engine, Base
from api.auth import router as auth_router
from api.chats import router as chats_router
from api.quizzes import router as quizzes_router
from api.flashcards import router as flashcards_router
from api.reports import router as reports_router
from api.voice import router as voice_router
from api.upload import router as upload_router

# ==========================================================
# Initialize Database Tables
# ==========================================================
# This creates all SQLAlchemy tables in SQLite/PostgreSQL
# automatically on startup.
Base.metadata.create_all(bind=engine)


# ==========================================================
# Create FastAPI Gateway Application
# ==========================================================
app = FastAPI(
    title="Educational AI Platform Orchestrator Gateway",
    description="Central Orchestrator, Gateway API Router and Authentication Manager.",
    version="1.0.0"
)


# ==========================================================
# CORS Configuration
# ==========================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================================
# Register API Routers
# ==========================================================
app.include_router(auth_router)
app.include_router(chats_router)
app.include_router(upload_router)
app.include_router(quizzes_router)
app.include_router(flashcards_router)
app.include_router(reports_router)
app.include_router(voice_router)


# ==========================================================
# Detailed Validation Exception Handler
# ==========================================================
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    print("\n========== REQUEST VALIDATION ERROR ==========")
    print(f"Path: {request.url.path}")
    print(f"Errors: {exc.errors()}")
    print("==============================================\n")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "message": "Request validation failed."}
    )


@app.get("/")
def gateway_root():
    return {
        "message": "Welcome to Educational AI Agent Gateway!",
        "status": "online",
        "port": 8000
    }


# ==========================================================
# Run application server
# ==========================================================
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
