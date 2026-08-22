"""
==========================================================
Error Handler

Project:
Educational Content Generator AI

Module:
Orchestrator Agent

Purpose:
Provides centralized exception handling for the
Orchestrator Agent.

Author:
Team Orchestrator
==========================================================
"""

from typing import Any, Dict

from state import AgentState

from utils.constants import (
    ErrorCode,
    ResponseStatus,
)

from utils.logger import get_logger

logger = get_logger(__name__)


class ErrorHandler:
    """
    Handles all orchestrator errors.
    """

    @staticmethod
    def handle_exception(
        state: AgentState,
        exception: Exception,
        error_code: ErrorCode = ErrorCode.INTERNAL_ERROR,
    ) -> Dict[str, Any]:
        """
        Handle an exception and return a standardized
        error response.
        """

        error_message = str(exception)

        logger.exception(
            f"{error_code.value}: {error_message}"
        )

        state["status"] = "failed"

        state["error"] = error_message

        response = {

            "status": ResponseStatus.FAILURE.value,

            "request_id": state.get("request_id"),

            "error": {

                "code": error_code.value,

                "message": error_message,

            }

        }

        return response

    @staticmethod
    def build_error_response(
        request_id: str,
        error_code: ErrorCode,
        message: str,
    ) -> Dict[str, Any]:
        """
        Build an error response without requiring
        AgentState.
        """

        logger.error(message)

        return {

            "status": ResponseStatus.FAILURE.value,

            "request_id": request_id,

            "error": {

                "code": error_code.value,

                "message": message,

            }

        }