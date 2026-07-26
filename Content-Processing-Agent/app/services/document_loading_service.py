"""
Document Loading Service

Selects the correct loader based on file type.
Falls back to OCR for scanned PDFs.
"""

from pathlib import Path

from fastapi import HTTPException

from app.loaders.pdf_loader import PDFLoader
from app.loaders.office_loader import OfficeLoader
from app.loaders.text_loader import PlainTextLoader
from app.ocr.ocr_loader import OCRLoader


class DocumentLoadingService:

    MIN_TEXT_LENGTH = 300

    @staticmethod
    def load(file_path: str) -> str:

        extension = Path(file_path).suffix.lower()

        # -------------------------------------
        # PDF
        # -------------------------------------

        if extension == ".pdf":

            print("Trying embedded PDF extraction...")

            loader = PDFLoader()

            text = loader.load(file_path)

            if len(text.strip()) >= DocumentLoadingService.MIN_TEXT_LENGTH:

                print("✓ Embedded text detected.")

                return text

            print("Scanned PDF detected -> Running OCR...")

            return OCRLoader.extract(file_path)

        # -------------------------------------
        # DOCX / PPTX
        # -------------------------------------

        elif extension in [".docx", ".pptx"]:

            print("Loading Office document...")

            return OfficeLoader.load(file_path)

        # -------------------------------------
        # TXT / Markdown
        # -------------------------------------

        elif extension in [".txt", ".md"]:

            print("Loading Text document...")

            return PlainTextLoader.load(file_path)

        # -------------------------------------
        # Unsupported
        # -------------------------------------

        raise HTTPException(
            status_code=400,
            detail=f"No loader available for '{extension}'."
        )