from app.knowledge.knowledge_service import (
    search_knowledge,
    search_uploaded_document,
)

from app.services.youtube_service import search_youtube
from app.services.khan_service import search_khan
from app.services.nptel_service import search_nptel
from app.services.tavily_service import search_tavily
from app.services.duckduckgo_service import search_duckduckgo

from app.core.config import settings


UPLOADED_DB_THRESHOLD = settings.UPLOADED_DB_THRESHOLD
SUBJECT_DB_THRESHOLD = settings.SUBJECT_DB_THRESHOLD


def hybrid_search(subject: str, question: str):

    print("\n========== HYBRID SEARCH ==========")
    print("Subject :", subject)
    print("Question:", question)
    print("===================================\n")

    # =====================================================
    # STEP 1 : Local Retrieval
    # =====================================================

    if subject:

        print("Searching Subject Database...\n")

        documents, score = search_knowledge(
            subject=subject,
            query=question,
            k=5,
        )

        source = "knowledge_base"

    else:

        print("Searching Uploaded Document...\n")

        documents, score = search_uploaded_document(
            query=question,
            k=5,
        )

        source = "uploaded_document"

    print("Retrieved Docs :", len(documents))
    print("Score :", score)

    # =====================================================
    # STEP 2 : Decide whether Web Search is required
    # =====================================================

    use_external = False

    # -----------------------------------------------------
    # Uploaded Document Mode
    # -----------------------------------------------------
    # Never use web search when an uploaded document exists.
    # If the uploaded document doesn't contain the answer,
    # Gemini should return:
    # "The uploaded document does not contain enough information."
    # -----------------------------------------------------

    if source == "uploaded_document":

        use_external = False

    # -----------------------------------------------------
    # Subject Knowledge Base Mode
    # -----------------------------------------------------

    else:

        if len(documents) == 0:

            use_external = True

        elif score is None:

            use_external = True

        elif score > SUBJECT_DB_THRESHOLD:

            use_external = True

        else:

            use_external = False

    # =====================================================
    # STEP 3 : External Search
    # =====================================================

    external_context = ""
    external_sources = []

    # -----------------------------------------------------
    # Uploaded Document
    # -----------------------------------------------------

    if source == "uploaded_document":

        print("\n========== UPLOADED DOCUMENT MODE ==========")
        print("External search is disabled.")
        print("Only uploaded document will be used.\n")

    # -----------------------------------------------------
    # Subject KB + Web Fallback
    # -----------------------------------------------------

    elif use_external:

        print("\n========== WEB FALLBACK ==========\n")

        # ---------- Tavily ----------
        try:

            tavily_context, tavily_sources = search_tavily(question)

            external_context += tavily_context

            external_sources.extend(tavily_sources)

        except Exception as e:

            print("Tavily Error :", e)

        # ---------- DuckDuckGo ----------
        try:

            duck_context = search_duckduckgo(question)

            if duck_context:

                external_context += "\n\n" + duck_context

        except Exception as e:

            print("DuckDuckGo Error :", e)

        if external_context.strip():

            source = "web"

    # -----------------------------------------------------
    # Local KB sufficient
    # -----------------------------------------------------

    else:

        print("\nLocal KB sufficient.\n")

    # =====================================================
    # STEP 4 : Educational Resources
    # =====================================================

    youtube = []
    khan = []
    nptel = []

    question_lower = question.lower()

    # ---------- YouTube only if user explicitly asks ----------
    wants_video = any(
        keyword in question_lower
        for keyword in [
            "video",
            "youtube",
            "watch",
            "lecture",
            "tutorial",
        ]
    )

    if wants_video:

        print("\nSearching YouTube...\n")

        youtube = search_youtube(
            question,
            max_results=3,
        )

    # ---------- Course Resources ----------
    wants_course = any(
        keyword in question_lower
        for keyword in [
            "course",
            "learn",
            "study",
            "full course",
        ]
    )

    if wants_course:

        print("\nSearching Khan Academy...\n")
        khan = search_khan(question)

        print("\nSearching NPTEL...\n")
        nptel = search_nptel(question)

    # =====================================================
    # STEP 5 : Return
    # =====================================================

    return {

        "documents": documents,

        "score": score,

        "source": source,

        "used_external": use_external,

        "external_context": external_context,

        "external_sources": external_sources,

        "videos": youtube,

        "khan": khan,

        "nptel": nptel,

    }