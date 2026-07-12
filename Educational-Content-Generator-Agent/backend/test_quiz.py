from services.quiz_generator import generate_quiz

sample_text = """
Artificial Intelligence is a branch of computer science.
Machine Learning is a subset of Artificial Intelligence.
Deep Learning is a subset of Machine Learning.
"""

quiz = generate_quiz(sample_text)

print(quiz)