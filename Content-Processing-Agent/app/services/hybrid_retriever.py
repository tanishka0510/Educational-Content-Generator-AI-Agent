"""
Hybrid Retriever

Retrieval flow:

1. Uploaded document mode:
   - Search uploaded document.
   - Never use external web search.
   - If information is not found, return empty context.

2. Subject knowledge-base mode:
   - Search subject knowledge base.
   - If relevant information is not found, use web APIs.

3. Educational resources:
   - YouTube is searched only when explicitly requested.
   - Khan Academy and NPTEL are searched only for course/study requests.
"""

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


# ==========================================================
# Retrieval Thresholds
# ==========================================================

UPLOADED_DB_THRESHOLD = settings.UPLOADED_DB_THRESHOLD
SUBJECT_DB_THRESHOLD = settings.SUBJECT_DB_THRESHOLD


# ==========================================================
# Hybrid Search
# ==========================================================

def hybrid_search(
    subject: str,
    question: str,
    document_uploaded: bool = False,
):

    print("\n========== HYBRID SEARCH ==========")
    print("Subject :", subject)
    print("Question:", question)
    print("Document Uploaded :", document_uploaded)
    print("===================================\n")

    # ======================================================
    # STEP 1 : LOCAL RETRIEVAL
    # ======================================================

    if document_uploaded:

        # --------------------------------------------------
        # Uploaded Document Mode
        # --------------------------------------------------

        print("MODE: Uploaded Document")
        print("Searching Uploaded Document...\n")

        documents, score = search_uploaded_document(
            query=question,
            k=5,
        )

        source = "uploaded_document"

    else:

        # --------------------------------------------------
        # Subject Knowledge Base Mode
        # --------------------------------------------------

        print("MODE: Subject Knowledge Base")
        print("Searching Subject Database...\n")

        documents, score = search_knowledge(
            subject=subject,
            query=question,
            k=5,
        )

        source = "knowledge_base"

    print("Retrieved Docs :", len(documents))
    print("Score :", score)

    # ======================================================
    # STEP 2 : DETERMINE WHETHER EXTERNAL SEARCH IS ALLOWED
    # ======================================================

    use_external = False

    # ------------------------------------------------------
    # Uploaded Document Mode
    # ------------------------------------------------------

    if document_uploaded:

        use_external = False

        print(
            "\n========== UPLOADED DOCUMENT MODE =========="
        )

        print(
            "External search is disabled."
        )

        print(
            "Only uploaded document will be used."
        )

    # ------------------------------------------------------
    # Subject Knowledge Base Mode
    # ------------------------------------------------------

    else:

        if len(documents) == 0:

            print(
                "\nNo relevant subject database chunks found."
            )

            use_external = True

        elif score is None:

            print(
                "\nNo retrieval score available."
            )

            use_external = True

        elif score > SUBJECT_DB_THRESHOLD:

            print(
                "\nSubject database score is above threshold."
            )

            print(
                "External search will be used."
            )

            use_external = True

        else:

            print(
                "\nSubject database contains sufficient information."
            )

            print(
                "Web fallback not required."
            )

            use_external = False

    # ======================================================
    # STEP 3 : EXTERNAL WEB SEARCH
    # ======================================================

    external_context = ""
    external_sources = []

    # ------------------------------------------------------
    # Uploaded Document
    # ------------------------------------------------------

    if document_uploaded:

        print(
            "\nUploaded document mode active."
        )

        print(
            "Tavily and DuckDuckGo will NOT be called."
        )

    # ------------------------------------------------------
    # Subject Knowledge Base + Web Fallback
    # ------------------------------------------------------

    elif use_external:

        print(
            "\n========== WEB FALLBACK ==========\n"
        )

        # ==================================================
        # Tavily
        # ==================================================

        try:

            tavily_result = search_tavily(
                question
            )

            if isinstance(
                tavily_result,
                tuple,
            ):

                tavily_context, tavily_sources = (
                    tavily_result
                )

            else:

                tavily_context = tavily_result
                tavily_sources = []

            if tavily_context:

                external_context += (
                    tavily_context
                )

            if tavily_sources:

                external_sources.extend(
                    tavily_sources
                )

        except Exception as e:

            print(
                "Tavily Error :",
                e,
            )

        # ==================================================
        # DuckDuckGo
        # ==================================================

        try:

            duck_result = search_duckduckgo(
                question
            )

            if isinstance(
                duck_result,
                tuple,
            ):

                duck_context, duck_sources = (
                    duck_result
                )

            else:

                duck_context = duck_result
                duck_sources = []

            if duck_context:

                if external_context.strip():

                    external_context += "\n\n"

                external_context += (
                    duck_context
                )

            if duck_sources:

                external_sources.extend(
                    duck_sources
                )

        except Exception as e:

            print(
                "DuckDuckGo Error :",
                e,
            )

        # --------------------------------------------------
        # Determine Final Source
        # --------------------------------------------------

        if external_context.strip():

            source = "web"

            print(
                "\nExternal information successfully retrieved."
            )

        else:

            print(
                "\nNo external information was retrieved."
            )

    # ------------------------------------------------------
    # Local Knowledge Base Sufficient
    # ------------------------------------------------------

    else:

        print(
            "\nLocal KB sufficient."
        )

        print(
            "Web fallback not required."
        )

    # ======================================================
    # STEP 4 : EDUCATIONAL RESOURCES
    # ======================================================

    youtube = []
    khan = []
    nptel = []

    question_lower = question.lower()

    # ======================================================
    # YouTube
    # ======================================================

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

        print(
            "\nSearching YouTube...\n"
        )

        try:

            youtube = search_youtube(
                question,
                max_results=3,
            )

        except Exception as e:

            print(
                "YouTube Error :",
                e,
            )

    # ======================================================
    # Course Resources
    # ======================================================

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

        # --------------------------------------------------
        # Khan Academy
        # --------------------------------------------------

        print(
            "\nSearching Khan Academy...\n"
        )

        try:

            khan = search_khan(
                question
            )

        except Exception as e:

            print(
                "Khan Academy Error :",
                e,
            )

        # --------------------------------------------------
        # NPTEL
        # --------------------------------------------------

        print(
            "\nSearching NPTEL...\n"
        )

        try:

            nptel = search_nptel(
                question
            )

        except Exception as e:

            print(
                "NPTEL Error :",
                e,
            )

    # ======================================================
    # STEP 5 : REMOVE DUPLICATE SOURCES
    # ======================================================

    external_sources = list(
        dict.fromkeys(
            source_item
            for source_item in external_sources
            if source_item
        )
    )

    # ======================================================
    # STEP 6 : FINAL RESPONSE
    # ======================================================

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