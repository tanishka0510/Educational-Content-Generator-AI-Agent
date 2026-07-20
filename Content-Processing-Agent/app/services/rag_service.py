from app.services.hybrid_retriever import hybrid_search
from app.services.llm_service import generate_answer, process_content


def ask_question(question: str):
    """
    Simple RAG QA using Hybrid Retrieval
    """

    data = hybrid_search(question)

    docs = data["documents"]
    videos = data["videos"]

    # No documents retrieved
    if not docs:
        return {
            "question": question,
            "answer": "The uploaded knowledge base does not contain enough information.",
            "sources": [],
            "videos": videos
        }

    context = "\n\n".join(doc.page_content for doc in docs)

    answer = generate_answer(context, question)

    return {
        "question": question,
        "answer": answer,
        "sources": list(
            dict.fromkeys(
                doc.metadata.get("source", "")
                for doc in docs
            )
        ),
        "videos": videos
    }


def process_question(question: str):
    """
    Content Processing Endpoint using Hybrid Retrieval
    """

    data = hybrid_search(question)

    docs = data["documents"]
    videos = data["videos"]

    # Nothing retrieved
    if not docs:
        return {
            "summary": "The uploaded knowledge base does not contain enough information.",
            "learning_objectives": [],
            "keywords": [],
            "concepts": [],
            "difficulty": "Unknown",
            "sources": [],
            "videos": videos
        }

    context = "\n\n".join(doc.page_content for doc in docs)

    # ---------- IMPORTANT FILTER ----------
    # Reject clearly unrelated retrievals
    question_words = set(question.lower().split())
    context_words = set(context.lower().split())

    overlap = question_words.intersection(context_words)

    if len(overlap) == 0:
        return {
            "summary": "The uploaded knowledge base does not contain enough information.",
            "learning_objectives": [],
            "keywords": [],
            "concepts": [],
            "difficulty": "Unknown",
            "sources": [],
            "videos": videos
        }
    # --------------------------------------

    result = process_content(context, question)

    result["sources"] = list(
        dict.fromkeys(
            doc.metadata.get("source", "")
            for doc in docs
        )
    )

    result["videos"] = videos

    return result