"""
Base OCR Engine

Every OCR engine should inherit from this class.
"""

from abc import ABC, abstractmethod
from PIL import Image


class BaseOCR(ABC):
    """
    Base class for OCR engines.
    """

    @abstractmethod
    def extract_text(self, image: Image.Image) -> str:
        """
        Extract text from an image.

        Parameters
        ----------
        image : PIL.Image

        Returns
        -------
        str
        """
        pass