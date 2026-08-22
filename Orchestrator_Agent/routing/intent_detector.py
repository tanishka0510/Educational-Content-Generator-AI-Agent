"""
==========================================================
Intent Detector (Version 2)

Project:
Educational Content Generator AI

Module:
Orchestrator Agent

Purpose:
Priority-based intent detection with mixed-query support.
==========================================================
"""

from typing import Dict, List, Set

from schemas.request import OrchestratorRequest
from utils.constants import Intent
from utils.logger import get_logger

logger = get_logger(__name__)


class IntentDetector:

    def __init__(self):

        self.intent_keywords: Dict[Intent, List[str]] = {

            Intent.ADMIN: [
                "system status",
                "status",
                "health",
                "reset",
                "clear"
            ],

            Intent.FOLLOW_UP: [
                "again",
                "continue",
                "previous",
                "earlier",
                "next"
            ],

            Intent.UPLOAD: [
                "upload",
                "import",
                "add document",
                "process file",
                "pdf"
            ],

            Intent.MULTIMEDIA: [
                "image",
                "video",
                "audio",
                "diagram",
                "infographic"
            ],

            Intent.SUMMARY: [
                "summary",
                "summarize"
            ],

            Intent.QUIZ: [
                "quiz",
                "mcq"
            ],

            Intent.FLASHCARDS: [
                "flashcard",
                "flashcards"
            ],

            Intent.LEARNING_OBJECTIVES: [
                "learning objectives",
                "learning objective"
            ],

            Intent.RESOURCE_SEARCH: [
                "resource",
                "resources",
                "reference",
                "references"
            ],

            Intent.COMPARE: [
                "compare",
                "difference",
                "versus",
                "vs"
            ],

            Intent.EXPLANATION: [
                "explain",
                "describe",
                "definition"
            ],

            Intent.PROGRAMMING: [
                "python",
                "java",
                "program",
                "coding",
                "code"
            ],

            Intent.MATHEMATICS: [
                "solve",
                "equation",
                "calculate",
                "math"
            ],

            Intent.ASSIGNMENT: [
                "assignment",
                "homework"
            ],

            Intent.STUDY_PLAN: [
                "study plan",
                "study schedule"
            ],

            Intent.GENERAL_KNOWLEDGE: [
                "tell me about",
                "information about"
            ],

            Intent.QA: [
                "what",
                "why",
                "when",
                "where",
                "who",
                "how",
                "question",
                "answer"
            ],
        }

    def detect(self, request: OrchestratorRequest) -> Intent:

        query = request.user_input.query.lower().strip()

        logger.info(f"Detecting intent for query: '{query}'")

        matched: Set[Intent] = set()

        for intent, keywords in self.intent_keywords.items():

            for keyword in keywords:

                if keyword in query:

                    matched.add(intent)

                    logger.debug(f"Matched '{keyword}' -> {intent.value}")

                    break

        if not matched:

            logger.info("No intent matched. Defaulting to QA.")

            return Intent.QA

        if len(matched) == 1:

            detected = next(iter(matched))

            logger.info(f"Detected intent: {detected.value}")

            return detected

        logger.info(
            f"Multiple intents detected: {[i.value for i in matched]}"
        )

        return Intent.MIXED_QUERY