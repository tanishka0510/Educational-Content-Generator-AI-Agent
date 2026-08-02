from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

db = Chroma(
    persist_directory="chroma_db/OS",
    embedding_function=embeddings,
)

docs = db.similarity_search_with_score(
    "What is Deadlock",
    k=10
)

for i, (doc, score) in enumerate(docs, 1):
    print("=" * 80)
    print(i)
    print("Distance:", score)
    print(doc.page_content[:1000])