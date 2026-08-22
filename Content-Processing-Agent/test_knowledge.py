from knowledge.knowledge_service import search_knowledge

query = "What is Data Structure?"

docs = search_knowledge(query)

print("=" * 50)

for i, doc in enumerate(docs, start=1):

    print(f"\nResult {i}\n")

    print(doc.page_content[:800])