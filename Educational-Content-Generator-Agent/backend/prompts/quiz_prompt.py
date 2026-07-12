def create_quiz_prompt(text):
    return f"""
You are an AI teacher.

Read the educational content below and generate exactly 5 multiple-choice questions.

Requirements:

1. Return ONLY valid JSON.
2. Do NOT use markdown.
3. Do NOT write explanations.
4. Do NOT wrap the JSON inside ```.

Format:

{{
  "quiz":[
    {{
      "question":"...",
      "options":[
        "A",
        "B",
        "C",
        "D"
      ],
      "answer":"A"
    }}
  ]
}}

Educational Content:

{text}
"""