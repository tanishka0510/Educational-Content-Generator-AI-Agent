"""
==========================================================
Execution Planner

Project:
Educational Content Generator AI

Module:
Orchestrator Agent

Purpose:
Determines how a selected workflow should be executed.

Version:
1.0

Author:
Team Orchestrator
==========================================================
"""

from typing import Dict

from utils.constants import (
    WorkflowCategory,
    ExecutionStrategy,
)
from utils.logger import get_logger

logger = get_logger(__name__)


class ExecutionPlanner:
    """
    Determines the execution strategy for a workflow.
    """

    def __init__(self) -> None:

        self.execution_mapping: Dict[
            WorkflowCategory,
            ExecutionStrategy,
        ] = {

            WorkflowCategory.CONTENT:
                ExecutionStrategy.SINGLE,

            WorkflowCategory.EDUCATIONAL:
                ExecutionStrategy.SINGLE,

            WorkflowCategory.MULTIMEDIA:
                ExecutionStrategy.SINGLE,

            WorkflowCategory.COMPOSITE:
                ExecutionStrategy.SEQUENTIAL,

            WorkflowCategory.CONTEXT:
                ExecutionStrategy.CONTEXT_BASED,

            WorkflowCategory.SYSTEM:
                ExecutionStrategy.SINGLE,
        }

    def get_execution_strategy(
        self,
        workflow: WorkflowCategory,
    ) -> ExecutionStrategy:
        """
        Returns the execution strategy for the workflow.

        Parameters
        ----------
        workflow : WorkflowCategory

        Returns
        -------
        ExecutionStrategy
        """

        logger.info(
            f"Planning execution for workflow '{workflow.value}'."
        )

        strategy = self.execution_mapping.get(
            workflow,
            ExecutionStrategy.SINGLE,
        )

        logger.info(
            f"Selected execution strategy: '{strategy.value}'."
        )

        return strategy