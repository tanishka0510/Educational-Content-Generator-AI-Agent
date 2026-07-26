import re
from typing import Optional


class MetadataService:
    """
    Extract useful metadata from educational documents.
    """

    # ----------------------------------------------------
    # Detect Unit Number
    # ----------------------------------------------------

    @staticmethod
    def detect_unit(text: str) -> Optional[str]:

        patterns = [

            r"\bUNIT\s*[-:]?\s*(\d+)\b",
            r"\bUnit\s*(\d+)\b",
            r"\bCHAPTER\s*(\d+)\b",
            r"\bChapter\s*(\d+)\b",

        ]

        first_500 = text[:500]

        for pattern in patterns:

            match = re.search(
                pattern,
                first_500,
                flags=re.IGNORECASE
            )

            if match:
                return f"Unit {match.group(1)}"

        return None

    # ----------------------------------------------------
    # Detect Topic
    # ----------------------------------------------------

    @staticmethod
    def detect_topic(text: str) -> Optional[str]:

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        for line in lines[:15]:

            if len(line) < 80:

                lower = line.lower()

                ignore = [
                    "page",
                    "copyright",
                    "university",
                    "faculty",
                    "www",
                    "http",
                    "operating system",
                    "computer science"
                ]

                if not any(word in lower for word in ignore):
                    return line

        return None