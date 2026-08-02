"""
Knowledge Service

Loads Chroma databases and performs semantic search.

Supports:
1. Subject Knowledge Base
2. Uploaded Document Knowledge Base
"""

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
# Subject Database
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
    
    print("Loading DB from:", subject_db.resolve())
    print("Collection Count:", vectordb._collection.count())

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
    print("\nINSIDE UPDATED KNOWLEDGE SERVICE\n")

    vectordb = load_subject_database(subject)

    # Retrieve top similar chunks
    results = vectordb.similarity_search_with_score(
        query=query,
        k=k,
    )

    documents = []

    best_score = None

    if results:
        best_score = results[0][1]

    print("\n========== SUBJECT SEARCH ==========\n")

    for index, (doc, score) in enumerate(results, start=1):

        documents.append(doc)

        print(f"\n========== Result {index} ==========")
        print("Distance :", round(score, 4))
        print("Page :", doc.metadata.get("page"))
        print("Unit :", doc.metadata.get("unit"))
        print("Topic :", doc.metadata.get("topic"))
        print(doc.page_content[:1000])
        print("=" * 70)

    return documents, best_score


# ==========================================================
# Uploaded Document Search
# ==========================================================

def search_uploaded_document(
    query: str,
    k: int = 8,
):

    collection = UploadedChromaClient.get_collection()

    total_docs = collection.count()

    print("\n========== UPLOADED DATABASE ==========")
    print("Collection :", collection.name)
    print("Total Documents :", total_docs)
    print("=======================================\n")

    if total_docs == 0:
        return [], None

    query_embedding = embeddings.embed_query(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
    )

    if not results["ids"] or len(results["ids"][0]) == 0:
        return [], None

    documents = []

    best_score = None

    ids = results.get("ids", [[]])[0]
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    if distances:
        best_score = distances[0]

    print("Best Distance :", best_score)
    print(settings.EMBEDDING_MODEL)

    print("\n========== UPLOADED SEARCH ==========\n")

    for i in range(len(ids)):

        if not docs[i]:
            continue

        metadata = metas[i] if metas else {}

        doc = Document(
            page_content=docs[i],
            metadata=metadata,
        )

        documents.append(doc)

        print(f"Result {i + 1}")
        print("Filename :", metadata.get("filename"))
        print("Distance :", round(distances[i], 4))
        print("-" * 50)

    return documents, best_score

