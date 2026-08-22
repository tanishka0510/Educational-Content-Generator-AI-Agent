"""
Hybrid Retriever

Retrieval flow:

1. Query Analysis
   - Extract topic
   - Extract keywords
   - Detect intent
   - Detect response style
   - Detect difficulty
   - Detect unit

2. Uploaded document mode:
   - Search uploaded document only.
   - Never use external web search.
   - Never use subject knowledge base.
   - If information is not found, return empty context.

3. Subject knowledge-base mode:
   - Search selected subject knowledge base.
   - Evaluate whether the local result is sufficiently relevant.
   - If local information is missing or insufficient,
     automatically use web fallback.

4. Educational resources:
   - YouTube is searched when explicitly requested.
   - Khan Academy / NPTEL are searched for course/study requests.

Important:
The retrieval query is the cleaned topic/keywords, NOT the raw
instructional question.

Example:

    "Explain normalization in brief"

becomes:

    retrieval_query = "normalization"

while:

    intent = "explanation"
    response_style = "brief"
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
from app.services.query_analyzer import QueryAnalyzer


# ==========================================================
# Retrieval Thresholds
# ==========================================================

UPLOADED_DB_THRESHOLD = settings.UPLOADED_DB_THRESHOLD
SUBJECT_DB_THRESHOLD = settings.SUBJECT_DB_THRESHOLD


# ==========================================================
# Helper: Build Retrieval Query
# ==========================================================

def build_retrieval_query(
    question: str,
    query_info: dict,
) -> str:
    """
    Build the query that will actually be sent to the
    retrieval systems.

    We intentionally DO NOT send the complete user instruction
    to the vector database / web search.

    Example:

        Question:
            Explain normalization in brief

        Query:
            normalization
    """

    topic = query_info.get("topic", "").strip()

    keywords = query_info.get("keywords", [])

    # ------------------------------------------------------
    # Prefer cleaned topic
    # ------------------------------------------------------

    if topic:
        return topic

    # ------------------------------------------------------
    # Fallback to keywords
    # ------------------------------------------------------

    if keywords:
        return " ".join(keywords)

    # ------------------------------------------------------
    # Last fallback
    # ------------------------------------------------------

    return question.strip()


# ==========================================================
# Helper: Determine Whether Local Subject Retrieval
# Is Sufficient
# ==========================================================

def is_subject_retrieval_sufficient(
    documents,
    score,
) -> bool:
    """
    Determine whether the subject knowledge base contains
    sufficiently relevant information.

    Chroma's similarity_search_with_score() returns a distance.

    Lower distance
        = more similar

    Higher distance
        = less similar

    Therefore:

        score <= SUBJECT_DB_THRESHOLD
            -> local result is considered sufficient

        score > SUBJECT_DB_THRESHOLD
            -> web fallback is required

    A completely empty result is always considered insufficient.
    """

    # ------------------------------------------------------
    # No documents
    # ------------------------------------------------------

    if not documents:
        print(
            "\nLocal subject KB returned NO documents."
        )

        return False

    # ------------------------------------------------------
    # No score
    # ------------------------------------------------------

    if score is None:
        print(
            "\nLocal subject KB returned documents "
            "but no similarity score."
        )

        return False

    # ------------------------------------------------------
    # Compare distance with threshold
    # ------------------------------------------------------

    print(
        "\nLocal subject KB best distance :",
        round(score, 4),
    )

    print(
        "Subject DB threshold           :",
        SUBJECT_DB_THRESHOLD,
    )

    if score <= SUBJECT_DB_THRESHOLD:

        print(
            "\nLocal subject KB contains "
            "sufficiently relevant information."
        )

        return True

    print(
        "\nLocal subject KB information "
        "is below the required relevance."
    )

    return False


# ==========================================================
# Helper: External Search
# ==========================================================

def perform_web_fallback(
    retrieval_query: str,
):
    """
    Search Tavily and DuckDuckGo using the cleaned retrieval
    query.

    Returns
    -------
    external_context : str
    external_sources : list
    """

    external_context = ""
    external_sources = []

    print(
        "\n=========================================="
    )
    print(
        "             WEB FALLBACK"
    )
    print(
        "=========================================="
    )

    print(
        "\nWeb Retrieval Query :",
        retrieval_query,
    )

    # ======================================================
    # Tavily
    # ======================================================

    try:

        print(
            "\nSearching Tavily using:",
            retrieval_query,
        )

        tavily_result = search_tavily(
            retrieval_query
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

            external_context = (
                tavily_context
            )

        if tavily_sources:

            external_sources.extend(
                tavily_sources
            )

    except Exception as e:

        print(
            "Tavily Error:",
            e,
        )

    # ======================================================
    # DuckDuckGo
    # ======================================================

    try:

        print(
            "\nSearching DuckDuckGo using:",
            retrieval_query,
        )

        duck_result = search_duckduckgo(
            retrieval_query
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
            "DuckDuckGo Error:",
            e,
        )

    # ======================================================
    # Remove duplicate sources
    # ======================================================

    external_sources = list(
        dict.fromkeys(
            source
            for source in external_sources
            if source
        )
    )

    # ======================================================
    # Final result
    # ======================================================

    if external_context.strip():

        print(
            "\nWeb fallback successfully retrieved information."
        )

    else:

        print(
            "\nWeb fallback did not retrieve information."
        )

    print(
        "External Sources :",
        len(external_sources),
    )

    return (
        external_context,
        external_sources,
    )


# ==========================================================
# Hybrid Search
# ==========================================================

def hybrid_search(
    subject: str | None,
    question: str,
    document_uploaded: bool = False,
    unit: str | None = None,
    topic: str | None = None,
):
    """
    Perform hybrid retrieval for the Educational Content
    Generator Agent.

    Parameters
    ----------
    subject:
        Currently selected subject.

        Example:
            "OOP"
            "OS"
            "DBMS"

        Can be None when working purely with an uploaded
        document.

    question:
        Original user query.

    document_uploaded:
        True:
            Search uploaded document ONLY.

        False:
            Search selected subject knowledge base and use
            external fallback when required.

    Returns
    -------
    dict
        Retrieval results plus query analysis metadata.
    """

    print(
        "\n=========================================="
    )
    print(
        "             HYBRID SEARCH"
    )
    print(
        "=========================================="
    )

    print(
        "Subject             :",
        subject,
    )

    print(
        "Question            :",
        question,
    )

    print(
        "Document Uploaded   :",
        document_uploaded,
    )

    # ======================================================
    # STEP 0 : QUERY ANALYSIS
    # ======================================================

    print(
        "\n========== QUERY ANALYSIS =========="
    )

    query_info = QueryAnalyzer.analyze(
        question
    )

    print(
        "Topic          :",
        query_info["topic"],
    )

    print(
        "Keywords       :",
        query_info["keywords"],
    )

    print(
        "Intent         :",
        query_info["intent"],
    )

    print(
        "Response Style :",
        query_info["response_style"],
    )

    print(
        "Difficulty     :",
        query_info["difficulty"],
    )

    print(
        "Unit           :",
        query_info["unit"],
    )

    # ======================================================
    # STEP 0.1 : BUILD CLEAN RETRIEVAL QUERY
    # ======================================================

    retrieval_query = build_retrieval_query(
        question=question,
        query_info=query_info,
    )

    print(
        "\nRetrieval Query :",
        retrieval_query,
    )

    # ======================================================
    # INITIAL VALUES
    # ======================================================

    documents = []
    score = None

    source = None

    use_external = False

    external_context = ""
    external_sources = []

    youtube = []
    khan = []
    nptel = []

    # ======================================================
    # STEP 1 : LOCAL RETRIEVAL
    # ======================================================

    if document_uploaded:

        # --------------------------------------------------
        # Uploaded Document Mode
        # --------------------------------------------------

        print(
            "\n========== UPLOADED DOCUMENT MODE =========="
        )

        print(
            "Searching uploaded document using:",
            retrieval_query,
        )

        documents, score = search_uploaded_document(
            query=retrieval_query,
            k=5,
        )

        source = "uploaded_document"

    else:

        # --------------------------------------------------
        # Subject Knowledge Base Mode
        # --------------------------------------------------

        print(
            "\n========== SUBJECT KNOWLEDGE BASE MODE =========="
        )

        if not subject:

            print(
                "\nERROR: No subject was provided."
            )

            documents = []
            score = None

        else:

            print(
                "Searching subject database using:",
                retrieval_query,
            )

            documents, score = search_knowledge(
                subject=subject,
                query=retrieval_query,
                k=5,
            )

        source = "knowledge_base"

    print(
        "\nRetrieved Docs :",
        len(documents),
    )

    print(
        "Best Score     :",
        score,
    )

    # ======================================================
    # STEP 2 : EXTERNAL SEARCH DECISION
    # ======================================================

    if document_uploaded:

        # --------------------------------------------------
        # Uploaded document mode NEVER uses web fallback.
        # --------------------------------------------------

        use_external = False

        print(
            "\n========== LOCAL DOCUMENT ONLY =========="
        )

        print(
            "Uploaded document mode is active."
        )

        print(
            "External web search is DISABLED."
        )

        print(
            "Subject knowledge base is DISABLED."
        )

        print(
            "Only the uploaded document will be used."
        )

    else:

        # --------------------------------------------------
        # Subject knowledge base mode
        # --------------------------------------------------

        local_is_sufficient = (
            is_subject_retrieval_sufficient(
                documents=documents,
                score=score,
            )
        )

        if local_is_sufficient:

            use_external = False

            print(
                "\nLocal knowledge is sufficient."
            )

            print(
                "Web fallback will NOT be used."
            )

        else:

            use_external = True

            print(
                "\nLocal knowledge is insufficient."
            )

            print(
                "WEB FALLBACK WILL BE USED."
            )

    # ======================================================
    # STEP 3 : EXTERNAL WEB SEARCH
    # ======================================================

    if document_uploaded:

        print(
            "\nTavily and DuckDuckGo will NOT be called."
        )

    elif use_external:

        (
            external_context,
            external_sources,
        ) = perform_web_fallback(
            retrieval_query=retrieval_query,
        )

        # --------------------------------------------------
        # Determine final source
        # --------------------------------------------------

        if external_context.strip():

            source = "web"

            print(
                "\nFinal retrieval source : WEB"
            )

        elif documents:

            # ------------------------------------------------
            # This is a safety fallback.
            #
            # If the local database returned documents but
            # failed the threshold and web search returned
            # nothing, preserve the local documents rather
            # than throwing away potentially useful context.
            # ------------------------------------------------

            source = "knowledge_base"

            print(
                "\nWeb fallback returned no information."
            )

            print(
                "Using available local knowledge instead."
            )

        else:

            source = "none"

            print(
                "\nNeither local nor web information was found."
            )

    else:

        print(
            "\nLocal knowledge base is sufficient."
        )

        print(
            "Web fallback not required."
        )

    # ======================================================
    # STEP 4 : EDUCATIONAL RESOURCES
    # ======================================================

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
            "\n========== YOUTUBE SEARCH =========="
        )

        try:

            youtube = search_youtube(
                retrieval_query,
                max_results=3,
            )

        except Exception as e:

            print(
                "YouTube Error:",
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
            "\n========== KHAN ACADEMY SEARCH =========="
        )

        try:

            khan = search_khan(
                retrieval_query
            )

        except Exception as e:

            print(
                "Khan Academy Error:",
                e,
            )

        # --------------------------------------------------
        # NPTEL
        # --------------------------------------------------

        print(
            "\n========== NPTEL SEARCH =========="
        )

        try:

            nptel = search_nptel(
                retrieval_query
            )

        except Exception as e:

            print(
                "NPTEL Error:",
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

    print(
        "\n========== RETRIEVAL COMPLETE =========="
    )

    print(
        "Final Source       :",
        source,
    )

    print(
        "Used External      :",
        use_external,
    )

    print(
        "Documents          :",
        len(documents),
    )

    print(
        "External Sources   :",
        len(external_sources),
    )

    print(
        "Videos             :",
        len(youtube),
    )

    print(
        "Khan Resources     :",
        len(khan),
    )

    print(
        "NPTEL Resources    :",
        len(nptel),
    )

    # ======================================================
    # RETURN
    # ======================================================

    return {

        # --------------------------------------------------
        # Retrieval
        # --------------------------------------------------

        "documents": documents,

        "score": score,

        "source": source,

        "used_external": use_external,

        "external_context": external_context,

        "external_sources": external_sources,

        # --------------------------------------------------
        # Educational resources
        # --------------------------------------------------

        "videos": youtube,

        "khan": khan,

        "nptel": nptel,

        # --------------------------------------------------
        # Query analysis
        # --------------------------------------------------

        "query": question,

        "retrieval_query": retrieval_query,

        "topic": query_info["topic"],

        "keywords": query_info["keywords"],

        "intent": query_info["intent"],

        "response_style": query_info["response_style"],

        "difficulty": query_info["difficulty"],

        "unit": query_info["unit"],
    }