"""
Orchestrator Agent Interface

Project: Educational Content Generator AI
Module: Orchestrator Agent (Gateway)
"""

from typing import Dict, Any, List, Optional
from uuid import uuid4

import httpx

from graph.graph import orchestrator_graph
from routing.intent_detector import IntentDetector
from schemas.request import OrchestratorRequest, SessionInfo, UserInput, RequestMetadata
from services.state_manager import StateManager


import os

CONTENT_PROCESSING_URL = os.getenv(
    "CONTENT_PROCESSING_URL",
    "http://localhost:8001"
)
EDUCATIONAL_INTENTS = {
    "assignment",
    "compare",
    "explanation",
    "flashcards",
    "learning_objectives",
    "mathematics",
    "programming",
    "quiz",
    "resource_search",
    "study_plan",
    "summary",
}
SCOPE_REJECTION = (
    "Please ask me something related to education or learning. You can also ask "
    "me to help you prepare for an exam or study a specific topic."
)


def _detected_subject(query: str) -> Optional[str]:
    try:
        response = httpx.get(
            f"{CONTENT_PROCESSING_URL}/detect-subject",
            params={"question": query},
            timeout=5.0,
        )
        if response.status_code == 200:
            return response.json().get("subject") or None
    except httpx.RequestError:
        pass
    return None


def _is_educational_request(
    query: str,
    subject: Optional[str],
    subject_hint: Optional[str],
    document_uploaded: bool,
) -> bool:
    if document_uploaded:
        return True

    detected_subject = _detected_subject(query)
    if detected_subject:
        return True

    request = OrchestratorRequest(
        session=SessionInfo(
            request_id="scope-check",
            session_id="scope-check",
            conversation_id="scope-check",
        ),
        user_input=UserInput(query=query),
        metadata=RequestMetadata(),
    )
    intent = IntentDetector().detect(request).value

    if intent in EDUCATIONAL_INTENTS:
        return True

    # Context can validate an ambiguous follow-up, but not an unrelated new QA request.
    return (
        bool(subject_hint and subject_hint.strip())
        and _is_contextual_follow_up(query)
    )


def _is_contextual_follow_up(query: str) -> bool:
    normalized_query = query.lower().strip()
    return any(
        marker in normalized_query
        for marker in (
            "these ",
            "those ",
            "its ",
            "their ",
            "previous",
            "earlier",
            "above",
            "this concept",
            "this process",
            "how does it",
            "why is it",
            "four necessary conditions",
        )
    )


def run_orchestrator(
    query: str,
    session_id: str,
    subject: Optional[str] = None,
    document_uploaded: bool = False,
    uploaded_files: Optional[List[str]] = None,
    conversation_id: Optional[str] = None,
    document_name: Optional[str] = None,
    subject_hint: Optional[str] = None,
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
    document_name : str
        Name of the specific uploaded/attached document.

    Returns
    -------
    dict
        Aggregated response payload.
    """
    if not _is_educational_request(query, subject, subject_hint, document_uploaded):
        return {
            "status": "success",
            "request_id": f"req-{uuid4().hex[:8]}",
            "workflow": "scope_guard",
            "intent": "out_of_scope",
            "data": {
                "processed_content": {},
                "educational_output": {
                    "answer": SCOPE_REJECTION,
                },
                "multimedia_output": {},
            },
            "error": None,
        }

    # 1. Initialize State
    state = StateManager.initialize_state()
    
    # 2. Populate Request Details
    state["request_id"] = f"req-{uuid4().hex[:8]}"
    state["session_id"] = session_id
    state["conversation_id"] = conversation_id or session_id
    state["user_query"] = query
    state["subject"] = subject
    state["subject_hint"] = subject_hint
    state["document_uploaded"] = document_uploaded
    state["document_name"] = document_name
    if document_name and not uploaded_files:
        state["uploaded_files"] = [document_name]
    else:
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
