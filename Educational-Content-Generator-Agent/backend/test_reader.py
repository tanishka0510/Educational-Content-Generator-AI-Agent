from services.pdf_reader import extract_text_from_pdf

pdf_path = "uploads/AI Technical.pdf"

text = extract_text_from_pdf(pdf_path)

print(text)