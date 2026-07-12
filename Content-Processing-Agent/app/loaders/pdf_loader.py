import fitz

from app.loaders.base_loader import BaseLoader


class PDFLoader(BaseLoader):

    def load(self, file_path: str) -> str:

        doc = fitz.open(file_path)

        pages = []

        for page in doc:
            pages.append(page.get_text())

        doc.close()

        return "\n".join(pages)