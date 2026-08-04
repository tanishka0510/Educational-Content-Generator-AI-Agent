from schemas.response import *

response = OrchestratorResponse(

    status=ResponseStatus.SUCCESS,

    message="Success",

    data=ResponseData(
        content={
            "summary": "Hello"
        }
    ),

    metadata=ResponseMetadata(
        request_id="REQ001",
        execution_time=1.42
    )

)

print(response.model_dump_json(indent=4))