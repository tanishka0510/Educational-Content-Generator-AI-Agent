from fastapi import APIRouter

from models.chat_model import ChatRequest
from services.content_processing_client import process_content
from services.chat_service import process_chat_query


router = APIRouter()


@router.post("/chat")
async def chat(request: ChatRequest):

    # ======================================================
    # Step 1: Ask the Content Processing Agent to process
    # the user's question/request.
    #
    # If document_uploaded=True:
    #     Content Processing Agent should use the uploaded
    #     document.
    #
    # If document_uploaded=False:
    #     Content Processing Agent should use the selected
    #     subject's knowledge base / external retrieval.
    # ======================================================

    content_response = process_content(
        subject=request.subject,
        question=request.question,
        document_uploaded=request.document_uploaded,
    )

    # ======================================================
    # Step 2: Educational Content Generator takes the
    # processed information and generates the final answer.
    #
    # The chat service also handles the requested response
    # style, such as:
    #
    # - brief
    # - detailed
    # - one word
    # - beginner friendly
    # - exam oriented
    # - step by step
    # - bullet points
    # ======================================================

    response = process_chat_query(
        subject=request.subject,
        question=request.question,
        content_response=content_response,
        document_uploaded=request.document_uploaded,
    )

    return response