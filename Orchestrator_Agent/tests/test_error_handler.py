"""
==========================================================
Test - Error Handler
==========================================================
"""

from services.state_manager import StateManager
from services.error_handler import ErrorHandler

from utils.constants import ErrorCode


def main():

    state = StateManager.initialize_state()

    state["request_id"] = "REQ-404"

    try:

        # Simulated error

        result = 10 / 0

    except Exception as e:

        response = ErrorHandler.handle_exception(

            state,

            e,

            ErrorCode.INTERNAL_ERROR,

        )

        print("=" * 80)
        print("Error Handler Test")
        print("=" * 80)

        print("\nReturned Response")

        print(response)

        print("\nUpdated State")

        print(state)

    print("\n")

    response = ErrorHandler.build_error_response(

        request_id="REQ-999",

        error_code=ErrorCode.INVALID_REQUEST,

        message="Query cannot be empty.",

    )

    print("=" * 80)

    print("Custom Error Response")

    print("=" * 80)

    print(response)


if __name__ == "__main__":
    main()