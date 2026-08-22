def create_quiz_prompt(
    text,
    subject,
    unit=None,
    topic=None,
    difficulty="medium",
    number_of_questions=5,
):
    return f"""
You are an AI teacher generating an educational multiple-choice quiz.

Generate exactly {number_of_questions} multiple-choice questions from the
educational content provided below.

============================================================
QUIZ INFORMATION
============================================================

Subject: {subject}
Unit: {unit or "Not specified"}
Topic: {topic or "Not specified"}
Difficulty: {difficulty}
Number of Questions: {number_of_questions}

============================================================
STRICT REQUIREMENTS
============================================================

1. Use ONLY the educational content provided below.
2. Do NOT use outside knowledge.
3. Every question must be answerable from the provided content.
4. Questions must match the requested subject, unit, topic, and difficulty
   as closely as possible.
5. Generate EXACTLY {number_of_questions} questions.
6. Each question must contain EXACTLY 4 options.
7. There must be EXACTLY ONE correct answer for each question.
8. The correct_answer must exactly match one of the four options.
9. Every question must have an explanation.
10. The explanation must be based ONLY on the provided educational content.
11. Do NOT create duplicate questions.
12. Avoid testing exactly the same concept repeatedly.
13. Return ONLY valid JSON.
14. Do NOT use Markdown.
15. Do NOT wrap the JSON inside ``` or ```json.
16. Do NOT add any text before or after the JSON.

============================================================
DIFFICULTY GUIDELINES
============================================================

EASY:
- Test definitions.
- Test direct factual recall.
- Test simple concepts.
- Avoid complex reasoning.

MEDIUM:
- Test conceptual understanding.
- Test application of concepts.
- Test comparisons.
- Use moderate reasoning.

HARD:
- Test deeper conceptual understanding.
- Test application of multiple concepts.
- Test analysis and reasoning.
- Do not make questions difficult merely by making the wording longer.

============================================================
REQUIRED JSON FORMAT
============================================================

{{
    "quiz_title": "{subject} {difficulty.title()} Quiz",
    "questions": [
        {{
            "id": 1,
            "question": "...",
            "options": [
                "...",
                "...",
                "...",
                "..."
            ],
            "correct_answer": "...",
            "explanation": "..."
        }}
    ]
}}

============================================================
EDUCATIONAL CONTENT
============================================================

{text}
"""