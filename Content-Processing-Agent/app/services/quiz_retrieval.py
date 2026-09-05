"""
Quiz Retrieval Service

Responsible for retrieving educational content specifically
for quiz generation.

Retrieval hierarchy:

    Subject
        ↓
    Unit / Chapter
        ↓
    Topic
        ↓
    Difficulty

Modes:

1. Uploaded Document Mode
   - Searches only the uploaded document.
   - No web search.
   - No subject knowledge base.

2. Subject Knowledge Base Mode
   - Searches the selected subject knowledge base.
   - Uses unit/topic information when available.
   - Does not use external web search here.

The retrieved context is returned to the Educational Content
Generator, where the LLM will generate the actual quiz.
"""

from typing import Optional

from app.knowledge.knowledge_service import (
    search_knowledge,
    search_uploaded_document,
)


# ============================================================
# QUIZ RETRIEVAL THRESHOLDS
# ============================================================

QUIZ_UPLOADED_DB_THRESHOLD = 0.60
QUIZ_SUBJECT_DB_THRESHOLD = 0.60


# ============================================================
# BUILD QUIZ RETRIEVAL QUERY
# ============================================================

def build_quiz_retrieval_query(
    subject: Optional[str],
    unit: Optional[str],
    topic: Optional[str],
    difficulty: str,
) -> str:
    """
    Build a focused retrieval query for quiz generation.

    Priority:

        topic + unit + subject

    Example:

        Subject    : OOP
        Unit       : Unit 3
        Topic      : Arrays
        Difficulty : Medium

    Query:

        OOP Unit 3 Arrays
    """

    parts = []

    if subject:
        parts.append(subject.strip())

    if unit:
        parts.append(unit.strip())

    if topic:
        parts.append(topic.strip())

    query = " ".join(
        part for part in parts
        if part
    )

    # --------------------------------------------------------
    # Fallback
    # --------------------------------------------------------

    if not query:
        query = subject or "educational content"

    return query


# ============================================================
# FORMAT RETRIEVED DOCUMENTS
# ============================================================

def format_documents(documents) -> str:
    """
    Convert retrieved documents into a single context string
    that can be sent to the quiz-generation LLM.
    """

    if not documents:
        return ""

    context_parts = []

    for index, document in enumerate(documents, start=1):

        # ----------------------------------------------------
        # LangChain Document
        # ----------------------------------------------------

        if hasattr(document, "page_content"):

            content = document.page_content

            metadata = getattr(
                document,
                "metadata",
                {},
            )

        # ----------------------------------------------------
        # Dictionary
        # ----------------------------------------------------

        elif isinstance(document, dict):

            content = (
                document.get("content")
                or document.get("text")
                or ""
            )

            metadata = document.get(
                "metadata",
                {},
            )

        # ----------------------------------------------------
        # String
        # ----------------------------------------------------

        else:

            content = str(document)

            metadata = {}

        if not content:
            continue

        filename = metadata.get(
            "filename",
            metadata.get("source", "Unknown"),
        )

        page = metadata.get(
            "page",
            metadata.get("page_number", "Unknown"),
        )

        context_parts.append(
            f"""
--- Retrieved Content {index} ---
Source   : {filename}
Page     : {page}

{content}
"""
        )

    return "\n".join(context_parts)


# ============================================================
# QUIZ RETRIEVAL
# ============================================================

