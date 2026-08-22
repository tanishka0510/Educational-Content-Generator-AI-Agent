"""
Content Processing Agent Client

Communicates with the Content Processing Agent through HTTP.

This client provides two levels of communication:

1. retrieve_content()
   - Calls /retrieve/
   - Used when the caller only needs retrieved documents/context.

2. process_content()
   - Calls /process-content
   - Used by the Educational Content Generator Agent.
   - Runs the complete Content Processing Agent pipeline:
       Local retrieval
       -> Uploaded document / Subject KB
       -> Web fallback when applicable
       -> RAG processing
       -> Educational content generation
"""

import httpx


# ==========================================================
# Configuration
# ==========================================================

CONTENT_PROCESSING_AGENT_URL = "http://127.0.0.1:8001"
REQUEST_TIMEOUT = 60.0


# ==========================================================
# Retrieve Content
# ==========================================================

def retrieve_content(
    subject: str | None,
    question: str,
    document_uploaded: bool = False,
):
    """
    Retrieve relevant content from the Content Processing Agent.

    This function calls the low-level /retrieve/ endpoint.

    Parameters
    ----------
    subject : str | None
        Currently selected subject.

        Example:
            "OOP"

        For uploaded-document mode, this can be None depending
        on the Content Processing Agent's current API design.

    question : str
        User's question or content-generation request.

    document_uploaded : bool
        True when the user has uploaded a document.
        False when the system should use the subject
        knowledge base / external retrieval.

    Returns
    -------
    dict
        Raw retrieval response returned by the Content Processing Agent.
    """

    url = f"{CONTENT_PROCESSING_AGENT_URL}/retrieve/"

    payload = {
        "subject": subject,
        "question": question,
        "document_uploaded": document_uploaded,
    }

    try:

        response = httpx.post(
            url,
            json=payload,
            timeout=REQUEST_TIMEOUT,
        )

        response.raise_for_status()

        return response.json()

    except httpx.HTTPStatusError as e:

        print(
            "Content Processing Agent HTTP Error:",
            e.response.status_code,
            e.response.text,
        )

        raise

    except httpx.RequestError as e:

        print(
            "Could not connect to Content Processing Agent:",
            str(e),
        )

        raise


# ==========================================================
# Process Content
# ==========================================================

def process_content(
    subject: str | None,
    question: str,
    document_uploaded: bool = False,
):
    """
    Process a question/request through the complete
    Content Processing Agent pipeline.

    This function calls /process-content/.

    The Content Processing Agent is responsible for:

        1. Selecting the appropriate retrieval source.
        2. Searching the uploaded document or subject KB.
        3. Deciding whether external search is required.
        4. Generating the educational content.
        5. Returning the final processed response.

    Parameters
    ----------
    subject : str | None
        Currently selected subject.

    question : str
        User's question or educational-content request.

    document_uploaded : bool
        True when the user has uploaded a document.

    Returns
    -------
    dict
        Final processed response returned by the
        Content Processing Agent.
    """

    url = f"{CONTENT_PROCESSING_AGENT_URL}/process-content"

    payload = {
        "subject": subject,
        "question": question,
        "document_uploaded": document_uploaded,
    }

    try:

        response = httpx.post(
            url,
            json=payload,
            timeout=REQUEST_TIMEOUT,
        )

        response.raise_for_status()

        return response.json()

    except httpx.HTTPStatusError as e:

        print(
            "Content Processing Agent HTTP Error:",
            e.response.status_code,
            e.response.text,
        )

        raise

    except httpx.RequestError as e:

        print(
            "Could not connect to Content Processing Agent:",
            str(e),
        )

        raise