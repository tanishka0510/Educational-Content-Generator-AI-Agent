"""
RAG Service

Coordinates retrieval and LLM generation.

Responsibilities:

1. Call the Hybrid Retriever.
2. Build context from retrieved documents and web results.
3. Pass query metadata to the LLM.
4. Generate the final educational answer.
5. Return sources and educational resources.

The Hybrid Retriever is responsible for:
    - Query analysis
    - Local knowledge-base retrieval
    - Uploaded-document retrieval
    - Web fallback
    - YouTube search
    - Khan Academy search
    - NPTEL search
"""


from app.services.hybrid_retriever import hybrid_search

from app.services.llm_service import (
    generate_answer,
    process_content,
)


# ==========================================================
# Helper: Build Context
# ==========================================================

def _build_context(
    documents,
    external_context: str = "",
):
    """
    Build the final context that will be provided to the LLM.

    Context can contain:

    1. Retrieved local/uploaded-document chunks.
    2. External web-search results.
    """

    context_parts = []

    # ------------------------------------------------------
    # Retrieved Documents
    # ------------------------------------------------------

    if documents:

        for document in documents:

            if hasattr(document, "page_content"):

                content = document.page_content

                if content and content.strip():

                    context_parts.append(
                        content.strip()
                    )

    # ------------------------------------------------------
    # External Web Context
    # ------------------------------------------------------

    if external_context:

        if external_context.strip():

            context_parts.append(
                "========== WEB KNOWLEDGE ==========\n"
                + external_context.strip()
            )

    # ------------------------------------------------------
    # Final Context
    # ------------------------------------------------------

    return "\n\n".join(context_parts)


# ==========================================================
# Helper: Collect Sources
# ==========================================================

def _collect_sources(
    documents,
    external_sources,
):
    """
    Collect and remove duplicate source names.
    """

    sources = []

    # ------------------------------------------------------
    # Local / Uploaded Document Sources
    # ------------------------------------------------------

    if documents:

        for document in documents:

            if not hasattr(document, "metadata"):
                continue

            metadata = document.metadata or {}

            source_name = metadata.get(
                "source",
                "",
            )

            if source_name:

                sources.append(
                    source_name
                )

    # ------------------------------------------------------
    # External Sources
    # ------------------------------------------------------

    if external_sources:

        sources.extend(
            external_sources
        )

    # ------------------------------------------------------
    # Remove Empty / Duplicate Sources
    # ------------------------------------------------------

    sources = list(
        dict.fromkeys(
            source
            for source in sources
            if source
        )
    )

    return sources


# ==========================================================
# Question Answering / Chat
# ==========================================================

