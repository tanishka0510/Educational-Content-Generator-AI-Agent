from PyPDF2 import PdfReader

def extract_text(pdf_path):
    reader = PdfReader(pdf_path)

    text = ""

    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"

    return text


if __name__ == "__main__":
    text = extract_text("uploads/AI Technical.pdf")
    print(text)