"""
Document Loading Service

Loads documents using the appropriate loader.
Falls back to OCR for scanned PDFs.
"""

from pathlib import Path

from fastapi import HTTPException

from app.loaders.pdf_loader import PDFLoader
from app.ocr.ocr_loader import OCRLoader


class DocumentLoadingService:
    """
    Handles document loading and OCR fallback.
    """

    MIN_TEXT_LENGTH = 300

    @staticmethod
    def load(file_path: str) -> str:
        """
        Load text from a document.

        Parameters
        ----------
        file_path : str
            Path to the uploaded document.

        Returns
        -------
        str
            Extracted document text.
        """

        extension = Path(file_path).suffix.lower()

        if extension == ".pdf":

            print("Trying embedded PDF extraction...")

            loader = PDFLoader()

            text = loader.load(file_path)

            if len(text.strip()) >= DocumentLoadingService.MIN_TEXT_LENGTH:
                print("✓ Embedded text detected.")
                return text

            print("Scanned PDF detected → Running OCR...")

            return OCRLoader.extract(file_path)

        raise HTTPException(
            status_code=400,
            detail=f"No loader available for '{extension}'."
        )