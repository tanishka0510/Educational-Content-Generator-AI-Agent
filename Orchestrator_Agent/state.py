"""
==========================================================
Orchestrator Agent State

Project:
Educational Content Generator AI

Module:
Orchestrator Agent

Purpose:
Defines the shared workflow state used by the
Orchestrator Agent throughout the execution lifecycle.

Author:
Team Orchestrator
==========================================================
"""

from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from typing_extensions import TypedDict


class AgentState(TypedDict, total=False):
    """
    Shared state exchanged between all nodes
    in the orchestration workflow.
    """

    # ======================================================
    # Request Information
    # ======================================================

    request_id: str
    session_id: str
    conversation_id: str
    timestamp: str

    # ======================================================
    # User Input
    # ======================================================

    user_query: str
    uploaded_files: List[str]

    # ======================================================
    # Routing
    # ======================================================

    intent: str
    workflow: str
    execution_strategy: str
    selected_agents: List[str]

    # ======================================================
    # Content Processing
    # ======================================================

    processed_content: Dict[str, Any]
    retrieved_context: Dict[str, Any]

    # ======================================================
    # Educational Agent
    # ======================================================

    educational_output: Dict[str, Any]

    # ======================================================
    # Multimedia Agent
    # ======================================================

    multimedia_output: Dict[str, Any]

    # ======================================================
    # Final Response
    # ======================================================

    response: Dict[str, Any]
    status: str

    # ======================================================
    # Error Handling
    # ======================================================

    error: Optional[str]
    retry_count: int