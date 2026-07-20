from app.knowledge.knowledge_service import search_knowledge
from app.services.youtube_service import search_youtube


def hybrid_search(question: str):
    """
    Searches all available knowledge sources.

    Returns:
        {
            "documents": [...],
            "videos": [...]
        }
    """

    documents = search_knowledge(question, k=5)

    videos = search_youtube(
        question,
        max_results=5
    )

    return {
        "documents": documents,
        "videos": videos
    }