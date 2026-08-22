from app.knowledge.knowledge_service import search_knowledge
from app.services.llm_service import generate_answer

query = "Explain Data Structure."

docs = search_knowledge(query, k=3)

context = "\n\n".join([doc.page_content for doc in docs])

prompt = f"""
You are an educational AI assistant.

Use ONLY the information below to answer the student's question.

Context:
{context}

Question:
{query}

Answer:
"""

answer = generate_answer(context,prompt)

print("\n========== ANSWER ==========\n")
print(answer)