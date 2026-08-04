from schemas.request import *

request = OrchestratorRequest(

    session=SessionInfo(
        request_id="REQ001",
        session_id="S001",
        conversation_id="C001"
    ),

    user_input=UserInput(
        query="Generate quiz",
        uploaded_files=["notes.pdf"]
    ),

    metadata=RequestMetadata()

)

print(request.model_dump_json(indent=4))