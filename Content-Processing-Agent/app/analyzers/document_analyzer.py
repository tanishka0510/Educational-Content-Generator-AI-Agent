"""
Document Analyzer

Analyzes cleaned text and extracts useful metadata.
"""

import re
from langdetect import detect
import yake


class DocumentAnalyzer:
    """
    Performs document analysis.
    """

    # ======================================================
    # Subject Keywords
    # ======================================================

    SUBJECT_KEYWORDS = {

        "OOP": [
            "object",
            "class",
            "constructor",
            "inheritance",
            "encapsulation",
            "polymorphism",
            "abstraction",
            "interface",
            "package",
            "method",
            "java",
            "jvm",
            "jdk",
            "exception",
            "collection"
        ],

        "OS": [
            "operating system",
            "process",
            "thread",
            "deadlock",
            "paging",
            "memory",
            "scheduler",
            "cpu",
            "kernel",
            "semaphore",
            "critical section"
        ],

        "DBMS": [
            "database",
            "sql",
            "normalization",
            "transaction",
            "entity",
            "attribute",
            "relation",
            "table",
            "primary key",
            "foreign key"
        ],

        "CN": [
            "network",
            "router",
            "switch",
            "tcp",
            "udp",
            "ip",
            "http",
            "osi",
            "protocol",
            "ethernet"
        ],

        "DSA": [
            "array",
            "stack",
            "queue",
            "linked list",
            "tree",
            "graph",
            "sorting",
            "searching",
            "recursion",
            "binary tree"
        ],

        "Python": [
            "python",
            "list",
            "tuple",
            "dictionary",
            "lambda",
            "numpy",
            "pandas"
        ]
    }

    @staticmethod
    def analyze(text: str) -> dict:

        if not text.strip():

            return {
                "subject": "",
                "topics": [],
                "keywords": [],
                "language": "Unknown",
                "word_count": 0,
                "character_count": 0,
                "reading_time": 0,
            }

        # -------------------------------------------------
        # Language
        # -------------------------------------------------

        try:
            language = detect(text)
        except Exception:
            language = "Unknown"

        language_map = {
            "en": "English",
            "hi": "Hindi",
            "fr": "French",
            "de": "German",
            "es": "Spanish",
        }

        language = language_map.get(language, language)

        # -------------------------------------------------
        # Word Count
        # -------------------------------------------------

        words = text.split()

        word_count = len(words)

        character_count = len(text)

        reading_time = max(1, round(word_count / 200))

        # -------------------------------------------------
        # Keywords (YAKE)
        # -------------------------------------------------

        extractor = yake.KeywordExtractor(
            lan="en",
            n=2,
            top=15,
        )

        keyword_result = extractor.extract_keywords(text)

        keywords = [keyword for keyword, _ in keyword_result]

        # -------------------------------------------------
        # Subject Classification
        # -------------------------------------------------

        lower_text = text.lower()

        scores = {}

        for subject, subject_keywords in DocumentAnalyzer.SUBJECT_KEYWORDS.items():

            score = 0

            for keyword in subject_keywords:

                score += lower_text.count(keyword.lower())

            scores[subject] = score

        best_subject = max(scores, key=scores.get)

        if scores[best_subject] == 0:
            best_subject = "General"

        # -------------------------------------------------
        # Topics
        # -------------------------------------------------

        topics = []

        headings = re.findall(
            r"(?:Chapter\s+\d+[:.]?\s*.*|Unit\s+\d+[:.]?\s*.*)",
            text,
            re.IGNORECASE,
        )

        for heading in headings:

            heading = heading.strip()

            if heading not in topics:
                topics.append(heading)

        if not topics:
            topics = keywords[:5]

        return {

            "subject": best_subject,

            "topics": topics,

            "keywords": keywords,

            "language": language,

            "word_count": word_count,

            "character_count": character_count,

            "reading_time": reading_time,

        }