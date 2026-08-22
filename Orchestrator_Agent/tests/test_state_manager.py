"""
==========================================================
Test - State Manager
==========================================================
"""

from services.state_manager import StateManager


def main():

    # -----------------------------------------
    # Initialize State
    # -----------------------------------------

    state = StateManager.initialize_state()

    print("=" * 80)
    print("State Manager Test")
    print("=" * 80)

    print("\nInitial State")
    print(state)

    # -----------------------------------------
    # Update Status
    # -----------------------------------------

    StateManager.update_status(
        state,
        "running"
    )

    print("\nStatus")
    print(state["status"])

    # -----------------------------------------
    # Update Routing
    # -----------------------------------------

    StateManager.update_routing(
        state,
        intent="quiz",
        workflow="educational",
        execution_strategy="single",
        selected_agents=["educational"],
    )

    print("\nRouting Information")

    print("Intent :", state["intent"])
    print("Workflow :", state["workflow"])
    print("Strategy :", state["execution_strategy"])
    print("Agents :", state["selected_agents"])

    # -----------------------------------------
    # Educational Output
    # -----------------------------------------

    StateManager.update_educational_output(
        state,
        {
            "quiz": "10 MCQs generated."
        }
    )

    print("\nEducational Output")

    print(state["educational_output"])

    # -----------------------------------------
    # Final Response
    # -----------------------------------------

    StateManager.update_response(
        state,
        {
            "message": "Success"
        }
    )

    print("\nResponse")

    print(state["response"])

    # -----------------------------------------
    # Retry Count
    # -----------------------------------------

    StateManager.increment_retry(state)

    print("\nRetry Count")

    print(state["retry_count"])

    # -----------------------------------------
    # Error
    # -----------------------------------------

    StateManager.set_error(
        state,
        "Sample Error"
    )

    print("\nError")

    print(state["error"])

    # -----------------------------------------
    # Final State
    # -----------------------------------------

    print("\nFinal State")

    print(state)


if __name__ == "__main__":
    main()