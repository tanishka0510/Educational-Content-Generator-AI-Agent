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
# Chroma Database Path
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CHROMA_PATH = BASE_DIR / "chroma_db"

print("CHROMA PATH =", CHROMA_PATH.resolve())

# ==========================================================
# Load Existing Vector Database
# ==========================================================

vectordb = Chroma(
    persist_directory=str(CHROMA_PATH),
    embedding_function=embeddings
)

print("Collection Name:", vectordb._collection.name)
print("Collection Count:", vectordb._collection.count())

# ==========================================================
# Search Knowledge Base
# ==========================================================

def search_knowledge(query: str, k: int = 5):
    """
    Returns the top-k most relevant documents.
    The LLM will decide whether they actually answer the question.
    """

    docs = vectordb.similarity_search(
        query=query,
        k=k
    )

    print("\n========== SEARCH RESULTS ==========\n")

    for i, doc in enumerate(docs, start=1):
        print(f"{i}.")
        print(doc.metadata.get("source", "Unknown"))
        print("-" * 60)

    print(f"\nRetrieved Documents: {len(docs)}")
    print("====================================\n")

    return docs