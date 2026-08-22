"""
==========================================================
State Manager

Project:
Educational Content Generator AI

Module:
Orchestrator Agent

Purpose:
Provides helper methods for managing the shared
LangGraph AgentState throughout the orchestration
workflow.

Author:
Team Orchestrator
==========================================================
"""

from typing import Any, Dict, List

from state import AgentState

from utils.logger import get_logger

logger = get_logger(__name__)


class StateManager:
    """
    Utility class for updating the shared AgentState.
    """

    @staticmethod
    def initialize_state() -> AgentState:
        """
        Create an empty orchestrator state.
        """

        logger.info("Initializing Agent State.")

        return AgentState(
            selected_agents=[],
            processed_content={},
            retrieved_context={},
            educational_output={},
            multimedia_output={},
            response={},
            status="initialized",
            error=None,
            retry_count=0,
        )

    @staticmethod
    def update_status(
        state: AgentState,
        status: str,
    ) -> AgentState:

        state["status"] = status

        logger.info(f"Workflow status updated -> {status}")

        return state

    @staticmethod
    def update_routing(
        state: AgentState,
        intent: str,
        workflow: str,
        execution_strategy: str,
        selected_agents: List[str],
    ) -> AgentState:

        state["intent"] = intent
        state["workflow"] = workflow
        state["execution_strategy"] = execution_strategy
        state["selected_agents"] = selected_agents

        logger.info("Routing information updated.")

        return state

    @staticmethod
    def update_processed_content(
        state: AgentState,
        content: Dict[str, Any],
    ) -> AgentState:

        state["processed_content"] = content

        return state

    @staticmethod
    def update_educational_output(
        state: AgentState,
        output: Dict[str, Any],
    ) -> AgentState:

        state["educational_output"] = output

        return state

    @staticmethod
    def update_multimedia_output(
        state: AgentState,
        output: Dict[str, Any],
    ) -> AgentState:

        state["multimedia_output"] = output

        return state

    @staticmethod
    def update_response(
        state: AgentState,
        response: Dict[str, Any],
    ) -> AgentState:

        state["response"] = response

        return state

    @staticmethod
    def set_error(
        state: AgentState,
        error_message: str,
    ) -> AgentState:

        state["error"] = error_message

        logger.error(error_message)

        return state

    @staticmethod
    def increment_retry(
        state: AgentState,
    ) -> AgentState:

        state["retry_count"] += 1

        logger.warning(
            f"Retry Count : {state['retry_count']}"
        )

        return state