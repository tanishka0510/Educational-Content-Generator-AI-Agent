"""
EasyOCR Engine
"""

import easyocr
import numpy as np
from PIL import Image

from app.ocr.base_ocr import BaseOCR


class EasyOCREngine(BaseOCR):
    """
    OCR engine using EasyOCR.
    """

    _reader = None

    @classmethod
    def get_reader(cls):
        """
        Load EasyOCR only once.
        """

        if cls._reader is None:
            cls._reader = easyocr.Reader(
                ["en"],
                gpu=False
            )

        return cls._reader

    def extract_text(self, image: Image.Image) -> str:
        """
        Extract text from an image.
        """

        # Convert to grayscale (faster)
        image = image.convert("L")

        image = np.array(image)

        reader = self.get_reader()

        results = reader.readtext(
            image,
            detail=0,
            paragraph=True,
            batch_size=4
        )

        return "\n".join(results)