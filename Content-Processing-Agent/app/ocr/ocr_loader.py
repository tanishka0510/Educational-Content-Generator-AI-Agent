"""
OCR Loader

Runs OCR on scanned PDF pages.
"""

import fitz
from PIL import Image

from app.ocr.easy_ocr import EasyOCREngine


class OCRLoader:
    """
    OCR loader for scanned PDFs.
    """

    @staticmethod
    def extract(pdf_path: str) -> str:
        """
        Extract text from scanned PDF.
        """

        doc = fitz.open(pdf_path)

        ocr = EasyOCREngine()

        pages = []

        total_pages = len(doc)

        for i, page in enumerate(doc):

            print(f"Processing page {i+1}/{total_pages}")

            pix = page.get_pixmap(
                dpi=150,
                alpha=False
            )

            image = Image.frombytes(
                "RGB",
                (pix.width, pix.height),
                pix.samples
            )

            try:
                text = ocr.extract_text(image)
            except Exception as e:
                print(f"OCR failed on page {i+1}: {e}")
                text = ""

            pages.append(text)

        doc.close()

        final_text = "\n\n".join(pages)

        print(f"\nOCR extracted {len(final_text)} characters.")

        return final_text