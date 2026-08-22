from pathlib import Path

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# ==========================================================
# Base Paths
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CHROMA_ROOT = BASE_DIR / "chroma_db"

# ==========================================================
# Embedding Model (load once)
# ==========================================================

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# ==========================================================
# Cache loaded vector stores
# ==========================================================

_vectorstores = {}


# ==========================================================
# Get Subject Vector Database
# ==========================================================

def get_vectorstore(subject: str):
    """
    Returns the Chroma vector database for the selected subject.
    Example:
        subject = "OS"
        subject = "DBMS"
        subject = "DATA STRUCTURE"
    """

    if subject in _vectorstores:
        return _vectorstores[subject]

    subject_path = CHROMA_ROOT / subject

    if not subject_path.exists():
        raise FileNotFoundError(
            f"Subject database not found: {subject}"
        )

    vectordb = Chroma(
        persist_directory=str(subject_path),
        embedding_function=embeddings
    )

    print(f"\nLoaded Subject Database : {subject}")
    print("Collection Count :", vectordb._collection.count())

    _vectorstores[subject] = vectordb

    return vectordb