"""
==========================================================
Request Manager

Project:
Educational Content Generator AI

Module:
Orchestrator Agent

Purpose:
Creates and validates OrchestratorRequest objects.

Version:
1.0

Author:
Team Orchestrator
==========================================================
"""

import uuid
from typing import List, Optional

from schemas.request import (
    SessionInfo,
    UserInput,
    RequestMetadata,
    OrchestratorRequest,
)

from utils.logger import get_logger

logger = get_logger(__name__)


class RequestManager:
    """
    Responsible for creating validated
    OrchestratorRequest objects.
    """

    def __init__(self):

        logger.info("Request Manager initialized.")

    def create_request(
        self,
        query: str,
        session_id: str,
        conversation_id: str,
        uploaded_files: Optional[List[str]] = None,
        source: str = "web",
        language: str = "en",
    ) -> OrchestratorRequest:
        """
        Creates a complete OrchestratorRequest.

        Parameters
        ----------
        query : str

        session_id : str

        conversation_id : str

        uploaded_files : List[str]

        source : str

        language : str

        Returns
        -------
        OrchestratorRequest
        """

        logger.info("Creating orchestrator request.")

        if uploaded_files is None:
            uploaded_files = []

        session = SessionInfo(

            request_id=str(uuid.uuid4()),

            session_id=session_id,

            conversation_id=conversation_id,
        )

        user_input = UserInput(

            query=query,

            uploaded_files=uploaded_files,
        )

        metadata = RequestMetadata(

            source=source,

            language=language,
        )

        request = OrchestratorRequest(

            session=session,

            user_input=user_input,

            metadata=metadata,
        )

        logger.info(
            f"Request created successfully. "
            f"Request ID: {session.request_id}"
        )

        return request

    def validate_request(
        self,
        request: OrchestratorRequest,
    ) -> bool:
        """
        Performs basic validation.

        Returns
        -------
        bool
        """

        logger.info("Validating request.")

        if not request.user_input.query.strip():

            logger.error("Query cannot be empty.")

            return False

        logger.info("Request validation successful.")

        return True