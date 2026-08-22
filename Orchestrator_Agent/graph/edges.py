"""
LangGraph Edges & Routing Logic

Project: Educational Content Generator AI
Module: Orchestrator Agent (Gateway)
"""

from typing import List, Literal
from state import AgentState
from utils.logger import get_logger

logger = get_logger(__name__)


def route_after_router(state: AgentState) -> Literal["content_processing", "educational", "multimedia", "aggregate"]:
    """
    Decides where to go immediately after routing request node.
    """
    selected_agents: List[str] = state.get("selected_agents", [])
    
    logger.info(f"Edge: routing after router. Selected agents: {selected_agents}")
    
    if "content_processing" in selected_agents:
        return "content_processing"
    elif "educational" in selected_agents:
        return "educational"
    elif "multimedia" in selected_agents:
        return "multimedia"
    else:
        return "aggregate"


def route_after_content(state: AgentState) -> Literal["educational", "multimedia", "aggregate"]:
    """
    Decides where to go after Content Processing node.
    """
    selected_agents: List[str] = state.get("selected_agents", [])
    
    logger.info(f"Edge: routing after content processing. Selected agents: {selected_agents}")
    
    if "educational" in selected_agents:
        return "educational"
    elif "multimedia" in selected_agents:
        return "multimedia"
    else:
        return "aggregate"


def route_after_educational(state: AgentState) -> Literal["multimedia", "aggregate"]:
    """
    Decides where to go after Educational Agent node.
    """
    selected_agents: List[str] = state.get("selected_agents", [])
    
    logger.info(f"Edge: routing after educational. Selected agents: {selected_agents}")
    
    # We also check if the user query was a voice query, in which case we always want TTS.
    # But for standard checks, we look at the selected agents list.
    if "multimedia" in selected_agents:
        return "multimedia"
    else:
        return "aggregate"
