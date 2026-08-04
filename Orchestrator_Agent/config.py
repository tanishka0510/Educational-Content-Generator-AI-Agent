"""
==========================================================
Orchestrator Agent Configuration

Project:
Educational Content Generator AI

Module:
Orchestrator Agent

Purpose:
Centralized configuration management for the
Orchestrator Agent.

Author:
Team Orchestrator

==========================================================
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration.

    All values are loaded from environment variables.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ======================================================
    # Application
    # ======================================================

    APP_NAME: str = Field(
        default="Educational Content Generator AI"
    )

    APP_VERSION: str = Field(
        default="1.0.0"
    )

    DEBUG: bool = Field(
        default=True
    )

    # ======================================================
    # API
    # ======================================================

    HOST: str = Field(
        default="0.0.0.0"
    )

    PORT: int = Field(
        default=8000
    )

    # ======================================================
    # LangGraph
    # ======================================================

    GRAPH_NAME: str = Field(
        default="orchestrator_graph"
    )

    # ======================================================
    # Logging
    # ======================================================

    LOG_LEVEL: str = Field(
        default="INFO"
    )

    # ======================================================
    # Request Configuration
    # ======================================================

    REQUEST_TIMEOUT: int = Field(
        default=120
    )

    MAX_RETRIES: int = Field(
        default=3
    )

    # ======================================================
    # Session
    # ======================================================

    SESSION_TIMEOUT: int = Field(
        default=3600
    )


@lru_cache
def get_settings() -> Settings:
    """
    Returns a singleton Settings instance.
    """
    return Settings()


settings = get_settings()