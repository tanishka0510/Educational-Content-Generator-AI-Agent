import os
import json
from dotenv import load_dotenv
from google import genai
from app.core.config import settings
load_dotenv()

# =====================================================
# Gemini Client
# =====================================================

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# =====================================================
# General Question Answering (RAG)
# =====================================================

def generate_answer(
    context: str,
    question: str,
    source: str = "knowledge_base",
) -> str:
    """
    Generates an answer using the retrieved context.
    """

    if source == "uploaded_document":

        system_prompt = """
You are an educational assistant.

Answer ONLY from the uploaded document.

Rules:
- Use ONLY the provided context.
- Do NOT use outside knowledge.
- Do NOT invent information.
- If the answer is not present in the uploaded document, reply:
"The uploaded document does not contain enough information."
- Explain in simple educational language.
"""

    else:

        system_prompt = """
You are an educational assistant.

Answer ONLY from the provided study material.

Rules:
- Use ONLY the provided context.
- Do NOT invent facts.
- If the answer is not available in the context, reply:
"The local knowledge base does not contain enough information."
- Explain in simple educational language.
"""

    prompt = f"""
{system_prompt}

Context:
{context}

Question:
{question}

Answer:
"""

    response = client.models.generate_content(
        model=settings.LLM_MODEL,
        contents=prompt,
    )

    return response.text.strip()


# =====================================================
# Educational Content Processing
# =====================================================

def process_content(context: str, question: str):
    """
    Returns structured educational content as JSON.
    """

    prompt = f"""
You are an Educational Content Processing Agent.

Your task is to analyze the provided study material.

Use ONLY the provided context.

Return ONLY valid JSON.

Do NOT write explanations.
Do NOT use markdown.
Do NOT wrap the JSON inside ```json.
Do NOT write anything before or after the JSON.

Return EXACTLY this structure:

{{
    "summary": "",

    "learning_objectives": [
        "",
        "",
        ""
    ],

    "keywords": [
        "",
        "",
        ""
    ],

    "concepts": [
        "",
        "",
        ""
    ],

    "difficulty": "Beginner",

    "sources": []
}}

Context:
{context}

Question:
{question}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    text = response.text.strip()

    print("\n========== GEMINI RAW RESPONSE ==========\n")
    print(text)
    print("\n=========================================\n")

    # -------------------------------------------------
    # Remove Markdown if Gemini returns ```json
    # -------------------------------------------------

    if text.startswith("```"):
        lines = text.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]

        text = "\n".join(lines).strip()

    # -------------------------------------------------
    # Convert JSON safely
    # -------------------------------------------------

    try:
        return json.loads(text)

    except Exception as e:

        print("\nJSON Parse Error")
        print(e)

        return {
            "summary": text,
            "learning_objectives": [],
            "keywords": [],
            "concepts": [],
            "difficulty": "Unknown",
            "sources": []
        }