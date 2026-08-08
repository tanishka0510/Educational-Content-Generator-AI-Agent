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
# Prompt Builder
# =====================================================

def _get_answer_prompt(source: str):

    if source == "uploaded_document":

        return """
You are an educational assistant.

The following context comes from a USER-UPLOADED DOCUMENT.

Rules:
- Use ONLY the uploaded document.
- Do NOT use outside knowledge.
- Do NOT invent facts.
- If the answer is missing, reply exactly:

"The uploaded document does not contain enough information."

- Explain clearly in simple educational language.
- Use headings and bullet points whenever appropriate.
"""

    elif source == "knowledge_base":

        return """
You are an educational assistant.

The following context comes from the LOCAL SUBJECT KNOWLEDGE BASE.

Rules:
- Use ONLY the provided study material.
- Do NOT use outside knowledge.
- Do NOT invent facts.
- If the answer is missing, reply exactly:

"The local knowledge base does not contain enough information."

- Explain clearly in educational language.
- Use headings and bullet points whenever appropriate.
"""

    elif source == "web":

        return """
You are an educational assistant.

The following context comes from TRUSTED WEB SEARCH RESULTS.

Rules:
- Use ONLY the provided web context.
- Do NOT use your own knowledge.
- Merge similar information from multiple sources.
- Explain clearly.
- Use headings and bullet points.
- If the web context does not answer the question, reply exactly:

"The web search results do not contain enough information."
"""

    return """
You are an educational assistant.

Answer ONLY from the provided context.

Do NOT invent information.
"""


# =====================================================
# General Question Answering
# =====================================================

def generate_answer(
    context: str,
    question: str,
    source: str = "knowledge_base",
):

    system_prompt = _get_answer_prompt(source)

    prompt = f"""
{system_prompt}

Context:
{context}

Question:
{question}

Answer:
"""

    try:

        response = client.models.generate_content(
            model=settings.LLM_MODEL,
            contents=prompt,
        )

        if response.text:
            return response.text.strip()

        return "No answer could be generated."

    except Exception as e:

        print("\n========== GEMINI ERROR ==========")
        print(e)
        print("=================================\n")

        return "Unable to generate answer because the language model is unavailable."


# =====================================================
# Educational Content Processing
# =====================================================

def process_content(
    context: str,
    question: str,
    source: str = "knowledge_base",
):

    if source == "uploaded_document":

        system_prompt = """
You are an Educational Content Processing Agent.

Use ONLY the uploaded document.

Do NOT use outside knowledge.
Do NOT invent facts.
"""

    elif source == "web":

        system_prompt = """
You are an Educational Content Processing Agent.

Use ONLY the provided trusted web context.

Merge duplicate information.
Do NOT invent facts.
"""

    else:

        system_prompt = """
You are an Educational Content Processing Agent.

Use ONLY the provided study material.

Do NOT invent facts.
"""

    prompt = f"""
{system_prompt}

Return ONLY valid JSON.

No markdown.

No explanation.

No ```json.

Return EXACTLY this structure.

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

    try:

        response = client.models.generate_content(
            model=settings.LLM_MODEL,
            contents=prompt,
        )

        text = response.text.strip()

        print("\n========== GEMINI RAW RESPONSE ==========\n")
        print(text)
        print("\n=========================================\n")

        # ---------------------------------------------
        # Remove Markdown
        # ---------------------------------------------

        if text.startswith("```"):

            lines = text.splitlines()

            if lines[0].startswith("```"):
                lines = lines[1:]

            if lines[-1].startswith("```"):
                lines = lines[:-1]

            text = "\n".join(lines).strip()

        return json.loads(text)

    except Exception as e:

        print("\n========== JSON PARSE ERROR ==========")
        print(e)
        print("======================================\n")

        return {
            "summary": text if "text" in locals() else "",
            "learning_objectives": [],
            "keywords": [],
            "concepts": [],
            "difficulty": "Unknown",
            "sources": [],
        }