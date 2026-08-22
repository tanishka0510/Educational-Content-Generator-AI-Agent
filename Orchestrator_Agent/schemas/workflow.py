"""
==========================================================
Workflow Schemas

Project:
Educational Content Generator AI

Module:
Orchestrator Agent

Purpose:
Defines the workflow-related schemas used during
routing and orchestration.

Author:
Team Orchestrator
==========================================================
"""

from typing import List

from pydantic import BaseModel, Field

from utils.constants import (
    AgentName,
    ExecutionStrategy,
    Intent,
    WorkflowCategory,
)


# ==========================================================
# Workflow Information
# ==========================================================

class WorkflowInfo(BaseModel):
    """
    Stores the detected intent and selected workflow.
    """

    intent: Intent = Field(
        ...,
        description="Detected user intent."
    )

    workflow: WorkflowCategory = Field(
        ...,
        description="Selected workflow category."
    )


# ==========================================================
# Routing Decision
# ==========================================================

class RoutingDecision(BaseModel):
    """
    Represents the routing decision made by
    the Workflow Manager.
    """

    workflow_info: WorkflowInfo

    selected_agents: List[AgentName] = Field(
        default_factory=list,
        description="Agents selected for execution."
    )


# ==========================================================
# Execution Plan
# ==========================================================

class ExecutionPlan(BaseModel):
    """
    Represents the execution plan generated
    by the Execution Planner.
    """

    routing: RoutingDecision

    execution_strategy: ExecutionStrategy = Field(
        ...,
        description="Execution strategy."
    )