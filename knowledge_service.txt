"""
Knowledge Service

Loads Chroma databases and performs semantic search.

Supports:

1. Subject Knowledge Base
2. Uploaded Document Knowledge Base

Important:
    Chroma's similarity_search_with_score() returns a DISTANCE,
    where LOWER values generally indicate better similarity.

This service:
    - Performs semantic retrieval
    - Applies a lightweight lexical relevance check
    - Preserves semantic matches
    - Returns the best distance
    - Avoids incorrectly rejecting valid comparison queries
"""

import re
from pathlib import Path

from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from app.core.config import settings
from app.database.uploaded_chroma_client import UploadedChromaClient


# ==========================================================
# Embedding Model
# ==========================================================

embeddings = HuggingFaceEmbeddings(
    model_name=settings.EMBEDDING_MODEL
)


# ==========================================================
# Directories
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

CHROMA_ROOT = BASE_DIR / "chroma_db"


# ==========================================================
# Stop Words
# ==========================================================

STOP_WORDS = {
    # Question words
    "what",
    "is",
    "are",
    "was",
    "were",
    "how",
    "why",
    "when",
    "where",
    "which",

    # Articles / connectors
    "the",
    "a",
    "an",
    "of",
    "to",
    "in",
    "for",
    "on",
    "and",
    "or",
    "with",
    "from",
    "about",
    "between",
    "into",
    "than",
    "through",

    # Instruction words
    "explain",
    "describe",
    "define",
    "discuss",
    "give",
    "provide",
    "tell",
    "show",
    "compare",
    "comparison",
    "difference",
    "differences",

    # Response style
    "brief",
    "briefly",
    "detail",
    "detailed",
    "deep",
    "deeply",
    "simple",
    "simply",

    # General conversational words
    "me",
    "you",
    "your",
    "please",
    "can",
    "could",
    "would",
    "should",
}
    

# ==========================================================
# Keyword Extraction
# ==========================================================

def extract_keywords(query: str):
    """
    Extract meaningful technical words from a retrieval query.

    Example:

        "primary storage secondary storage"

    becomes:

        [
            "primary",
            "storage",
            "secondary"
        ]
    """

    if not query:
        return []

    words = re.findall(
        r"[A-Za-z0-9]+(?:[-+.#][A-Za-z0-9]+)*",
        query.lower(),
    )

    keywords = [
        word
        for word in words
        if word not in STOP_WORDS
        and len(word) > 1
    ]

    # Remove duplicates while preserving order
    return list(dict.fromkeys(keywords))


# ==========================================================
# Normalize Text
# ==========================================================