def ask_question(
    subject: str,
    question: str,
    document_uploaded: bool = False,
):
    """
    Retrieve relevant information and generate
    the final educational answer.

    When document_uploaded=True:

        Only the uploaded document is searched.

    When document_uploaded=False:

        The selected subject knowledge base is searched
        first, followed by external search when required.

    The QueryAnalyzer metadata returned by hybrid_search()
    is passed to the LLM so that the response can respect
    the user's requested:

        - topic
        - intent
        - response style
        - difficulty
    """

    # ======================================================
    # STEP 1: Hybrid Retrieval
    # ======================================================

    data = hybrid_search(
        subject=subject,
        question=question,
        document_uploaded=document_uploaded,
    )

    # ======================================================
    # STEP 2: Extract Retrieval Data
    # ======================================================

    documents = data.get(
        "documents",
        [],
    )

    score = data.get(
        "score",
    )

    source = data.get(
        "source",
        "unknown",
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

    # ======================================================
    # STEP 3: Query Analyzer Metadata
    # ======================================================

    topic = data.get(
        "topic",
    )

    intent = data.get(
        "intent",
        "general",
    )

    response_style = data.get(
        "response_style",
        "normal",
    )

    difficulty = data.get(
        "difficulty",
        "Medium",
    )

    unit = data.get(
        "unit",
    )

    print(
        "\n========== RAG QUERY METADATA =========="
    )

    print(
        "Topic          :",
        topic,
    )

    print(
        "Intent         :",
        intent,
    )

    print(
        "Response Style :",
        response_style,
    )

    print(
        "Difficulty     :",
        difficulty,
    )

    print(
        "Unit           :",
        unit,
    )

    print(
        "========================================\n"
    )

    # ======================================================
    # STEP 4: Build Context
    # ======================================================

    context = _build_context(
        documents=documents,
        external_context=external_context,
    )

    # ======================================================
    # STEP 5: Nothing Retrieved
    # ======================================================

    if not context.strip():

        if source == "uploaded_document":

            return {
                "question": question,

                "answer": (
                    "The uploaded document does not "
                    "contain enough information."
                ),

                "topic": topic,
                "intent": intent,
                "response_style": response_style,
                "difficulty": difficulty,
                "unit": unit,

                "sources": [],

                "retrieval_score": score,
            }

        return {
            "question": question,

            "answer": (
                "No relevant information could be found."
            ),

            "topic": topic,
            "intent": intent,
            "response_style": response_style,
            "difficulty": difficulty,
            "unit": unit,

            "sources": [],

            "retrieval_score": score,
        }

    # ======================================================
    # STEP 6: Generate Answer
    # ======================================================

    answer = generate_answer(
        context=context,
        question=question,
        source=source,

        # Query Analyzer metadata
        intent=intent,
        response_style=response_style,
        difficulty=difficulty,
        topic=topic,
    )

    # ======================================================
    # STEP 7: Collect Sources
    # ======================================================

    sources = _collect_sources(
        documents=documents,
        external_sources=external_sources,
    )

    # ======================================================
    # STEP 8: Build Final Response
    # ======================================================

    response = {

        "question": question,
        "answer": answer,

        # ----------------------------------------------
        # Query metadata
        # ----------------------------------------------

        "topic": topic,
        "intent": intent,
        "response_style": response_style,
        "difficulty": difficulty,
        "unit": unit,

        # ----------------------------------------------
        # Retrieval information
        # ----------------------------------------------

        "source": source,
        "sources": sources,
        "retrieval_score": score,
    }

    # ======================================================
    # STEP 9: Optional Educational Resources
    # ======================================================

    if videos:
        response["videos"] = videos
    if khan:
        response["khan"] = khan
    if nptel:
        response["nptel"] = nptel

    # ======================================================
    # STEP 10: Debug Output
    # ======================================================

    print(
        "\n========== RAG RESPONSE =========="
    )
    print(
        "Question       :",
        question,
    )
    print(
        "Source         :",
        source,
    )
    print(
        "Topic          :",
        topic,
    )
    print(
        "Intent         :",
        intent,
    )
    print(
        "Response Style :",
        response_style,
    )
    print(
        "Difficulty     :",
        difficulty,
    )
    print(
        "Documents      :",
        len(documents),
    )
    print(
        "Sources        :",
        len(sources),
    )
    print(
        "Videos         :",
        len(videos),
    )
    print("=================================\n")

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
    Retrieve information and generate structured
    educational content.

    This function is intended for structured outputs
    such as:

        - summaries
        - learning objectives
        - keywords
        - concepts

    The current process_content() function returns
    structured JSON.
    """

    # ======================================================
    # STEP 1: Hybrid Retrieval
    # ======================================================

    data = hybrid_search(
        subject=subject,
        question=question,
        document_uploaded=document_uploaded,
    )

    # ======================================================
    # STEP 2: Extract Retrieval Data
    # ======================================================

    documents = data.get(
        "documents",
        [],
    )
    score = data.get(
        "score",
    )
    source = data.get(
        "source",
        "unknown",
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

    # ======================================================
    # STEP 3: Query Metadata
    # ======================================================

    topic = data.get(
        "topic",
    )
    intent = data.get(
        "intent",
        "general",
    )
    response_style = data.get(
        "response_style",
        "normal",
    )
    difficulty = data.get(
        "difficulty",
        "Medium",
    )
    unit = data.get(
        "unit",
    )

    # ======================================================
    # STEP 4: Build Context
    # ======================================================

    context = _build_context(
        documents=documents,
        external_context=external_context,
    )

    # ======================================================
    # STEP 5: Nothing Retrieved
    # ======================================================

    if not context.strip():
        if source == "uploaded_document":
            return {
                "summary": (
                    "The uploaded document does not "
                    "contain enough information."
                ),

                "learning_objectives": [],
                "keywords": [],
                "concepts": [],
                "difficulty": "Unknown",
                "topic": topic,
                "intent": intent,
                "response_style": response_style,
                "unit": unit,
                "sources": [],
                "retrieval_score": score,
            }

        return {
            "summary": "No relevant information found.",
            "learning_objectives": [],
            "keywords": [],
            "concepts": [],
            "difficulty": "Unknown",
            "topic": topic,
            "intent": intent,
            "response_style": response_style,
            "unit": unit,
            "sources": [],
            "retrieval_score": score,
        }

    # ======================================================
    # STEP 6: Generate Structured Content
    # ======================================================

    result = process_content(
        context=context,
        question=question,
        source=source,
        intent=intent,
        response_style=response_style,
        difficulty=difficulty,
        topic=topic,
    )
    
    print("\n========== PROCESS QUESTION RESULT ==========")
    print("Result type :", type(result)) 
    print("Result keys :", result.keys()) 
    print("Code present:", "code" in result)
    print("Code value  :", result.get("code"))
    print("=============================================\n")

    # ======================================================
    # STEP 7: Add Query Metadata
    # ======================================================

    result["topic"] = topic
    result["intent"] = intent
    result["response_style"] = response_style
    result["unit"] = unit
    # ======================================================
    # STEP 8: Collect Sources
    # ======================================================
    sources = _collect_sources(
        documents=documents,
        external_sources=external_sources,
    )
    result["sources"] = sources
    result["retrieval_score"] = score
    # ======================================================
    # STEP 9: Optional Educational Resources
    # ======================================================
    if videos:
        result["videos"] = videos
    if khan:
        result["khan"] = khan
    if nptel:
        result["nptel"] = nptel
    # ======================================================
    # STEP 10: Return
    # ======================================================
    return result