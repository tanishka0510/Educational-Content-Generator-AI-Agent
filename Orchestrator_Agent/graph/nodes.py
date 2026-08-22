"""
LangGraph Nodes

Project: Educational Content Generator AI
Module: Orchestrator Agent (Gateway)
"""

import httpx
from typing import Dict, Any

from state import AgentState
from routing.router import Router
from services.response_aggregator import ResponseAggregator
from utils.logger import get_logger
from schemas.request import OrchestratorRequest, SessionInfo, UserInput, RequestMetadata

logger = get_logger(__name__)

# Agent ports mapping
CONTENT_PROCESSING_URL = "http://localhost:8001"
EDUCATIONAL_AGENT_URL = "http://localhost:8002"
MULTIMEDIA_AGENT_URL = "http://localhost:8003"
TIMEOUT = 60.0


def route_request_node(state: AgentState) -> Dict[str, Any]:
    """
    Node 1: Analyze user request, detect intent, and choose target agents.
    """
    logger.info("Node: Routing request")
    
    # Construct schema request for Router
    router_req = OrchestratorRequest(
        session=SessionInfo(
            request_id=state.get("request_id", "default"),
            session_id=state.get("session_id", "default"),
            conversation_id=state.get("conversation_id", "default")
        ),
        user_input=UserInput(
            query=state.get("user_query", ""),
            uploaded_files=state.get("uploaded_files", [])
        ),
        metadata=RequestMetadata()
    )
    
    router = Router()
    execution_plan = router.route(router_req)
    
    intent = execution_plan.routing.workflow_info.intent.value
    workflow = execution_plan.routing.workflow_info.workflow.value
    strategy = execution_plan.execution_strategy.value
    agents = [agent.value for agent in execution_plan.routing.selected_agents]
    
    logger.info(f"Route selected: Intent={intent}, Workflow={workflow}, Strategy={strategy}, Agents={agents}")
    
    return {
        "intent": intent,
        "workflow": workflow,
        "execution_strategy": strategy,
        "selected_agents": agents,
        "status": "routed"
    }


def content_processing_node(state: AgentState) -> Dict[str, Any]:
    """
    Node 2: Call the Content Processing Agent to retrieve and prepare content context.
    """
    logger.info("Node: Content Processing")
    
    subject = state.get("subject", "OS")
    query = state.get("user_query", "")
    document_uploaded = state.get("document_uploaded", False)
    
    url = f"{CONTENT_PROCESSING_URL}/process-content"
    payload = {
        "subject": subject,
        "question": query,
        "document_uploaded": document_uploaded
    }
    
    try:
        with httpx.Client() as client:
            response = client.post(url, json=payload, timeout=TIMEOUT)
            response.raise_for_status()
            processed_data = response.json()
            logger.info("Content Processing Agent call successful.")
            return {
                "processed_content": processed_data,
                "status": "content_processed"
            }
    except Exception as e:
        logger.error(f"Error in Content Processing node: {str(e)}")
        return {
            "error": f"Content Processing Agent error: {str(e)}",
            "status": "failed"
        }


def educational_agent_node(state: AgentState) -> Dict[str, Any]:
    """
    Node 3: Call the Educational Agent to construct a clear educational response.
    """
    logger.info("Node: Educational Agent")
    
    subject = state.get("subject", "OS")
    query = state.get("user_query", "")
    document_uploaded = state.get("document_uploaded", False)
    processed_content = state.get("processed_content", {})
    
    # If the Content Processing Node failed or had errors, we still want to call Educational Agent with empty context.
    url = f"{EDUCATIONAL_AGENT_URL}/chat"
    payload = {
        "subject": subject,
        "question": query,
        "document_uploaded": document_uploaded
    }
    
    # In case we bypassed Content Processing (e.g. for general queries) or it was successful,
    # we call Educational Agent backend. Wait, Educational Agent's /chat endpoint takes ChatRequest:
    # { "subject": str, "question": str, "document_uploaded": bool }
    # Let's verify: Yes, in Educational Agent backend/api/chat.py, /chat endpoint takes ChatRequest,
    # which internally calls process_content on Port 8001, then calls process_chat_query!
    # Wait! If the Educational Agent `/chat` endpoint internally calls Port 8001 (Content Processing Agent),
    # then our node calling `/chat` will automatically do the Content Processing retrieval too!
    # But wait, to keep it modular and true to the orchestrator architecture:
    # If Content Processing is a separate step, can we send the processed content to the Educational Agent?
    # Wait, does the Educational Agent have an endpoint that accepts the query AND the processed content directly?
    # In `Educational-Content-Generator-Agent/backend/services/chat_service.py` we have `process_chat_query(subject, question, content_response, document_uploaded)`.
    # Let's expose an endpoint in Educational Agent backend `/chat/generate` or `/chat` that accepts both query AND processed content,
    # or let the Educational Agent call Content Processing (since it is already integrated and working in the starter code).
    # Actually, in the starter code:
    # Educational Agent `/chat` receives `ChatRequest` (subject, question, document_uploaded) and calls Content Processing.
    # If we call Educational Agent `/chat` from the Orchestrator, it will work perfectly out of the box because the internal client is already set up to call Content Processing!
    # But wait, what if we want the Orchestrator to directly control this?
    # We can keep it simple: the Orchestrator's Educational Node calls Educational Agent's `/chat` endpoint.
    # Let's check: does it work? Yes!
    
    try:
        with httpx.Client() as client:
            response = client.post(url, json=payload, timeout=TIMEOUT)
            response.raise_for_status()
            edu_data = response.json()
            logger.info("Educational Agent call successful.")
            return {
                "educational_output": edu_data,
                "status": "educational_processed"
            }
    except Exception as e:
        logger.error(f"Error in Educational Agent node: {str(e)}")
        return {
            "error": f"Educational Agent error: {str(e)}",
            "status": "failed"
        }


def multimedia_agent_node(state: AgentState) -> Dict[str, Any]:
    """
    Node 4: Call the Multimedia Agent to generate speech/audio responses if needed.
    """
    logger.info("Node: Multimedia Agent")
    
    # We take the text response generated by the Educational Agent and convert it to speech.
    edu_output = state.get("educational_output", {})
    text_to_convert = edu_output.get("answer") or edu_output.get("summary")
    
    if not text_to_convert:
        logger.warning("No text found to convert to speech.")
        return {
            "status": "multimedia_skipped"
        }
        
    url = f"{MULTIMEDIA_AGENT_URL}/multimedia/tts"
    payload = {
        "text": text_to_convert
    }
    
    try:
        with httpx.Client() as client:
            response = client.post(url, json=payload, timeout=TIMEOUT)
            response.raise_for_status()
            multimedia_data = response.json()
            logger.info("Multimedia Agent TTS call successful.")
            return {
                "multimedia_output": multimedia_data,
                "status": "multimedia_processed"
            }
    except Exception as e:
        logger.error(f"Error in Multimedia Agent node: {str(e)}")
        # We don't want to fail the whole response if TTS fails, so we just log the error and proceed.
        return {
            "multimedia_output": {"error": f"TTS generation failed: {str(e)}"},
            "status": "multimedia_failed"
        }


def aggregate_results_node(state: AgentState) -> Dict[str, Any]:
    """
    Node 5: Aggregate the final response.
    """
    logger.info("Node: Aggregating results")
    final_response = ResponseAggregator.aggregate(state)
    return {
        "response": final_response,
        "status": "completed"
    }
