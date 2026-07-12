from services.pdf_reader import extract_text_from_pdf
from services.text_cleaner import clean_text

pdf_path = "uploads/AI Technical.pdf"

text = extract_text_from_pdf(pdf_path)

cleaned = clean_text(text)

print(cleaned)