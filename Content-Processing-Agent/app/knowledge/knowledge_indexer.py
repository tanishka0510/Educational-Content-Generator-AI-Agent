from pathlib import Path
import shutil

from dotenv import load_dotenv
load_dotenv()

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from app.knowledge.knowledge_loader import load_documents


# ==========================================================
# Paths
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

KNOWLEDGE_PATH = BASE_DIR / "knowledge_base"

CHROMA_ROOT = BASE_DIR / "chroma_db"

print("Knowledge Base :", KNOWLEDGE_PATH)
print("Chroma Root    :", CHROMA_ROOT)

# ==========================================================
# Embedding Model
# ==========================================================

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# ==========================================================
# Text Splitter
# ==========================================================

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)


# ==========================================================
# Build Subject Database
# ==========================================================

def build_subject_database(subject_folder: Path):

    subject_name = subject_folder.name

    print("\n" + "=" * 70)
    print(f"INDEXING SUBJECT : {subject_name}")
    print("=" * 70)

    docs = load_documents(subject_folder)

    print(f"Loaded Documents : {len(docs)}")

    if len(docs) == 0:
        print("No documents found.")
        return

    chunks = splitter.split_documents(docs)

    print(f"Created Chunks : {len(chunks)}")

    subject_db = CHROMA_ROOT / subject_name

    if subject_db.exists():
        print("Removing old database...")
        shutil.rmtree(subject_db)

    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(subject_db)
    )

    print(f"Database Saved : {subject_db}")
    print(f"Collection Count : {vectordb._collection.count()}")


# ==========================================================
# Build All Databases
# ==========================================================

def build_vector_database():

    if not KNOWLEDGE_PATH.exists():
        print("Knowledge Base folder not found.")
        return

    CHROMA_ROOT.mkdir(exist_ok=True)

    subject_folders = [
        folder
        for folder in KNOWLEDGE_PATH.iterdir()
        if folder.is_dir()
    ]

    print(f"\nFound {len(subject_folders)} subjects.\n")

    for folder in subject_folders:
        build_subject_database(folder)

    print("\n" + "=" * 70)
    print("ALL SUBJECT DATABASES CREATED SUCCESSFULLY")
    print("=" * 70)


# ==========================================================
# Run
# ==========================================================

if __name__ == "__main__":
    build_vector_database()