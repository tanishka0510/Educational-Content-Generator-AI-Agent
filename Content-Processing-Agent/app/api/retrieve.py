"""
Retrieval API

Provides retrieved knowledge/context to other agents,
such as the Educational Content Generator Agent.

This API does NOT generate the final educational answer.

It only performs retrieval through the Content Processing Agent.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.hybrid_retriever import hybrid_search


router = APIRouter(
    prefix="/retrieve",
    tags=["Retrieval"],
)


# ==========================================================
# Request Model
# ==========================================================

class RetrieveRequest(BaseModel):

    subject: str
    question: str
    document_uploaded: bool = False


# ==========================================================
# Retrieve Content
# ==========================================================

@router.post("/")
async def retrieve_content(request: RetrieveRequest):

    print("\n========== RETRIEVAL API ==========")
    print("Subject :", request.subject)
    print("Question:", request.question)
    print("Document Uploaded :", request.document_uploaded)
    print("===================================\n")

    # ------------------------------------------------------
    # Validate request
    # ------------------------------------------------------

    if not request.subject.strip():

        raise HTTPException(
            status_code=400,
            detail="Subject is required.",
        )

    if not request.question.strip():

        raise HTTPException(
            status_code=400,
            detail="Question is required.",
        )

    # ------------------------------------------------------
    # Select retrieval mode
    # ------------------------------------------------------

    try:

        if request.document_uploaded:

            print("MODE: Uploaded Document")

            data = hybrid_search(
                subject="",
                question=request.question,
            )

        else:

            print("MODE: Subject Knowledge Base")

            data = hybrid_search(
                subject=request.subject,
                question=request.question,
            )

    except Exception as e:

        print("Retrieval Error :", e)

        raise HTTPException(
            status_code=500,
            detail=f"Retrieval failed: {str(e)}",
        )

    # ------------------------------------------------------
    # Convert LangChain Documents into JSON
    # ------------------------------------------------------

    documents = []

    for doc in data.get("documents", []):

        documents.append(
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
            }
        )

    # ======================================================
    # IMPORTANT: Uploaded Document Has No Answer
    # ======================================================

    if request.document_uploaded and len(documents) == 0:

        print(
            "\nNo relevant information found "
            "in uploaded document."
        )

        return {
            "subject": request.subject,
            "question": request.question,

            "source": "uploaded_document",

            "documents": [],

            "retrieval_score": data.get("score"),

            "used_external": False,

            "external_context": "",

            "external_sources": [],

            "videos": [],

            "khan": [],

            "nptel": [],

            "answer_available": False,

            "message": (
                "The uploaded document does not "
                "contain enough information to answer "
                "this question."
            ),
        }

    # ======================================================
    # Normal Retrieval Result
    # ======================================================

    return {
        "subject": request.subject,
        "question": request.question,

        "source": data.get(
            "source",
            "unknown",
        ),

        "documents": documents,

        "retrieval_score": data.get(
            "score"
        ),

        "used_external": data.get(
            "used_external",
            False,
        ),

        "external_context": data.get(
            "external_context",
            "",
        ),

        "external_sources": data.get(
            "external_sources",
            [],
        ),

        "videos": data.get(
            "videos",
            [],
        ),

        "khan": data.get(
            "khan",
            [],
        ),

        "nptel": data.get(
            "nptel",
            [],
        ),

        "answer_available": True,

        "message": None,
    }