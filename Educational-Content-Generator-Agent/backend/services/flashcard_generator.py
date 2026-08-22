"""
Flashcard Generator Service

Project: Educational Content Generator AI
Module: Educational Agent
"""

import json
import re
import requests
from typing import Dict, Any

from services.gemini_service import ask_gemini
from prompts.flashcard_prompt import create_flashcard_prompt

# Config to point to Content Processing Agent on port 8001
CONTENT_PROCESSING_AGENT_URL = "http://127.0.0.1:8001"
RETRIEVAL_ENDPOINT = f"{CONTENT_PROCESSING_AGENT_URL}/quiz/retrieve"


def generate_flashcards(
    subject: str,
    unit: str = None,
    topic: str = None,
    difficulty: str = "medium",
    number_of_cards: int = 5,
    document_uploaded: bool = False
) -> Dict[str, Any]:
    """
    Generates educational flashcards from retrieved study material context.
    """
    
    # 1. Fetch relevant content from Content Processing Agent
    payload = {
        "subject": subject,
        "unit": unit,
        "topic": topic,
        "difficulty": difficulty,
        "number_of_questions": number_of_cards,  # Use to resolve chunk quantity
        "document_uploaded": document_uploaded
    }
    
    try:
        response = requests.post(RETRIEVAL_ENDPOINT, json=payload, timeout=60)
        response.raise_for_status()
        retrieval = response.json()
    except Exception as e:
        print(f"Error connecting to Content Processing Agent: {str(e)}")
        # Fallback to local prompt without context if retrieval fails
        retrieval = {"documents": [], "external_context": "No context available."}

    # 2. Extract context
    documents = retrieval.get("documents", [])
    external_context = retrieval.get("external_context", "")
    
    context_parts = []
    for doc in documents:
        if isinstance(doc, dict):
            content = doc.get("page_content") or doc.get("content") or ""
        elif hasattr(doc, "page_content"):
            content = doc.page_content
        else:
            content = str(doc)
            
        if content.strip():
            context_parts.append(content.strip())
            
    if isinstance(external_context, str) and external_context.strip():
        context_parts.append(external_context.strip())
        
    context = "\n\n".join(context_parts).strip()
    
    if not context:
        # If no context can be found, return a default structured error
        return {
            "subject": subject,
            "topic": topic or "General",
            "difficulty": difficulty,
            "flashcards": [],
            "error": "No study context was found to generate flashcards."
        }

    # 3. Create Gemini Prompt
    prompt = create_flashcard_prompt(
        text=context,
        subject=subject,
        unit=unit,
        topic=topic,
        difficulty=difficulty,
        number_of_cards=number_of_cards
    )

    # 4. Generate with Gemini
    raw_response = ask_gemini(prompt)
    if not raw_response:
        return {
            "subject": subject,
            "topic": topic or "General",
            "flashcards": [],
            "error": "Gemini generated an empty flashcard response."
        }

    # 5. Parse JSON output
    cleaned_json = raw_response.strip()
    if cleaned_json.startswith("```"):
        cleaned_json = re.sub(r"^```(?:json)?", "", cleaned_json, flags=re.IGNORECASE)
        cleaned_json = re.sub(r"```$", "", cleaned_json).strip()
        
    start = cleaned_json.find("{")
    end = cleaned_json.rfind("}")
    
    if start == -1 or end == -1:
        return {
            "subject": subject,
            "topic": topic or "General",
            "flashcards": [],
            "error": "Could not locate JSON formatting in LLM output.",
            "raw": raw_response
        }
        
    json_text = cleaned_json[start:end + 1]
    
    try:
        parsed_cards = json.loads(json_text)
        return parsed_cards
    except Exception as e:
        return {
            "subject": subject,
            "topic": topic or "General",
            "flashcards": [],
            "error": f"JSON parsing failed: {str(e)}",
            "raw": raw_response
        }
