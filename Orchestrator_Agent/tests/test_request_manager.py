"""
==========================================================
Test - Request Manager
==========================================================
"""

from services.request_manager import RequestManager


def main():

    manager = RequestManager()

    request = manager.create_request(

        query="Generate a quiz",

        session_id="session_001",

        conversation_id="conversation_001",

        uploaded_files=["notes.pdf"],

        source="web",

        language="en",
    )

    print("=" * 80)
    print("Request Manager Test")
    print("=" * 80)

    print("Request ID      :", request.session.request_id)
    print("Session ID      :", request.session.session_id)
    print("Conversation ID :", request.session.conversation_id)

    print()

    print("Query           :", request.user_input.query)
    print("Files           :", request.user_input.uploaded_files)

    print()

    print("Source          :", request.metadata.source)
    print("Language        :", request.metadata.language)
    print("Timestamp       :", request.metadata.timestamp)

    print()

    print(
        "Validation      :",
        manager.validate_request(request)
    )


if __name__ == "__main__":
    main()