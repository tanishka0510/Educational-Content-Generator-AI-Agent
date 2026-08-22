"""
==========================================================
Agent Selector

Project:
Educational Content Generator AI

Module:
Orchestrator Agent

Purpose:
Selects the agent(s) responsible for executing
the planned workflow.

Version:
1.0

Author:
Team Orchestrator
==========================================================
"""

from typing import Dict, List, Tuple

from utils.constants import (
    AgentName,
    ExecutionStrategy,
    WorkflowCategory,
)
from utils.logger import get_logger

logger = get_logger(__name__)


class AgentSelector:
    """
    Selects one or more agents based on the workflow
    category and execution strategy.
    """

    def __init__(self) -> None:

        self.agent_mapping: Dict[
            Tuple[WorkflowCategory, ExecutionStrategy],
            List[AgentName]
        ] = {

            (
                WorkflowCategory.CONTENT,
                ExecutionStrategy.SINGLE,
            ): [
                AgentName.CONTENT_PROCESSING
            ],

            (
                WorkflowCategory.EDUCATIONAL,
                ExecutionStrategy.SINGLE,
            ): [
                AgentName.EDUCATIONAL
            ],

            (
                WorkflowCategory.MULTIMEDIA,
                ExecutionStrategy.SINGLE,
            ): [
                AgentName.MULTIMEDIA
            ],

            (
                WorkflowCategory.COMPOSITE,
                ExecutionStrategy.SEQUENTIAL,
            ): [
                AgentName.CONTENT_PROCESSING,
                AgentName.EDUCATIONAL,
                AgentName.MULTIMEDIA,
            ],

            (
                WorkflowCategory.CONTEXT,
                ExecutionStrategy.CONTEXT_BASED,
            ): [
                AgentName.EDUCATIONAL
            ],

            (
                WorkflowCategory.SYSTEM,
                ExecutionStrategy.SINGLE,
            ): [
                AgentName.ORCHESTRATOR
            ],
        }

    def select_agents(
        self,
        workflow: WorkflowCategory,
        strategy: ExecutionStrategy,
    ) -> List[AgentName]:
        """
        Returns the list of agents responsible for
        executing the workflow.
        """

        logger.info(
            f"Selecting agents for workflow "
            f"'{workflow.value}' "
            f"using strategy "
            f"'{strategy.value}'."
        )

        agents = self.agent_mapping.get(
            (workflow, strategy),
            []
        )

        logger.info(
            f"Selected agents: "
            f"{[agent.value for agent in agents]}"
        )

        return agents