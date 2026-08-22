from pathlib import Path
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

BASE_DIR = Path(__file__).resolve().parent
DB = BASE_DIR / "chroma_db" / "OS"

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectordb = Chroma(
    persist_directory=str(DB),
    embedding_function=embeddings
)

docs = vectordb.similarity_search(
    "operating system",
    k=20
)

print("\n============= METADATA =============\n")

for i, doc in enumerate(docs):

    print(f"Document {i+1}")
    print(doc.metadata)
    print("-"*60)