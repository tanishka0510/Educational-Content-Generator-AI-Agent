from schemas.errors import *

error = ErrorResponse(

    error_code=ErrorCode.INVALID_REQUEST,

    message="Invalid request.",

    metadata=ErrorMetadata(
        component="router"
    )

)

print(error.model_dump_json(indent=4))