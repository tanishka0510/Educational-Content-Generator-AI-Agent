"""
Document Analyzer

Analyzes cleaned text and extracts useful metadata.
"""

import re

from langdetect import detect
import yake


class DocumentAnalyzer:
    """
    Performs basic document analysis.
    """

    @staticmethod
    def analyze(text: str) -> dict:
        """
        Analyze cleaned text.

        Returns:
            dict
        """

        if not text.strip():
            return {
                "subject": "",
                "topics": [],
                "keywords": [],
                "language": "Unknown",
                "word_count": 0,
                "character_count": 0,
                "reading_time": 0
            }

        # ----------------------------------------
        # Language
        # ----------------------------------------

        try:
            language = detect(text)
        except Exception:
            language = "Unknown"

        language_map = {
            "en": "English",
            "hi": "Hindi",
            "fr": "French",
            "de": "German",
            "es": "Spanish"
        }

        language = language_map.get(language, language)

        # ----------------------------------------
        # Word Count
        # ----------------------------------------

        words = text.split()

        word_count = len(words)

        character_count = len(text)

        reading_time = max(1, round(word_count / 200))

        # ----------------------------------------
        # Keywords
        # ----------------------------------------

        extractor = yake.KeywordExtractor(
            lan="en",
            n=2,
            top=15
        )

        keyword_result = extractor.extract_keywords(text)

        keywords = []

        for keyword, score in keyword_result:
            keywords.append(keyword)

        # ----------------------------------------
        # Subject
        # ----------------------------------------

        subject = keywords[0] if keywords else "General"

        # ----------------------------------------
        # Topics
        # ----------------------------------------

        topics = []

        headings = re.findall(
            r"(?:Chapter\s+\d+[:.]?\s*.*|Unit\s+\d+[:.]?\s*.*)",
            text,
            re.IGNORECASE
        )

        for heading in headings:
            heading = heading.strip()

            if heading not in topics:
                topics.append(heading)

        # Fallback

        if not topics:
            topics = keywords[:5]

        return {
            "subject": subject,
            "topics": topics,
            "keywords": keywords,
            "language": language,
            "word_count": word_count,
            "character_count": character_count,
            "reading_time": reading_time
        }