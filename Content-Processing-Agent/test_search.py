from app.knowledge.knowledge_service import search_knowledge

query = "What is Process Scheduling?"

docs = search_knowledge(query, k=5)

print(f"\nFound {len(docs)} documents\n")

for i, doc in enumerate(docs):

    print("=" * 60)
    print("Result", i + 1)
    print("=" * 60)

    print("SOURCE:")
    print(doc.metadata.get("source"))

    print("\nCONTENT:")
    print(doc.page_content[:700])