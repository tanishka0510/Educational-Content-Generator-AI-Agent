"""
==========================================================
Test - Workflow Manager
==========================================================
"""

from routing.workflow_manager import WorkflowManager
from utils.constants import Intent


def main():

    manager = WorkflowManager()

    intents = [

        Intent.UPLOAD,
        Intent.QA,
        Intent.SUMMARY,
        Intent.QUIZ,
        Intent.FLASHCARDS,
        Intent.LEARNING_OBJECTIVES,
        Intent.MULTIMEDIA,
        Intent.RESOURCE_SEARCH,
        Intent.COMPARE,
        Intent.EXPLANATION,
        Intent.PROGRAMMING,
        Intent.MATHEMATICS,
        Intent.ASSIGNMENT,
        Intent.STUDY_PLAN,
        Intent.MIXED_QUERY,
        Intent.FOLLOW_UP,
        Intent.GENERAL_KNOWLEDGE,
        Intent.ADMIN,
    ]

    print("=" * 80)
    print("Workflow Manager Test")
    print("=" * 80)

    for intent in intents:

        workflow = manager.get_workflow(intent)

        print(f"Intent   : {intent.value}")
        print(f"Workflow : {workflow.value}")
        print("-" * 80)


if __name__ == "__main__":
    main()