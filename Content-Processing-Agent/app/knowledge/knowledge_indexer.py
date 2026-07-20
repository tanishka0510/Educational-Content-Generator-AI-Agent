from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from knowledge_loader import load_documents


BASE_DIR = Path(__file__).resolve().parent.parent.parent
CHROMA_PATH = str(BASE_DIR / "chroma_db")
print("CHROMA PATH =", CHROMA_PATH)

def build_vector_database():

    print("Loading documents...")
    docs = load_documents()

    print(f"Loaded {len(docs)} documents")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    print("Splitting documents...")

    chunks = splitter.split_documents(docs)

    print(f"Created {len(chunks)} chunks")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PATH
    )

    print("\nKnowledge Base Indexed Successfully.")
    print(f"Database stored at : {CHROMA_PATH}")
    print("Collection Count:", vectordb._collection.count())


if __name__ == "__main__":
    build_vector_database()