def retrieve_quiz_context(
    subject: Optional[str],
    unit: Optional[str] = None,
    topic: Optional[str] = None,
    difficulty: str = "medium",
    document_uploaded: bool = False,
    number_of_questions: int = 5,
):
    """
    Retrieve content that will be used for quiz generation.

    Parameters
    ----------
    subject:
        Selected academic subject.

    unit:
        Selected unit/chapter.

    topic:
        Selected topic.

    difficulty:
        easy / medium / hard.

    document_uploaded:
        Whether an uploaded document should be used.

    number_of_questions:
        Number of questions requested.

    Returns
    -------
    dict
        Retrieved context and metadata.
    """

    print(
        "\n=========================================="
    )

    print(
        "             QUIZ RETRIEVAL"
    )

    print(
        "=========================================="
    )

    print(
        "Subject             :",
        subject,
    )

    print(
        "Unit                :",
        unit,
    )

    print(
        "Topic               :",
        topic,
    )

    print(
        "Difficulty          :",
        difficulty,
    )

    print(
        "Questions           :",
        number_of_questions,
    )

    print(
        "Document Uploaded   :",
        document_uploaded,
    )

    # ========================================================
    # VALIDATE DIFFICULTY
    # ========================================================

    difficulty = difficulty.lower().strip()

    if difficulty not in {
        "easy",
        "medium",
        "hard",
    }:

        raise ValueError(
            "Difficulty must be easy, medium, or hard."
        )

    # ========================================================
    # BUILD RETRIEVAL QUERY
    # ========================================================

    retrieval_query = build_quiz_retrieval_query(
        subject=subject,
        unit=unit,
        topic=topic,
        difficulty=difficulty,
    )

    print(
        "\nQuiz Retrieval Query :",
        retrieval_query,
    )

    # ========================================================
    # INITIAL VALUES
    # ========================================================

    documents = []

    score = None

    source = "none"

    context = ""

    # ========================================================
    # UPLOADED DOCUMENT MODE
    # ========================================================

    if document_uploaded:

        print(
            "\n========== QUIZ DOCUMENT MODE =========="
        )

        print(
            "Searching uploaded document..."
        )

        documents, score = search_uploaded_document(
            query=retrieval_query,
            k=8,
        )

        source = "uploaded_document"

        print(
            "Retrieved Documents :",
            len(documents),
        )

        print(
            "Best Distance        :",
            score,
        )

        # ----------------------------------------------------
        # Check relevance
        # ----------------------------------------------------

        if documents:

            if (
                score is None
                or score <= QUIZ_UPLOADED_DB_THRESHOLD
            ):

                context = format_documents(
                    documents
                )

                print(
                    "\nUploaded document content "
                    "is sufficiently relevant."
                )

            else:

                print(
                    "\nUploaded document results "
                    "are below relevance threshold."
                )

                context = ""

        # ----------------------------------------------------
        # IMPORTANT:
        # Never use web fallback here.
        # ----------------------------------------------------

        print(
            "\nExternal search : DISABLED"
        )

        print(
            "Subject KB      : DISABLED"
        )

    # ========================================================
    # SUBJECT KNOWLEDGE BASE MODE
    # ========================================================

    else:

        print(
            "\n========== QUIZ SUBJECT MODE =========="
        )

        if not subject:

            print(
                "\nERROR: No subject provided."
            )

            return {
                "context": "",
                "documents": [],
                "score": None,
                "source": "none",
                "retrieval_query": retrieval_query,
                "subject": subject,
                "unit": unit,
                "topic": topic,
                "difficulty": difficulty,
                "number_of_questions": number_of_questions,
            }

        print(
            "Searching subject knowledge base..."
        )

        documents, score = search_knowledge(
            subject=subject,
            query=retrieval_query,
            k=8,
        )

        print(
            "Retrieved Documents :",
            len(documents),
        )

        print(
            "Best Distance        :",
            score,
        )

        # ----------------------------------------------------
        # Relevance check
        # ----------------------------------------------------

        if documents and (
            score is None
            or score <= QUIZ_SUBJECT_DB_THRESHOLD
        ):

            context = format_documents(
                documents
            )

            source = "knowledge_base"

            print(
                "\nSubject knowledge base "
                "content is sufficiently relevant."
            )

        else:

            print(
                "\nSubject knowledge base did not "
                "return sufficiently relevant content."
            )

            context = ""

            source = "none"

    # ========================================================
    # FINAL RESULT
    # ========================================================

    print(
        "\n========== QUIZ RETRIEVAL COMPLETE =========="
    )

    print(
        "Source              :",
        source,
    )

    print(
        "Documents           :",
        len(documents),
    )

    print(
        "Context Length      :",
        len(context),
    )

    print(
        "Retrieval Query     :",
        retrieval_query,
    )

    print(
        "Difficulty          :",
        difficulty,
    )

    print(
        "=============================================="
    )

    return {

        # ----------------------------------------------------
        # Retrieved information
        # ----------------------------------------------------

        "context": context,

        "documents": documents,

        "score": score,

        "source": source,

        # ----------------------------------------------------
        # Quiz metadata
        # ----------------------------------------------------

        "subject": subject,

        "unit": unit,

        "topic": topic,

        "difficulty": difficulty,

        "number_of_questions": number_of_questions,

        # ----------------------------------------------------
        # Retrieval metadata
        # ----------------------------------------------------

        "retrieval_query": retrieval_query,
    }