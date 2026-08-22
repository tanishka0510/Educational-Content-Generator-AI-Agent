"""
LangGraph Compiler

Project: Educational Content Generator AI
Module: Orchestrator Agent (Gateway)
"""

from langgraph.graph import StateGraph, END
from state import AgentState

from graph.nodes import (
    route_request_node,
    content_processing_node,
    educational_agent_node,
    multimedia_agent_node,
    aggregate_results_node,
)
from graph.edges import (
    route_after_router,
    route_after_content,
    route_after_educational,
)


def compile_workflow():
    """
    Constructs, wires, and compiles the multi-agent Orchestrator LangGraph.
    """
    # 1. Create StateGraph
    workflow = StateGraph(AgentState)

    # 2. Add Nodes
    workflow.add_node("route_request", route_request_node)
    workflow.add_node("content_processing", content_processing_node)
    workflow.add_node("educational", educational_agent_node)
    workflow.add_node("multimedia", multimedia_agent_node)
    workflow.add_node("aggregate", aggregate_results_node)

    # 3. Set Entry Point
    workflow.set_entry_point("route_request")

    # 4. Add Conditional Routing Edges
    workflow.add_conditional_edges(
        "route_request",
        route_after_router,
        {
            "content_processing": "content_processing",
            "educational": "educational",
            "multimedia": "multimedia",
            "aggregate": "aggregate",
        }
    )

    workflow.add_conditional_edges(
        "content_processing",
        route_after_content,
        {
            "educational": "educational",
            "multimedia": "multimedia",
            "aggregate": "aggregate",
        }
    )

    workflow.add_conditional_edges(
        "educational",
        route_after_educational,
        {
            "multimedia": "multimedia",
            "aggregate": "aggregate",
        }
    )

    # 5. Add Direct Transition Edges
    workflow.add_edge("multimedia", "aggregate")
    workflow.add_edge("aggregate", END)

    # 6. Compile
    return workflow.compile()


# Compile the global graph app
orchestrator_graph = compile_workflow()
