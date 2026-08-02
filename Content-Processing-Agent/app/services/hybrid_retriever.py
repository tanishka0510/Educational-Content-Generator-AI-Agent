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

UPLOADED_DB_THRESHOLD = 0.90

SUBJECT_DB_THRESHOLD = 1.80


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
    # STEP 1 : Decide which database to search
    # =====================================================

    # ---------- CASE 1 : Subject is selected ----------
    if subject:

        print("\nUsing Subject Knowledge Base\n")

        documents, score = search_knowledge(
            subject=subject,
            query=question,
            k=5,
        )

        print("Retrieved docs :", len(documents))
        print("Retrieved score:", score)

        source = "knowledge_base"

    # ---------- CASE 2 : No subject -> use uploaded document ----------
    else:

        print("\nUsing Uploaded Document\n")

        documents, score = search_uploaded_document(
            query=question,
            k=5,
        )

        print("Uploaded docs :", len(documents))
        print("Uploaded score:", score)

        source = "uploaded_document"

    # =====================================================
    # Decide whether external search is needed
    # =====================================================

    if len(documents) == 0:
        need_external = True

    elif score is None:
        need_external = True

    else:
        need_external = False

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

        search_query = question if subject is None else f"{subject} {question}"

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
        "source": source,
    }