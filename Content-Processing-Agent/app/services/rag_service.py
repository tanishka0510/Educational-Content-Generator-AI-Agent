from app.services.hybrid_retriever import hybrid_search
from app.services.llm_service import generate_answer, process_content


# ==========================================================
# Question Answering
# ==========================================================

def ask_question(subject: str, question: str):

    data = hybrid_search(subject, question)

    docs = data["documents"]
    score = data["score"]

    videos = data["videos"]
    khan = data["khan"]
    nptel = data["nptel"]

    used_external = data["used_external"]

    # --------------------------------------------------
    # No Local Knowledge
    # --------------------------------------------------

    if len(docs) == 0:

        response = {
            "question": question,
            "answer": (
                "The uploaded knowledge base does not contain enough "
                "information to answer this question."
            ),
            "sources": [],
            "retrieval_score": score,
        }

        if used_external:
            response["videos"] = videos
            response["khan"] = khan
            response["nptel"] = nptel

        return response

    # --------------------------------------------------
    # Build Context
    # --------------------------------------------------

    context = "\n\n".join(
        doc.page_content
        for doc in docs
    )

    # --------------------------------------------------
    # Generate Answer
    # --------------------------------------------------

    answer = generate_answer(
        context=context,
        question=question
    )

    # --------------------------------------------------
    # Sources
    # --------------------------------------------------

    sources = list(
        dict.fromkeys(
            doc.metadata.get("source", "")
            for doc in docs
        )
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

    # --------------------------------------------------
    # Attach external resources ONLY if used
    # --------------------------------------------------

    if used_external:

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

    videos = data["videos"]
    khan = data["khan"]
    nptel = data["nptel"]

    used_external = data["used_external"]

    # --------------------------------------------------
    # No Local Knowledge
    # --------------------------------------------------

    if len(docs) == 0:

        response = {
            "summary": (
                "No relevant information was found in the selected subject."
            ),
            "learning_objectives": [],
            "keywords": [],
            "concepts": [],
            "difficulty": "Unknown",
            "sources": [],
            "retrieval_score": score,
        }

        if used_external:

            if videos:
                response["videos"] = videos

            if khan:
                response["khan"] = khan

            if nptel:
                response["nptel"] = nptel

        return response

    # --------------------------------------------------
    # Build Context
    # --------------------------------------------------

    context = "\n\n".join(
        doc.page_content
        for doc in docs
    )

    # --------------------------------------------------
    # Generate Educational Content
    # --------------------------------------------------

    result = process_content(
        context=context,
        question=question
    )

    # --------------------------------------------------
    # Sources
    # --------------------------------------------------

    result["sources"] = list(
        dict.fromkeys(
            doc.metadata.get("source", "")
            for doc in docs
        )
    )

    result["retrieval_score"] = score

    # --------------------------------------------------
    # Attach external resources ONLY if used
    # --------------------------------------------------

    if used_external:

        if videos:
            result["videos"] = videos

        if khan:
            result["khan"] = khan

        if nptel:
            result["nptel"] = nptel

    return result