"""
==========================================================
Error Schemas

Project:
Educational Content Generator AI

Module:
Orchestrator Agent

Purpose:
Defines the standardized error models used
throughout the Orchestrator Agent.

Author:
Team Orchestrator
==========================================================
"""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from utils.constants import ErrorCode


# ==========================================================
# Error Details
# ==========================================================

class ErrorDetails(BaseModel):
    """
    Additional information about the error.
    """

    details: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional debugging information."
    )


# ==========================================================
# Error Metadata
# ==========================================================

class ErrorMetadata(BaseModel):
    """
    Metadata associated with an error.
    """

    component: str = Field(
        ...,
        description="Component where the error occurred."
    )

    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Time when the error occurred."
    )


# ==========================================================
# Main Error Response
# ==========================================================

class ErrorResponse(BaseModel):
    """
    Standardized error response.
    """

    error_code: ErrorCode = Field(
        ...,
        description="Application error code."
    )

    message: str = Field(
        ...,
        description="Human-readable error message."
    )

    metadata: ErrorMetadata

    details: Optional[ErrorDetails] = Field(
        default=None,
        description="Optional debugging details."
    )