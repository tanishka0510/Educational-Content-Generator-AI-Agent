"""
Text Cleaner

Responsible for cleaning extracted raw text before it
is sent to analysis, chunking and embeddings.
"""

import re


class TextCleaner:
    """
    Cleans extracted document text.
    """

    # Common artifacts found in scanned educational PDFs
    ARTIFACT_PATTERNS = [
        r"Scanned by CamScanner",
        r"TECHNICAL PUBLICATIONS",
        r"An up thrust for knowledge",
    ]

    @staticmethod
    def clean(text: str) -> str:
        """
        Clean extracted document text.

        Parameters
        ----------
        text : str
            Raw extracted text.

        Returns
        -------
        str
            Cleaned text.
        """

        if not text:
            return ""

        # -----------------------------------------
        # Normalize line endings
        # -----------------------------------------
        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        # -----------------------------------------
        # Replace tabs with spaces
        # -----------------------------------------
        text = text.replace("\t", " ")

        # -----------------------------------------
        # Remove multiple spaces
        # -----------------------------------------
        text = re.sub(r"[ ]{2,}", " ", text)

        # -----------------------------------------
        # Remove page numbers appearing alone
        # Examples:
        # 1
        # 12
        # 250
        # -----------------------------------------
        text = re.sub(
            r"^\s*\d+\s*$",
            "",
            text,
            flags=re.MULTILINE
        )

        # -----------------------------------------
        # Remove page markers
        # Examples:
        # 7-12
        # 3-18
        # 10-4
        # -----------------------------------------
        text = re.sub(
            r"\b\d+\-\d+\b",
            "",
            text
        )

        # -----------------------------------------
        # Remove common scanned PDF artifacts
        # -----------------------------------------
        for pattern in TextCleaner.ARTIFACT_PATTERNS:
            text = re.sub(
                pattern,
                "",
                text,
                flags=re.IGNORECASE
            )

        # -----------------------------------------
        # Remove spaces before newline
        # -----------------------------------------
        text = re.sub(
            r"[ \t]+\n",
            "\n",
            text
        )

        # -----------------------------------------
        # Remove excessive blank lines
        # -----------------------------------------
        text = re.sub(
            r"\n{3,}",
            "\n\n",
            text
        )

        # -----------------------------------------
        # Remove leading/trailing whitespace
        # -----------------------------------------
        text = text.strip()

        return text