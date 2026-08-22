import json

from services.gemini_service import ask_gemini
from prompts.quiz_prompt import create_quiz_prompt


def generate_quiz(
    text,
    subject,
    unit=None,
    topic=None,
    difficulty="medium",
    number_of_questions=5,
):
    prompt = create_quiz_prompt(
        text=text,
        subject=subject,
        unit=unit,
        topic=topic,
        difficulty=difficulty,
        number_of_questions=number_of_questions,
    )

    response = ask_gemini(prompt)

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