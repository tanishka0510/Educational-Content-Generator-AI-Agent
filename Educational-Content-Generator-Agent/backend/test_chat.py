from services.pdf_reader import extract_text
from services.text_cleaner import clean_text
from services.chat_service import chat_with_document

text = extract_text("uploads/AI Technical.pdf")

text = clean_text(text)

question = "What is Artificial Intelligence?"

answer = chat_with_document(text, question)

print(answer)