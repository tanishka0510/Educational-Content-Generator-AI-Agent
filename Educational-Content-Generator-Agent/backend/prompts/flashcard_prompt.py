"""
Flashcard Generator Prompt Template

Project: Educational Content Generator AI
Module: Educational Agent
"""

def create_flashcard_prompt(
    text: str,
    subject: str,
    unit: str = None,
    topic: str = None,
    difficulty: str = "medium",
    number_of_cards: int = 5,
) -> str:
    """
    Constructs the prompt for Gemini to generate flashcards from context.
    """
    
    subject_details = f"Subject: {subject}"
    if unit:
        subject_details += f"\nUnit: {unit}"
    if topic:
        subject_details += f"\nTopic: {topic}"

    prompt = f"""
You are an expert educational designer. Your task is to generate high-quality study flashcards from the provided study context.

==================================================
STUDY SPECIFICATIONS
==================================================
{subject_details}
Difficulty Level: {difficulty}
Number of Cards to Generate: {number_of_cards}

==================================================
EDUCATIONAL CONTEXT (SOURCE MATERIAL)
==================================================
{text}

==================================================
FLASHCARD DESIGN INSTRUCTIONS
==================================================
1. Each flashcard must consist of a "front" (Question, Term, or Concept prompt) and a "back" (Clear, concise answer or explanation).
2. The front should be brief and trigger active recall (e.g., "What is the difference between X and Y?", "Define Abstraction in OOP").
3. The back should explain the concept clearly in 1 to 3 sentences. Avoid long paragraphs.
4. Adapt the explanation depth based on the specified difficulty level ({difficulty}):
   - 'easy': Simple language, focused on core definitions and basic intuition.
   - 'medium': Good technical accuracy, standard definitions, and clear examples.
   - 'hard': In-depth technical explanations, highlighting edge cases or complex performance trade-offs.
5. Create exactly {number_of_cards} unique cards.
6. Base all questions and answers strictly on the facts provided in the Educational Context. Do not invent outside information.

==================================================
RESPONSE FORMAT
==================================================
You must return the response as a single, valid JSON object. Do not include any extra text, comments, or markdown formatting outside the JSON.

Expected JSON schema:
{{
  "subject": "{subject}",
  "topic": "{topic or 'General'}",
  "difficulty": "{difficulty}",
  "flashcards": [
    {{
      "id": 1,
      "front": "Question or term on the front of the card",
      "back": "Answer or explanation on the back of the card"
    }}
  ]
}}
"""
    return prompt.strip()
