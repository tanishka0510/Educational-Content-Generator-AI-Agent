import json

from services.gemini_service import ask_gemini
from prompts.quiz_prompt import create_quiz_prompt


def generate_quiz(text):
    prompt = create_quiz_prompt(text)

    response = ask_gemini(prompt)

    # Remove markdown if Gemini accidentally returns it
    response = response.replace("```json", "")
    response = response.replace("```", "")
    response = response.strip()

    try:
        quiz = json.loads(response)
        return quiz

    except json.JSONDecodeError:
        return {
            "error": "Failed to parse Gemini response",
            "raw_response": response
        }