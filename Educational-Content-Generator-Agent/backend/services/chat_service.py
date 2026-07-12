from services.gemini_service import ask_gemini


def chat_with_document(document_text, question):
    prompt = f"""
You are an AI tutor.

Answer the student's question ONLY using the information given in the document.

If the answer is not present in the document, reply:

"I couldn't find the answer in the uploaded document."

Document:

{document_text}


Student Question:

{question}
"""

    answer = ask_gemini(prompt)

    return answer