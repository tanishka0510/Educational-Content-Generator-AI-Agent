"""
==========================================================
Router

Project:
Educational Content Generator AI

Module:
Orchestrator Agent

Purpose:
Coordinates the complete routing pipeline by invoking
all routing components and generating the final
execution plan.

Version:
1.0

Author:
Team Orchestrator
==========================================================
"""

from schemas.request import OrchestratorRequest
from schemas.workflow import (
    WorkflowInfo,
    RoutingDecision,
    ExecutionPlan,
)

from routing.intent_detector import IntentDetector
from routing.workflow_manager import WorkflowManager
from routing.execution_planner import ExecutionPlanner
from routing.agent_selector import AgentSelector

from utils.logger import get_logger

logger = get_logger(__name__)


class Router:
    """
    Coordinates all routing components.

    Pipeline

    Request
        ↓
    Intent Detector
        ↓
    Workflow Manager
        ↓
    Execution Planner
        ↓
    Agent Selector
        ↓
    Execution Plan
    """

    def __init__(self):

        self.intent_detector = IntentDetector()

        self.workflow_manager = WorkflowManager()

        self.execution_planner = ExecutionPlanner()

        self.agent_selector = AgentSelector()

    def route(
        self,
        request: OrchestratorRequest,
    ) -> ExecutionPlan:
        """
        Executes the complete routing pipeline.

        Parameters
        ----------
        request : OrchestratorRequest

        Returns
        -------
        ExecutionPlan
        """

        logger.info("Starting routing pipeline.")

        # ------------------------------------------
        # Step 1
        # Detect Intent
        # ------------------------------------------

        intent = self.intent_detector.detect(request)

        # ------------------------------------------
        # Step 2
        # Select Workflow
        # ------------------------------------------

        workflow = self.workflow_manager.get_workflow(
            intent
        )

        # ------------------------------------------
        # Step 3
        # Select Execution Strategy
        # ------------------------------------------

        strategy = self.execution_planner.get_execution_strategy(
            workflow
        )

        # ------------------------------------------
        # Step 4
        # Select Agents
        # ------------------------------------------

        agents = self.agent_selector.select_agents(
            workflow,
            strategy,
        )

        # ------------------------------------------
        # Step 5
        # Build Workflow Information
        # ------------------------------------------

        workflow_info = WorkflowInfo(
            intent=intent,
            workflow=workflow,
        )

        routing_decision = RoutingDecision(
            workflow_info=workflow_info,
            selected_agents=agents,
        )

        execution_plan = ExecutionPlan(
            routing=routing_decision,
            execution_strategy=strategy,
        )

        logger.info("Routing pipeline completed successfully.")

        return execution_plan