"""
==========================================================
Test - Execution Planner
==========================================================
"""

from routing.execution_planner import ExecutionPlanner
from utils.constants import WorkflowCategory


def main():

    planner = ExecutionPlanner()

    workflows = [

        WorkflowCategory.CONTENT,
        WorkflowCategory.EDUCATIONAL,
        WorkflowCategory.MULTIMEDIA,
        WorkflowCategory.COMPOSITE,
        WorkflowCategory.CONTEXT,
        WorkflowCategory.SYSTEM,
    ]

    print("=" * 80)
    print("Execution Planner Test")
    print("=" * 80)

    for workflow in workflows:

        strategy = planner.get_execution_strategy(
            workflow
        )

        print(f"Workflow : {workflow.value}")
        print(f"Strategy : {strategy.value}")
        print("-" * 80)


if __name__ == "__main__":
    main()