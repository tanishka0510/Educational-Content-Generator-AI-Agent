"""
Knowledge Service

Loads Chroma databases and performs semantic search.

Supports:
1. Subject Knowledge Base
2. Uploaded Document Knowledge Base
"""

from pathlib import Path

from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


# ==========================================================
# Embedding Model
# ==========================================================

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# ==========================================================
# Base Directories
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

CHROMA_ROOT = BASE_DIR / "chroma_db"

UPLOADED_DB = BASE_DIR / "uploaded_db"

print("Subject DB Root  :", CHROMA_ROOT.resolve())
print("Uploaded DB Root :", UPLOADED_DB.resolve())


# ==========================================================
# Load Subject Database
# ==========================================================

def load_subject_database(subject: str):

    subject_db = CHROMA_ROOT / subject

    if not subject_db.exists():
        raise FileNotFoundError(
            f"Database for subject '{subject}' not found."
        )

    vectordb = Chroma(
        persist_directory=str(subject_db),
        embedding_function=embeddings,
    )

    print("\n========================================")
    print("Subject     :", subject)
    print("Database    :", subject_db)
    print("Collection  :", vectordb._collection.name)
    print("Documents   :", vectordb._collection.count())
    print("========================================\n")

    return vectordb


# ==========================================================
# Load Uploaded Database
# ==========================================================

def load_uploaded_database():

    if not UPLOADED_DB.exists():
        return None

    vectordb = Chroma(
        persist_directory=str(UPLOADED_DB),
        embedding_function=embeddings,
    )

    if vectordb._collection.count() == 0:
        return None

    print("\n========================================")
    print("Uploaded Document Database")
    print("Database  :", UPLOADED_DB)
    print("Documents :", vectordb._collection.count())
    print("========================================\n")

    return vectordb


# ==========================================================
# Internal Search Function
# ==========================================================

def _search(vectordb, query: str, k: int, title: str):

    if vectordb is None:
        return [], None

    results = vectordb.similarity_search_with_score(
        query=query,
        k=k,
    )

    docs = []

    best_score = None

    if results:
        best_score = results[0][1]

    print(f"\n========== {title} ==========\n")

    for index, (doc, score) in enumerate(results, start=1):

        print(f"Result {index}")
        print("Source   :", doc.metadata.get("source"))
        print("Page     :", doc.metadata.get("page"))
        print("Distance :", round(score, 4))
        print("-" * 60)

        docs.append(doc)

    print(f"\nRetrieved Documents : {len(docs)}")

    if best_score is not None:
        print("Best Score :", round(best_score, 4))
    else:
        print("Best Score : None")

    print("========================================\n")

    return docs, best_score


# ==========================================================
# Search Subject Knowledge Base
# ==========================================================

def search_knowledge(
    subject: str,
    query: str,
    unit: str | None = None,
    topic: str | None = None,
    k: int = 8,
):

    vectordb = load_subject_database(subject)

    return _search(
        vectordb=vectordb,
        query=query,
        k=k,
        title="SUBJECT SEARCH RESULTS",
    )


# ==========================================================
# Search Uploaded Document
# ==========================================================

def search_uploaded_document(
    query: str,
    k: int = 8,
):

    vectordb = load_uploaded_database()

    return _search(
        vectordb=vectordb,
        query=query,
        k=k,
        title="UPLOADED DOCUMENT SEARCH RESULTS",
    )