import os

from dotenv import load_dotenv
from google import genai

from app.core.config import settings

load_dotenv()

# ==========================================================
# Gemini Client
# ==========================================================

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# ==========================================================
# Validate Subject
# ==========================================================

def validate_document_subject(
    selected_subject: str,
    document_text: str,
) -> tuple[bool, str]:
    """
    Validates whether the uploaded document belongs to the
    selected subject.

    Returns:
        (True, detected_subject)
        (False, detected_subject)
    """

    # Only the first part of the document is needed
    sample = document_text[:5000]

    prompt = f"""
You are an academic document classifier.

Selected Subject:
{selected_subject}

Document Content:
{sample}

Task:

Determine whether this document primarily belongs to the selected subject.

Examples:

Selected Subject:
Operating System

Document:
Process Scheduling
Deadlock
Memory Management

Answer:
YES
Detected Subject:
Operating System

----------------------------------------

Selected Subject:
Object Oriented Programming

Document:
CPU Scheduling
Semaphores
Paging

Answer:
NO
Detected Subject:
Operating System

----------------------------------------

Rules:

1. Consider the overall topic.
2. Ignore a few unrelated words.
3. Answer ONLY in this format.

YES
Detected Subject: <subject>

OR

NO
Detected Subject: <subject>

Do not explain.
"""

    response = client.models.generate_content(
        model=settings.LLM_MODEL,
        contents=prompt,
    )

    text = response.text.strip()

    print("\n========== SUBJECT VALIDATION ==========")
    print(text)
    print("========================================\n")

    lines = text.splitlines()

    if not lines:
        return False, "Unknown"

    decision = lines[0].strip().upper()

    detected = "Unknown"

    for line in lines:

        if line.lower().startswith("detected subject"):

            detected = line.split(":", 1)[1].strip()
            break

    return decision == "YES", detected