def normalize_text(text: str) -> str:
    """
    Normalize text for lexical matching.
    """

    if not text:
        return ""

    text = text.lower()

    # Normalize common punctuation
    text = re.sub(r"[^a-z0-9+#.\-\s]", " ", text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ==========================================================
# Lexical Relevance
# ==========================================================

def calculate_keyword_match(
    doc: Document,
    keywords: list[str],
):
    """
    Calculate how many retrieval keywords occur in a document.

    This is NOT used as the primary semantic ranking.

    It is only an additional signal to prevent obviously
    unrelated chunks from being returned.
    """

    if not keywords:
        return 0

    text = normalize_text(doc.page_content)

    matched = 0

    for keyword in keywords:

        if keyword in text:
            matched += 1

    return matched


# ==========================================================
# Relevance Filter
# ==========================================================

def filter_relevant_documents(
    results,
    query,
    minimum_keyword_matches: int = 1,
):
    """
    Apply a lightweight lexical relevance filter.

    IMPORTANT:

    Semantic similarity remains the PRIMARY retrieval mechanism.

    The lexical check is only used to remove obviously unrelated
    chunks when the retrieval query contains meaningful keywords.

    If no keywords are available, semantic results are preserved.

    For multi-concept questions such as:

        "primary storage secondary storage"

    a chunk mentioning either concept can survive the filter.
    """

    keywords = extract_keywords(query)

    # ------------------------------------------------------
    # No usable keywords
    # ------------------------------------------------------

    if not keywords:
        return results

    filtered = []

    for doc, score in results:

        matched = calculate_keyword_match(
            doc,
            keywords,
        )

        # --------------------------------------------------
        # Keep semantically retrieved chunks that contain at
        # least one meaningful retrieval keyword.
        # --------------------------------------------------

        if matched >= minimum_keyword_matches:

            filtered.append(
                (
                    doc,
                    score,
                )
            )

    return filtered


# ==========================================================
# Sort Results By Semantic Distance
# ==========================================================

def sort_by_distance(results):
    """
    Chroma similarity_search_with_score returns distance.

    Lower distance = better semantic match.

    Always sort explicitly so the first result is guaranteed
    to be the best result.
    """

    return sorted(
        results,
        key=lambda item: item[1],
    )


# ==========================================================
# Subject Database
# ==========================================================

def load_subject_database(subject: str):

    if not subject:
        raise ValueError(
            "Subject is required for subject knowledge-base search."
        )

    subject_db = CHROMA_ROOT / subject

    if not subject_db.exists():

        raise FileNotFoundError(
            f"Database for subject '{subject}' not found."
        )

    vectordb = Chroma(
        persist_directory=str(subject_db),
        embedding_function=embeddings,
    )

    print(
        "Loading DB from:",
        subject_db.resolve(),
    )

    print(
        "Collection Count:",
        vectordb._collection.count(),
    )

    return vectordb


# ==========================================================
# Subject Search
# ==========================================================

def search_knowledge(
    subject: str,
    query: str,
    unit: str | None = None,
    topic: str | None = None,
    k: int = 8,
):
    """
    Search the selected subject knowledge base.

    Parameters
    ----------
    subject:
        Subject name such as OS, DBMS, OOP, CN.

    query:
        Clean retrieval query generated by QueryAnalyzer.

    unit:
        Optional detected unit.

    topic:
        Optional detected topic.

    k:
        Number of semantic candidates to retrieve.

    Returns
    -------
    documents, best_score
    """

    print("\n==========================================")
    print("        SUBJECT KNOWLEDGE SEARCH")
    print("==========================================")

    print("Subject :", subject)
    print("Query   :", query)
    print("Unit    :", unit)
    print("Topic   :", topic)

    # ------------------------------------------------------
    # Load database
    # ------------------------------------------------------

    vectordb = load_subject_database(subject)

    # ------------------------------------------------------
    # Semantic search
    # ------------------------------------------------------

    results = vectordb.similarity_search_with_score(
        query=query,
        k=k,
    )

    print(
        "\nSemantic candidates retrieved :",
        len(results),
    )

    # ------------------------------------------------------
    # Sort by semantic distance
    # ------------------------------------------------------

    results = sort_by_distance(results)

    # ------------------------------------------------------
    # Lightweight lexical filtering
    # ------------------------------------------------------

    filtered_results = filter_relevant_documents(
        results,
        query,
        minimum_keyword_matches=1,
    )

    # ------------------------------------------------------
    # If lexical filtering removed everything,
    # preserve semantic results instead of incorrectly
    # declaring the database empty.
    # ------------------------------------------------------

    if not filtered_results:

        print(
            "\nLexical filter removed all candidates."
        )

        print(
            "Preserving semantic search results."
        )

        filtered_results = results

    # ------------------------------------------------------
    # No semantic results
    # ------------------------------------------------------

    if not filtered_results:

        print(
            "\nNo relevant subject chunks found."
        )

        return [], None

    # ------------------------------------------------------
    # Sort again after filtering
    # ------------------------------------------------------

    filtered_results = sort_by_distance(
        filtered_results
    )

    documents = []

    best_score = filtered_results[0][1]

    # ------------------------------------------------------
    # Debug output
    # ------------------------------------------------------

    print("\n========== SUBJECT SEARCH ==========\n")

    for index, (doc, score) in enumerate(
        filtered_results,
        start=1,
    ):

        documents.append(doc)

        print(
            f"\n========== Result {index} =========="
        )

        print(
            "Distance :",
            round(score, 4),
        )

        print(
            "Page :",
            doc.metadata.get("page"),
        )

        print(
            "Unit :",
            doc.metadata.get("unit"),
        )

        print(
            "Topic :",
            doc.metadata.get("topic"),
        )

        print(
            "Filename :",
            doc.metadata.get("filename"),
        )

        print(
            "Content:"
        )

        print(
            doc.page_content[:1000]
        )

        print(
            "=" * 70
        )

    print(
        "\nBest Semantic Distance :",
        round(best_score, 4),
    )

    return documents, best_score


# ==========================================================
# Uploaded Document Search
# ==========================================================

def search_uploaded_document(
    query: str,
    k: int = 8,
):
    """
    Search only the uploaded document Chroma collection.

    No subject knowledge base or web fallback is handled here.

    The hybrid retriever decides whether external sources are
    allowed.
    """

    collection = UploadedChromaClient.get_collection()

    total_docs = collection.count()

    print(
        "\n========== UPLOADED DATABASE =========="
    )

    print(
        "Collection :",
        collection.name,
    )

    print(
        "Total Documents :",
        total_docs,
    )

    print(
        "=======================================\n"
    )

    # ------------------------------------------------------
    # Empty database
    # ------------------------------------------------------

    if total_docs == 0:

        print(
            "Uploaded database is empty."
        )

        return [], None

    # ------------------------------------------------------
    # Create query embedding
    # ------------------------------------------------------

    query_embedding = embeddings.embed_query(
        query
    )

    # ------------------------------------------------------
    # Chroma semantic search
    # ------------------------------------------------------

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
    )

    if (
        not results.get("ids")
        or len(results["ids"][0]) == 0
    ):

        print(
            "No uploaded document results found."
        )

        return [], None

    ids = results["ids"][0]

    docs = results["documents"][0]

    metas = results["metadatas"][0]

    distances = results["distances"][0]

    raw_results = []

    # ------------------------------------------------------
    # Convert Chroma results to LangChain Documents
    # ------------------------------------------------------

    for i in range(len(ids)):

        metadata = (
            metas[i]
            if metas and metas[i]
            else {}
        )

        raw_results.append(
            (
                Document(
                    page_content=docs[i],
                    metadata=metadata,
                ),
                distances[i],
            )
        )

    # ------------------------------------------------------
    # Sort by distance
    # ------------------------------------------------------

    raw_results = sort_by_distance(
        raw_results
    )

    # ------------------------------------------------------
    # Lightweight lexical filtering
    # ------------------------------------------------------

    filtered_results = filter_relevant_documents(
        raw_results,
        query,
        minimum_keyword_matches=1,
    )

    # ------------------------------------------------------
    # Preserve semantic results if lexical filtering
    # removes everything.
    # ------------------------------------------------------

    if not filtered_results:

        print(
            "\nLexical filter removed all uploaded candidates."
        )

        print(
            "Preserving semantic search results."
        )

        filtered_results = raw_results

    # ------------------------------------------------------
    # No results
    # ------------------------------------------------------

    if not filtered_results:

        print(
            "\nNo relevant uploaded document chunks."
        )

        return [], None

    # ------------------------------------------------------
    # Sort again
    # ------------------------------------------------------

    filtered_results = sort_by_distance(
        filtered_results
    )

    documents = []

    best_score = filtered_results[0][1]

    print(
        "\nBest Distance :",
        round(best_score, 4),
    )

    print(
        "Retriever model:",
        settings.EMBEDDING_MODEL,
    )

    print(
        "\n========== UPLOADED SEARCH ==========\n"
    )

    # ------------------------------------------------------
    # Debug output
    # ------------------------------------------------------

    for i, (doc, distance) in enumerate(
        filtered_results,
        start=1,
    ):

        documents.append(doc)

        print(
            f"Result {i}"
        )

        print(
            "Filename :",
            doc.metadata.get("filename"),
        )

        print(
            "Page :",
            doc.metadata.get("page"),
        )

        print(
            "Unit :",
            doc.metadata.get("unit"),
        )

        print(
            "Topic :",
            doc.metadata.get("topic"),
        )

        print(
            "Distance :",
            round(distance, 4),
        )

        print(
            "Content :",
            doc.page_content[:500],
        )

        print(
            "-" * 50
        )

    return documents, best_score