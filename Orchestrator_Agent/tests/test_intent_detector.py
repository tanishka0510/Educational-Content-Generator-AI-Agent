"""
==========================================================
Test - Intent Detector

Purpose:
Tests the Intent Detector with different user queries.
==========================================================
"""

from routing.intent_detector import IntentDetector
from schemas.request import (
    OrchestratorRequest,
    SessionInfo,
    UserInput,
    RequestMetadata,
)


def create_request(query: str) -> OrchestratorRequest:
    """
    Creates a sample request for testing.
    """

    return OrchestratorRequest(
        session=SessionInfo(
            request_id="REQ001",
            session_id="SESSION001",
            conversation_id="CONV001",
        ),
        user_input=UserInput(
            query=query,
            uploaded_files=[],
        ),
        metadata=RequestMetadata(),
    )


def main():

    detector = IntentDetector()

    test_queries = [
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

    print("=" * 80)
    print("Intent Detector Test")
    print("=" * 80)

    for query in test_queries:

        request = create_request(query)

        intent = detector.detect(request)

        print(f"Query  : {query}")
        print(f"Intent : {intent.value}")
        print("-" * 80)


if __name__ == "__main__":
    main()