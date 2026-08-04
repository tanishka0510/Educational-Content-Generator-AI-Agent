"""
==========================================================
Test - Response Aggregator
==========================================================
"""

from services.state_manager import StateManager
from services.response_aggregator import ResponseAggregator


def main():

    state = StateManager.initialize_state()

    state["request_id"] = "REQ-001"

    state["intent"] = "quiz"

    state["workflow"] = "educational"

    state["processed_content"] = {
        "chunks": 25
    }

    state["educational_output"] = {
        "quiz": "10 MCQs Generated"
    }

    state["multimedia_output"] = {
        "image": "mindmap.png"
    }

    response = ResponseAggregator.aggregate(state)

    print("=" * 80)
    print("Response Aggregator Test")
    print("=" * 80)

    for key, value in response.items():
        print(f"{key} : {value}")


if __name__ == "__main__":
    main()