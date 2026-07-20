from app.services.llm_service import generate_answer

context = """
Data Structure is a method of organizing data efficiently.
Algorithm + Data Structure = Program.
"""

question = "What is a Data Structure?"

answer = generate_answer(context, question)

print(answer)