"""
==========================================================
Request Schemas

Project:
Educational Content Generator AI

Module:
Orchestrator Agent

Purpose:
Defines the request models received by the
Orchestrator Agent.

Author:
Team Orchestrator
==========================================================
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# ==========================================================
# Session Information
# ==========================================================

class SessionInfo(BaseModel):
    """
    Session-related information.
    """

    request_id: str = Field(
        ...,
        description="Unique request identifier."
    )

    session_id: str = Field(
        ...,
        description="Unique user session identifier."
    )

    conversation_id: str = Field(
        ...,
        description="Conversation identifier."
    )


# ==========================================================
# User Input
# ==========================================================

class UserInput(BaseModel):
    """
    User input data.
    """

    query: str = Field(
        ...,
        description="User query."
    )

    uploaded_files: List[str] = Field(
        default_factory=list,
        description="List of uploaded file paths."
    )


# ==========================================================
# Request Metadata
# ==========================================================

class RequestMetadata(BaseModel):
    """
    Metadata associated with the request.
    """

    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Request timestamp."
    )

    source: str = Field(
        default="web",
        description="Request source."
    )

    language: str = Field(
        default="en",
        description="Request language."
    )


# ==========================================================
# Main Request Schema
# ==========================================================

class OrchestratorRequest(BaseModel):
    """
    Complete request model for the Orchestrator Agent.
    """

    session: SessionInfo

    user_input: UserInput

    metadata: RequestMetadata