"""
==========================================================
Response Schemas

Project:
Educational Content Generator AI

Module:
Orchestrator Agent

Purpose:
Defines the standardized response models returned
by the Orchestrator Agent.

Author:
Team Orchestrator
==========================================================
"""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from utils.constants import ResponseStatus


# ==========================================================
# Response Metadata
# ==========================================================

class ResponseMetadata(BaseModel):
    """
    Metadata associated with the response.
    """

    request_id: str = Field(
        ...,
        description="Unique request identifier."
    )

    execution_time: float = Field(
        ...,
        description="Execution time in seconds."
    )

    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Response generation timestamp."
    )


# ==========================================================
# Response Data
# ==========================================================

class ResponseData(BaseModel):
    """
    Payload returned by the orchestrator.
    """

    content: Dict[str, Any] = Field(
        default_factory=dict,
        description="Generated response content."
    )


# ==========================================================
# Main Response Schema
# ==========================================================

class OrchestratorResponse(BaseModel):
    """
    Standard response returned by the Orchestrator Agent.
    """

    status: ResponseStatus = Field(
        ...,
        description="Execution status."
    )

    message: str = Field(
        ...,
        description="Human-readable response message."
    )

    data: ResponseData

    metadata: ResponseMetadata

    error: Optional[str] = Field(
        default=None,
        description="Error message if request fails."
    )