"""
RAG Service

Coordinates retrieval and LLM generation.

The hybrid_retriever is the ONLY component responsible
for deciding whether external search is required.
"""

from app.services.hybrid_retriever import hybrid_search
from app.services.llm_service import (
    generate_answer,
    process_content,
)


# ==========================================================
# Question Answering
# ==========================================================

def ask_question(subject: str, question: str):

    data = hybrid_search(subject, question)

    docs = data["documents"]
    score = data["score"]

    external_context = data.get("external_context", "")
    external_sources = data.get("external_sources", [])

    videos = data.get("videos", [])
    khan = data.get("khan", [])
    nptel = data.get("nptel", [])

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

        if data["source"] == "uploaded_document":

            return {
                "question": question,
                "answer": "The uploaded document does not contain enough information.",
                "sources": [],
                "retrieval_score": score,
            }

        return {
            "question": question,
            "answer": "No relevant information could be found.",
            "sources": [],
            "retrieval_score": score,
        }

    # --------------------------------------------------
    # Generate Answer
    # --------------------------------------------------

    answer = generate_answer(
        context=context,
        question=question,
        source=data["source"],
    )

    # --------------------------------------------------
    # Collect Sources
    # --------------------------------------------------

    sources = []

    if docs:

        sources.extend(
            list(
                dict.fromkeys(
                    doc.metadata.get("source", "")
                    for doc in docs
                )
            )
        )

    sources.extend(external_sources)

    sources = list(dict.fromkeys(sources))

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

def process_question(subject: str, question: str):

    data = hybrid_search(subject, question)

    docs = data["documents"]
    score = data["score"]

    external_context = data.get("external_context", "")
    external_sources = data.get("external_sources", [])

    videos = data.get("videos", [])
    khan = data.get("khan", [])
    nptel = data.get("nptel", [])

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

        if data["source"] == "uploaded_document":

            return {
                "summary": "The uploaded document does not contain enough information.",
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
        source=data["source"],
    )

    # --------------------------------------------------
    # Collect Sources
    # --------------------------------------------------

    sources = []

    if docs:

        sources.extend(
            list(
                dict.fromkeys(
                    doc.metadata.get("source", "")
                    for doc in docs
                )
            )
        )

    sources.extend(external_sources)

    result["sources"] = list(dict.fromkeys(sources))
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