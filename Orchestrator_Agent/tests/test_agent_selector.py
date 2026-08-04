"""
==========================================================
Test - Agent Selector
==========================================================
"""

from routing.agent_selector import AgentSelector
from utils.constants import (
    WorkflowCategory,
    ExecutionStrategy,
)


def main():

    selector = AgentSelector()

    test_cases = [

        (
            WorkflowCategory.CONTENT,
            ExecutionStrategy.SINGLE,
        ),

        (
            WorkflowCategory.EDUCATIONAL,
            ExecutionStrategy.SINGLE,
        ),

        (
            WorkflowCategory.MULTIMEDIA,
            ExecutionStrategy.SINGLE,
        ),

        (
            WorkflowCategory.COMPOSITE,
            ExecutionStrategy.SEQUENTIAL,
        ),

        (
            WorkflowCategory.CONTEXT,
            ExecutionStrategy.CONTEXT_BASED,
        ),

        (
            WorkflowCategory.SYSTEM,
            ExecutionStrategy.SINGLE,
        ),
    ]

    print("=" * 80)
    print("Agent Selector Test")
    print("=" * 80)

    for workflow, strategy in test_cases:

        agents = selector.select_agents(
            workflow,
            strategy,
        )

        print(f"Workflow : {workflow.value}")
        print(f"Strategy : {strategy.value}")
        print(
            f"Agents   : "
            f"{[agent.value for agent in agents]}"
        )

        print("-" * 80)


if __name__ == "__main__":
    main()