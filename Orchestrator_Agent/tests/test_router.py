"""
==========================================================
Test - Router
==========================================================
"""

import uuid

from routing.router import Router

from schemas.request import (
    SessionInfo,
    UserInput,
    RequestMetadata,
    OrchestratorRequest,
)


def test(query: str):

    router = Router()

    request = OrchestratorRequest(

        session=SessionInfo(
            request_id=str(uuid.uuid4()),
            session_id="session_001",
            conversation_id="conversation_001",
        ),

        user_input=UserInput(
            query=query,
            uploaded_files=[],
        ),

        metadata=RequestMetadata(
            source="web",
            language="en",
        ),
    )

    result = router.route(request)

    print("=" * 80)
    print(f"Query       : {query}")
    print("=" * 80)

    print(
        "Intent      :",
        result.routing.workflow_info.intent.value,
    )

    print(
        "Workflow    :",
        result.routing.workflow_info.workflow.value,
    )

    print(
        "Strategy    :",
        result.execution_strategy.value,
    )

    print(
        "Agents      :",
        [agent.value for agent in result.routing.selected_agents],
    )

    print()


def main():

    queries = [

        "Upload this PDF",

        "Answer this question",

        "Generate a summary",

        "Create a quiz",

        "Generate flashcards",

        "Create learning objectives",

        "Generate an infographic",

        "Suggest learning resources",

        "Compare CNN and RNN",

        "Explain recursion",

        "Write a Python program",

        "Solve x² + 5x + 6",

        "Generate an assignment",

        "Create a study plan",

        "Upload this PDF and generate a quiz",

        "Explain that again",

        "Tell me about Artificial Intelligence",

        "Show system status",
    ]

    for query in queries:

        test(query)


if __name__ == "__main__":
    main()