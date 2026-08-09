"""
RAG Service

Coordinates retrieval and LLM generation.

The hybrid_retriever is responsible for retrieval decisions.
"""

from app.services.hybrid_retriever import hybrid_search
from app.services.llm_service import (
    generate_answer,
    process_content,
)


# ==========================================================
# Question Answering
# ==========================================================

def ask_question(
    subject: str,
    question: str,
    document_uploaded: bool = False,
):
    """
    Retrieve information and generate an answer.

    When document_uploaded=True:
        Only the uploaded document is searched.

    When document_uploaded=False:
        Subject knowledge base is searched first,
        followed by external search when required.
    """

    data = hybrid_search(
        subject=subject,
        question=question,
        document_uploaded=document_uploaded,
    )

    docs = data.get("documents", [])
    score = data.get("score")

    external_context = data.get(
        "external_context",
        "",
    )

    external_sources = data.get(
        "external_sources",
        [],
    )

    videos = data.get(
        "videos",
        [],
    )

    khan = data.get(
        "khan",
        [],
    )

    nptel = data.get(
        "nptel",
        [],
    )

    # --------------------------------------------------
    # Build Context
    # --------------------------------------------------

    context = ""

    if docs:

        context += "\n\n".join(
            doc.page_content
            for doc in docs
        )

    if external_context:

        context += (
            "\n\n========== WEB KNOWLEDGE ==========\n"
            + external_context
        )

    # --------------------------------------------------
    # Nothing Retrieved
    # --------------------------------------------------

    if context.strip() == "":

        if data.get("source") == "uploaded_document":

            return {
                "question": question,
                "answer": (
                    "The uploaded document does not "
                    "contain enough information."
                ),
                "sources": [],
                "retrieval_score": score,
            }

        return {
            "question": question,
            "answer": (
                "No relevant information could be found."
            ),
            "sources": [],
            "retrieval_score": score,
        }

    # --------------------------------------------------
    # Generate Answer
    # --------------------------------------------------

    answer = generate_answer(
        context=context,
        question=question,
        source=data.get(
            "source",
            "unknown",
        ),
    )

    # --------------------------------------------------
    # Collect Sources
    # --------------------------------------------------

    sources = []

    if docs:

        for doc in docs:

            source_name = doc.metadata.get(
                "source",
                "",
            )

            if source_name:
                sources.append(source_name)

    sources.extend(external_sources)

    sources = list(
        dict.fromkeys(sources)
    )

    # --------------------------------------------------
    # Response
    # --------------------------------------------------

    response = {
        "question": question,
        "answer": answer,
        "sources": sources,
        "retrieval_score": score,
    }

    if videos:
        response["videos"] = videos

    if khan:
        response["khan"] = khan

    if nptel:
        response["nptel"] = nptel

    return response


# ==========================================================
# Educational Content Processing
# ==========================================================

def process_question(
    subject: str,
    question: str,
    document_uploaded: bool = False,
):
    """
    Retrieve information and generate educational content.

    When document_uploaded=True:
        Only the uploaded document is used.

    When document_uploaded=False:
        Subject knowledge base is searched and web fallback
        is allowed when the local knowledge base is insufficient.
    """

    data = hybrid_search(
        subject=subject,
        question=question,
        document_uploaded=document_uploaded,
    )

    docs = data.get(
        "documents",
        [],
    )

    score = data.get(
        "score",
    )

    external_context = data.get(
        "external_context",
        "",
    )

    external_sources = data.get(
        "external_sources",
        [],
    )

    videos = data.get(
        "videos",
        [],
    )

    khan = data.get(
        "khan",
        [],
    )

    nptel = data.get(
        "nptel",
        [],
    )

    # --------------------------------------------------
    # Build Context
    # --------------------------------------------------

    context = ""

    if docs:

        context += "\n\n".join(
            doc.page_content
            for doc in docs
        )

    if external_context:

        context += (
            "\n\n========== WEB KNOWLEDGE ==========\n"
            + external_context
        )

    # --------------------------------------------------
    # Nothing Retrieved
    # --------------------------------------------------

    if context.strip() == "":

        if data.get("source") == "uploaded_document":

            return {
                "summary": (
                    "The uploaded document does not "
                    "contain enough information."
                ),
                "learning_objectives": [],
                "keywords": [],
                "concepts": [],
                "difficulty": "Unknown",
                "sources": [],
                "retrieval_score": score,
            }

        return {
            "summary": "No relevant information found.",
            "learning_objectives": [],
            "keywords": [],
            "concepts": [],
            "difficulty": "Unknown",
            "sources": [],
            "retrieval_score": score,
        }

    # --------------------------------------------------
    # Generate Educational Content
    # --------------------------------------------------

    result = process_content(
        context=context,
        question=question,
        source=data.get(
            "source",
            "unknown",
        ),
    )

    # --------------------------------------------------
    # Collect Sources
    # --------------------------------------------------

    sources = []

    if docs:

        for doc in docs:

            source_name = doc.metadata.get(
                "source",
                "",
            )

            if source_name:
                sources.append(source_name)

    sources.extend(external_sources)

    result["sources"] = list(
        dict.fromkeys(sources)
    )

    result["retrieval_score"] = score

    # --------------------------------------------------
    # Optional Educational Resources
    # --------------------------------------------------

    if videos:
        result["videos"] = videos

    if khan:
        result["khan"] = khan

    if nptel:
        result["nptel"] = nptel

    return result