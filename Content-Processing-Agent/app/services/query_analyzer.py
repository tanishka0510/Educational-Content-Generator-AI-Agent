"""
Query Analyzer

Extracts retrieval metadata from the user's question.

Current Version:
- Topic
- Unit
- Keywords
- Difficulty

Later:
- Bloom Level
- Intent
- Question Type
"""

import re


class QueryAnalyzer:

    @staticmethod
    def analyze(question: str):

        question_lower = question.lower()

        # ---------------------------------------------
        # Unit Detection
        # ---------------------------------------------

        unit = None

        match = re.search(
            r"unit\s*[-:]?\s*(\d+)",
            question_lower
        )

        if match:
            unit = f"Unit {match.group(1)}"

        # ---------------------------------------------
        # Topic Detection
        # ---------------------------------------------

        stop_words = {
            "what",
            "is",
            "are",
            "the",
            "of",
            "a",
            "an",
            "explain",
            "define",
            "write",
            "short",
            "note",
            "on",
            "about",
            "why",
            "how",
            "when",
            "where",
            "which",
            "give",
            "list",
            "with",
            "for",
            "to",
            "in",
            "and",
        }

        words = re.findall(
            r"[A-Za-z]+",
            question
        )

        keywords = []

        for word in words:

            if word.lower() not in stop_words:
                keywords.append(word)

        topic = " ".join(keywords)

        # ---------------------------------------------
        # Difficulty Detection
        # ---------------------------------------------

        difficulty = "Medium"

        if any(
            word in question_lower
            for word in [
                "define",
                "what is",
                "list"
            ]
        ):
            difficulty = "Easy"

        elif any(
            word in question_lower
            for word in [
                "compare",
                "difference",
                "advantages",
                "disadvantages"
            ]
        ):
            difficulty = "Medium"

        elif any(
            word in question_lower
            for word in [
                "design",
                "implement",
                "analysis",
                "algorithm",
                "prove"
            ]
        ):
            difficulty = "Hard"

        return {

            "topic": topic,

            "unit": unit,

            "keywords": keywords,

            "difficulty": difficulty,
        }