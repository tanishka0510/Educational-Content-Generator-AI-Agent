"""
==========================================================
Workflow Manager

Project:
Educational Content Generator AI

Module:
Orchestrator Agent

Purpose:
Maps a detected user intent to the corresponding
workflow category.

Version:
1.0

Author:
Team Orchestrator
==========================================================
"""

from typing import Dict

from utils.constants import Intent, WorkflowCategory
from utils.logger import get_logger


logger = get_logger(__name__)


class WorkflowManager:
    """
    Maps a detected intent to the appropriate workflow.
    """

    def __init__(self) -> None:

        self.workflow_mapping: Dict[Intent, WorkflowCategory] = {

            # ==================================================
            # Content Processing Workflow
            # ==================================================

            Intent.UPLOAD: WorkflowCategory.CONTENT,

            # ==================================================
            # Educational Workflow
            # ==================================================

            Intent.QA: WorkflowCategory.EDUCATIONAL,

            Intent.SUMMARY: WorkflowCategory.EDUCATIONAL,

            Intent.QUIZ: WorkflowCategory.EDUCATIONAL,

            Intent.FLASHCARDS: WorkflowCategory.EDUCATIONAL,

            Intent.LEARNING_OBJECTIVES: WorkflowCategory.EDUCATIONAL,

            Intent.RESOURCE_SEARCH: WorkflowCategory.EDUCATIONAL,

            Intent.COMPARE: WorkflowCategory.EDUCATIONAL,

            Intent.EXPLANATION: WorkflowCategory.EDUCATIONAL,

            Intent.PROGRAMMING: WorkflowCategory.EDUCATIONAL,

            Intent.MATHEMATICS: WorkflowCategory.EDUCATIONAL,

            Intent.ASSIGNMENT: WorkflowCategory.EDUCATIONAL,

            Intent.STUDY_PLAN: WorkflowCategory.EDUCATIONAL,

            Intent.GENERAL_KNOWLEDGE: WorkflowCategory.EDUCATIONAL,

            # ==================================================
            # Multimedia Workflow
            # ==================================================

            Intent.MULTIMEDIA: WorkflowCategory.MULTIMEDIA,

            # ==================================================
            # Composite Workflow
            # ==================================================

            Intent.MIXED_QUERY: WorkflowCategory.COMPOSITE,

            # ==================================================
            # Context Workflow
            # ==================================================

            Intent.FOLLOW_UP: WorkflowCategory.CONTEXT,

            # ==================================================
            # System Workflow
            # ==================================================

            Intent.ADMIN: WorkflowCategory.SYSTEM,
        }

    # ======================================================
    # Public Method
    # ======================================================

    def get_workflow(self, intent: Intent) -> WorkflowCategory:
        """
        Returns the workflow category for the detected intent.

        Parameters
        ----------
        intent : Intent
            Detected user intent.

        Returns
        -------
        WorkflowCategory
            Corresponding workflow category.
        """

        logger.info(f"Mapping intent '{intent.value}' to workflow.")

        workflow = self.workflow_mapping.get(
            intent,
            WorkflowCategory.EDUCATIONAL
        )

        logger.info(f"Selected workflow: '{workflow.value}'")

        return workflow