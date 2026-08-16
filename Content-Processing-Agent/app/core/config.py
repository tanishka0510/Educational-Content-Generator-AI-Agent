"""
Application Configuration

This file centralizes all project configuration.

Every module should import settings from here instead of
hardcoding values.
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

import os
from dotenv import load_dotenv

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
class Settings(BaseSettings):

    # =====================================================
    # Project
    # =====================================================

    PROJECT_NAME: str = "Educational Content Processing Agent"
    PROJECT_VERSION: str = "1.0.0"
    API_VERSION: str = "v1"
    DEBUG: bool = True

    # =====================================================
    # Storage
    # =====================================================

    UPLOAD_DIR: str = "uploads"
    CHROMA_DB_PATH: str = "chroma_db"

    # =====================================================
    # Upload
    # =====================================================

    MAX_UPLOAD_SIZE_MB: int = 100

    # =====================================================
    # AI Models
    # =====================================================

    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"

    LLM_MODEL: str = "gemini-3.1-flash-lite"
    
    # =====================================================
    # External APIs
    # =====================================================

    TAVILY_MAX_RESULTS: int = 5
    TAVILY_API_KEY: str = ""
    
    # =====================================================
    # Retrieval Thresholds
    # =====================================================

    UPLOADED_DB_THRESHOLD: float = 0.90
    SUBJECT_DB_THRESHOLD: float = 0.70

    # =====================================================
    # OCR
    # =====================================================

    OCR_LANGUAGE: str = "eng"

    # =====================================================
    # Database
    # =====================================================

    POSTGRES_URL: str = ""

    # =====================================================
    # Supported Input Types
    # =====================================================

    SUPPORTED_DOCUMENT_TYPES: tuple[str, ...] = (
        ".pdf",
        ".docx",
        ".pptx",
        ".txt",
        ".md",
    )

    SUPPORTED_IMAGE_TYPES: tuple[str, ...] = (
        ".png",
        ".jpg",
        ".jpeg",
        ".bmp",
        ".tiff",
    )

    SUPPORTED_AUDIO_TYPES: tuple[str, ...] = (
        ".wav",
        ".mp3",
        ".m4a",
    )

    # =====================================================
    # External Sources
    # =====================================================

    ENABLE_WEB_URL : bool = True
    ENABLE_GOOGLE_DOCS : bool = True
    ENABLE_YOUTUBE : bool = True
    ENABLE_DATASETS : bool = True
    
    
    # =====================================================
    # Supported Content Sources
    # =====================================================

    SUPPORTED_SOURCES: tuple[str, ...] = (
        "file",
        "web_url",
        "youtube",
        "google_docs",
        "dataset",
        "image",
        "audio",
    )



    # =====================================================
    # Pydantic Configuration
    # =====================================================

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()

# ==========================================================
# Create Required Directories Automatically
# ==========================================================

Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)  #parents=True creates missing parent directories if needed

Path(settings.CHROMA_DB_PATH).mkdir(parents=True, exist_ok=True) #exist_ok=True avoids errors if the directory already exists.