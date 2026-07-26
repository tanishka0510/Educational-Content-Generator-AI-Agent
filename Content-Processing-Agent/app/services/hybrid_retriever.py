from app.knowledge.knowledge_service import (
    search_knowledge,
    search_uploaded_document,
)
from app.services.youtube_service import search_youtube
from app.services.khan_service import search_khan
from app.services.nptel_service import search_nptel


# ----------------------------------------------------------
# Lower distance = Better semantic match
#
# 0.00 -> Perfect
# 0.30 -> Excellent
# 0.50 -> Very Good
# 0.65 -> Good
# 0.80 -> Weak
# ----------------------------------------------------------

SIMILARITY_THRESHOLD = 0.75


def hybrid_search(subject: str, question: str):
    """
    Hybrid Retrieval Pipeline

    Priority:
    1. Uploaded Document (if available)
    2. Subject Knowledge Base
    3. External Educational Resources
    """

    print("\n========== HYBRID SEARCH ==========")
    print("Subject  :", subject)
    print("Question :", question)
    print("===================================\n")

    # =====================================================
    # STEP 1 : Search Uploaded Document
    # =====================================================

    uploaded_docs, uploaded_score = search_uploaded_document(
        query=question,
        k=5,
    )

    if (uploaded_docs
        and uploaded_score is not None
        and uploaded_score <= SIMILARITY_THRESHOLD):

        print("\nUsing Uploaded Document.\n")

        return {
            "documents": uploaded_docs,
            "score": uploaded_score,
            "videos": [],
            "khan": [],
            "nptel": [],
            "used_external": False,
            "source": "uploaded_document",
        }

    # =====================================================
    # STEP 2 : Search Subject Knowledge Base
    # =====================================================
    
    if subject is None:
         raise ValueError(
            "No uploaded document exists. Please specify a subject."
        )

    documents, score = search_knowledge(
        subject=subject,
        query=question,
        k=5,
    )

    need_external = (
        len(documents) == 0
        or score is None
        or score > SIMILARITY_THRESHOLD
    )

    youtube = []
    khan = []
    nptel = []

    # =====================================================
    # STEP 3 : Subject KB is enough
    # =====================================================

    if not need_external:

        print("\nLocal Knowledge Base is sufficient.")
        print("Skipping External APIs.\n")

    # =====================================================
    # STEP 4 : Fetch External Resources
    # =====================================================

    else:

        print("\nKnowledge Base confidence is low.")
        print("Fetching External Educational Resources...\n")

        search_query = f"{subject} {question}"

        youtube = search_youtube(
            search_query,
            max_results=3,
        )

        khan = search_khan(search_query)

        nptel = search_nptel(search_query)

    # =====================================================
    # Return
    # =====================================================

    return {
        "documents": documents,
        "score": score,
        "videos": youtube,
        "khan": khan,
        "nptel": nptel,
        "used_external": need_external,
        "source": "knowledge_base",
    }