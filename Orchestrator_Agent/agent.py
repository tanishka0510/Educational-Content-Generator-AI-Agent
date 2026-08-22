"""
Orchestrator Agent Interface

Project: Educational Content Generator AI
Module: Orchestrator Agent (Gateway)
"""

from typing import Dict, Any, List, Optional
from uuid import uuid4

from graph.graph import orchestrator_graph
from services.state_manager import StateManager


def run_orchestrator(
    query: str,
    session_id: str,
    subject: str,
    document_uploaded: bool = False,
    uploaded_files: Optional[List[str]] = None,
    conversation_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executes the Orchestrator LangGraph pipeline for a user query.

    Parameters
    ----------
    query : str
        User's natural language request.
    session_id : str
        Unique identifier for the user session.
    subject : str
        Currently selected subject (e.g. 'OS', 'OOP').
    document_uploaded : bool
        Whether a local document is uploaded for retrieval.
    uploaded_files : list
        List of files associated with the upload.
    conversation_id : str
        Unique chat history session identifier.

    Returns
    -------
    dict
        Aggregated response payload.
    """
    # 1. Initialize State
    state = StateManager.initialize_state()
    
    # 2. Populate Request Details
    state["request_id"] = f"req-{uuid4().hex[:8]}"
    state["session_id"] = session_id
    state["conversation_id"] = conversation_id or session_id
    state["user_query"] = query
    state["subject"] = subject
    state["document_uploaded"] = document_uploaded
    state["uploaded_files"] = uploaded_files or []
    
    # 3. Invoke LangGraph
    final_state = orchestrator_graph.invoke(state)
    
    # 4. Extract Aggregated Response
    response = final_state.get("response", {})
    if not response:
        response = {
            "status": "failure",
            "error": final_state.get("error") or "Unknown orchestration failure.",
            "data": {}
        }
        
    return response
