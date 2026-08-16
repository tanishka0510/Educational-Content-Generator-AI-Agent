"""
Query Analyzer

Extracts retrieval and generation metadata from the user's question.

Returns:
    - topic
    - unit
    - keywords
    - difficulty
    - intent
    - response_style

Design goals:
    1. Subject-agnostic
       Works consistently for OS, DBMS, OOP, CN, AI/ML,
       Software Engineering, Mathematics, etc.

    2. Separate WHAT from HOW
       WHAT the user wants to study  -> topic / keywords
       WHAT the user wants to do      -> intent
       HOW the answer should look     -> response_style

    3. Preserve technical vocabulary
       Instructional words are removed from the retrieval query,
       but technical concepts are preserved.

Examples:

    "Explain normalization in brief"
        topic          -> normalization
        intent         -> explanation
        response_style -> brief

    "Explain deadlock in OS in detail"
        topic          -> deadlock os
        intent         -> explanation
        response_style -> detailed

    "Compare process and thread"
        topic          -> process thread
        intent         -> comparison
        response_style -> normal

    "Compare primary storage and secondary storage"
        topic          -> primary storage secondary storage
        intent         -> comparison
        response_style -> normal

    "Explain polymorphism in simple language"
        topic          -> polymorphism
        intent         -> explanation
        response_style -> beginner

    "Calculate subnet mask with example"
        topic          -> subnet mask
        intent         -> mathematical
        response_style -> with_examples

    "Explain implementation of binary search"
        topic          -> implementation binary search
        intent         -> explanation
        response_style -> normal

Important:
    The analyzer does NOT contain subject-specific rules.

    Do NOT add rules such as:

        if subject == "OS":
            ...

        if "deadlock" in question:
            ...

    The same analyzer must work across all subjects.
"""

import re


class QueryAnalyzer:

    # ==========================================================
    # MAIN ANALYZER
    # ==========================================================

    @staticmethod
    def analyze(question: str):
        """
        Analyze a user question and return normalized metadata.
        """

        # ------------------------------------------------------
        # Empty question
        # ------------------------------------------------------

        if not question or not question.strip():
            return {
                "topic": "",
                "unit": None,
                "keywords": [],
                "difficulty": "Medium",
                "intent": "general",
                "response_style": "normal",
            }

        question_lower = question.lower().strip()

        # ======================================================
        # UNIT DETECTION
        # ======================================================

        unit = QueryAnalyzer._detect_unit(question_lower)

        # ======================================================
        # RESPONSE STYLE
        # ======================================================

        response_style = QueryAnalyzer._detect_response_style(
            question_lower
        )

        # ======================================================
        # INTENT
        # ======================================================

        intent = QueryAnalyzer._detect_intent(
            question_lower
        )

        # ======================================================
        # TOPIC + KEYWORDS
        # ======================================================

        topic, keywords = QueryAnalyzer._extract_topic_and_keywords(
            question_lower
        )

        # ======================================================
        # DIFFICULTY
        # ======================================================

        difficulty = QueryAnalyzer._detect_difficulty(
            question_lower,
            intent
        )

        # ======================================================
        # DEBUG OUTPUT
        # ======================================================

        print("\n========== QUERY ANALYSIS ==========")
        print(f"Original Question : {question}")
        print(f"Topic             : {topic}")
        print(f"Keywords          : {keywords}")
        print(f"Intent            : {intent}")
        print(f"Response Style    : {response_style}")
        print(f"Difficulty        : {difficulty}")
        print(f"Unit              : {unit}")
        print("====================================\n")

        # ======================================================
        # RETURN
        # ======================================================

        return {
            "topic": topic,
            "unit": unit,
            "keywords": keywords,
            "difficulty": difficulty,
            "intent": intent,
            "response_style": response_style,
        }

    # ==========================================================
    # UNIT DETECTION
    # ==========================================================

    @staticmethod
    def _detect_unit(question: str):
        """
        Detect unit references such as:

            Unit 1
            unit-1
            unit: 1
            Unit:1

        Also supports:

            Chapter 1
            chapter-1
            chapter: 1

        Returns:
            "Unit 1"
            or None
        """

        patterns = [
            r"\bunit\s*[-:]?\s*(\d+)\b",
            r"\bchapter\s*[-:]?\s*(\d+)\b",
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                question,
                flags=re.IGNORECASE,
            )

            if match:
                return f"Unit {match.group(1)}"

        return None

    # ==========================================================
    # TOPIC / KEYWORD EXTRACTION
    # ==========================================================

    @staticmethod
    def _extract_topic_and_keywords(question: str):
        """
        Extract the actual academic/technical content from the
        question.

        Important principle:

            REMOVE INSTRUCTIONS
            PRESERVE SUBJECT MATTER

        Examples:

            "Explain normalization in brief"
                -> normalization

            "Explain implementation of binary search"
                -> implementation binary search

            "Compare process and thread"
                -> process thread

            "Compare primary storage and secondary storage"
                -> primary storage secondary storage

            "What is the difference between primary storage
             and secondary storage?"
                -> primary storage secondary storage
        """

        topic_text = question.lower().strip()

        # ======================================================
        # PHRASES TO REMOVE
        # ======================================================

        instruction_phrases = [

            # --------------------------------------------------
            # Explanation / question instructions
            # --------------------------------------------------

            "give me an explanation",
            "give me explanation",
            "provide an explanation",
            "provide explanation",

            "explain",
            "explanation",
            "define",
            "definition",
            "describe",
            "description",
            "discuss",
            "discussion",
            "elaborate",
            "clarify",
            "clarification",

            # --------------------------------------------------
            # Quiz
            # --------------------------------------------------

            "generate a quiz",
            "generate quiz",
            "create a quiz",
            "create quiz",
            "make a quiz",
            "make quiz",
            "give me a quiz",
            "give me quiz",

            "generate mcqs",
            "generate mcq",
            "create mcqs",
            "create mcq",
            "make mcqs",
            "make mcq",

            "multiple choice questions",
            "multiple choice question",

            "true or false questions",
            "true or false question",

            "fill in the blanks",
            "fill in the blank",

            "viva questions",
            "viva question",

            "practice questions",
            "practice question",

            # --------------------------------------------------
            # Flashcards
            # --------------------------------------------------

            "create flashcards",
            "create flashcard",
            "make flashcards",
            "make flashcard",
            "generate flashcards",
            "generate flashcard",

            "give me flashcards",
            "give me flashcard",

            "revision cards",
            "revision card",
            "memory cards",
            "memory card",

            # --------------------------------------------------
            # Summarization
            # --------------------------------------------------

            "summarize",
            "summarise",
            "summary",
            "summarization",
            "summarisation",

            "key takeaways",
            "revision notes",
            "short notes",
            "short note",

            # --------------------------------------------------
            # Keyword extraction
            # --------------------------------------------------

            "extract keywords",
            "extract keyword",
            "important terms",
            "important term",
            "technical vocabulary",
            "index terms",

            # --------------------------------------------------
            # Concept extraction
            # --------------------------------------------------

            "main concepts",
            "main concept",
            "core concepts",
            "core concept",
            "list concepts",
            "list concept",
            "concept hierarchy",
            "concept map",
            "relationships between concepts",
            "relationship between concepts",

            # --------------------------------------------------
            # Learning objectives
            # --------------------------------------------------

            "learning objectives",
            "learning objective",
            "course outcomes",
            "course outcome",
            "study roadmap",
            "concepts to master",
            "concept to master",

            # --------------------------------------------------
            # External resources
            # --------------------------------------------------

            "find youtube videos",
            "find youtube video",
            "youtube videos",
            "youtube video",

            "khan academy resources",
            "khan academy resource",

            "nptel lectures",
            "nptel lecture",

            "online resources",
            "online resource",

            "additional reading",
            "reference books",
            "reference book",

            # --------------------------------------------------
            # Mathematical / problem-solving instructions
            # --------------------------------------------------

            "solve for",
            "solve",
            "calculate",
            "derivation",
            "derive",
            "numerical example",
            "numerical examples",
            "practice problem",
            "practice problems",

            # --------------------------------------------------
            # General question phrases
            # --------------------------------------------------

            "what is",
            "what are",
            "what was",
            "what were",

            "why is",
            "why are",
            "why was",
            "why were",

            "how does",
            "how do",
            "how did",
            "how is",
            "how are",

            "why does",
            "why do",
            "why did",

            "when is",
            "when are",
            "when does",
            "when do",

            "where is",
            "where are",
            "where does",
            "where do",

            "which is",
            "which are",

            # --------------------------------------------------
            # Response style
            # --------------------------------------------------

            "in brief",
            "briefly",
            "brief",

            "short answer",
            "shortly",
            "in short",

            "in detail",
            "in-depth",
            "in depth",
            "detailed",
            "detail",
            "deeply",
            "deep explanation",
            "advanced explanation",
            "technical explanation",

            "simple language",
            "simple explanation",
            "beginner friendly",
            "beginner-friendly",
            "for beginners",
            "easy language",

            "exam oriented",
            "exam-oriented",
            "for exam",

            "interview oriented",
            "interview-oriented",
            "for interview",

            "step by step",
            "step-by-step",
            "show the steps",

            "bullet points",
            "in points",
            "point wise",
            "point-wise",

            "with examples",
            "with example",
            "give examples",
            "give an example",

            "real life example",
            "real-life example",

            "one word",
            "one-word",
            "single word",

            "one sentence",
            "one-sentence",
            "single sentence",

            # --------------------------------------------------
            # Generic politeness / instructions
            # --------------------------------------------------

            "please",
            "can you",
            "could you",
            "would you",
            "will you",

            "tell me",
            "give me",
            "provide",
            "show me",

            "answer",
            "mention",
            "list",
            "enlist",

            # --------------------------------------------------
            # Comparison instructions
            # --------------------------------------------------

            "difference between",
            "differences between",

            "compare",
            "comparison",

            "versus",
            "vs",
            "vs.",
        ]

        # Remove longer phrases first.
        instruction_phrases = sorted(
            set(instruction_phrases),
            key=len,
            reverse=True,
        )

        for phrase in instruction_phrases:

            topic_text = re.sub(
                rf"\b{re.escape(phrase)}\b",
                " ",
                topic_text,
                flags=re.IGNORECASE,
            )

        # ======================================================
        # REMOVE UNIT / CHAPTER REFERENCES
        # ======================================================

        topic_text = re.sub(
            r"\bunit\s*[-:]?\s*\d+\b",
            " ",
            topic_text,
            flags=re.IGNORECASE,
        )

        topic_text = re.sub(
            r"\bchapter\s*[-:]?\s*\d+\b",
            " ",
            topic_text,
            flags=re.IGNORECASE,
        )

        # ======================================================
        # REMOVE COMMON CONNECTORS
        # ======================================================

        connector_words = {
            "the",
            "of",
            "a",
            "an",
            "on",
            "about",
            "with",
            "for",
            "to",
            "in",
            "and",
            "or",
            "from",
            "using",
            "used",
            "use",
            "this",
            "that",
            "these",
            "those",

            "my",
            "me",
            "you",
            "your",

            "is",
            "are",
            "was",
            "were",
            "be",
            "being",
            "been",

            "do",
            "does",
            "did",

            "can",
            "could",
            "would",
            "should",
            "will",

            "please",

            # --------------------------------------------------
            # IMPORTANT FOR COMPARISON QUERIES
            #
            # Example:
            #
            # "difference between primary storage and
            # secondary storage"
            #
            # should become:
            #
            # "primary storage secondary storage"
            # --------------------------------------------------

            "between",
            "among",
            "than",
            "both",
        }

        # ======================================================
        # EXTRACT WORDS
        # ======================================================

        words = re.findall(
            r"[A-Za-z0-9]+(?:[-+.#][A-Za-z0-9]+)*",
            topic_text,
        )

        keywords = []

        for word in words:

            word_lower = word.lower().strip()

            if not word_lower:
                continue

            if word_lower in connector_words:
                continue

            # Ignore extremely short fragments.
            if len(word_lower) <= 1:
                continue

            keywords.append(word_lower)

        # ======================================================
        # REMOVE DUPLICATES
        # ======================================================

        keywords = list(
            dict.fromkeys(keywords)
        )

        # ======================================================
        # TOPIC
        # ======================================================

        topic = " ".join(keywords).strip()

        topic = re.sub(
            r"\s+",
            " ",
            topic,
        )

        # ======================================================
        # FALLBACK
        # ======================================================

        if not topic:

            fallback = QueryAnalyzer._fallback_topic(
                question
            )

            topic = fallback

            if fallback:
                keywords = fallback.split()

        return topic, keywords

    # ==========================================================
    # TOPIC FALLBACK
    # ==========================================================

    @staticmethod
    def _fallback_topic(question: str):
        """
        Conservative fallback when normal topic extraction
        produces an empty result.
        """

        fallback = question.lower().strip()

        fallback_phrases = [
            "what is",
            "what are",
            "why is",
            "why are",
            "how does",
            "how do",
            "how is",
            "how are",
            "why does",
            "why do",

            "difference between",
            "differences between",

            "compare",
            "comparison",

            "versus",
            "vs",
            "vs.",

            "explain",
            "define",
            "describe",
            "discuss",

            "please",
            "can you",
            "could you",
            "would you",

            "tell me",
            "give me",
            "provide",
            "show me",

            "in brief",
            "briefly",
            "in detail",
            "detailed",
            "in depth",
            "in-depth",

            "bullet points",
            "in points",
            "point wise",
            "point-wise",
        ]

        fallback_phrases = sorted(
            set(fallback_phrases),
            key=len,
            reverse=True,
        )

        for phrase in fallback_phrases:

            fallback = re.sub(
                rf"\b{re.escape(phrase)}\b",
                " ",
                fallback,
                flags=re.IGNORECASE,
            )

        fallback = re.sub(
            r"\bunit\s*[-:]?\s*\d+\b",
            " ",
            fallback,
            flags=re.IGNORECASE,
        )

        fallback = re.sub(
            r"\bchapter\s*[-:]?\s*\d+\b",
            " ",
            fallback,
            flags=re.IGNORECASE,
        )

        fallback_words = re.findall(
            r"[A-Za-z0-9]+(?:[-+.#][A-Za-z0-9]+)*",
            fallback,
        )

        fallback_stop_words = {
            "the",
            "of",
            "a",
            "an",
            "to",
            "in",
            "for",
            "on",
            "and",
            "or",
            "with",
            "about",
            "between",
            "among",
            "than",
            "is",
            "are",
            "was",
            "were",
            "be",
            "this",
            "that",
            "please",
        }

        fallback_words = [
            word.lower()
            for word in fallback_words
            if word.lower() not in fallback_stop_words
            and len(word) > 1
        ]

        return " ".join(
            dict.fromkeys(fallback_words)
        ).strip()

    # ==========================================================
    # RESPONSE STYLE DETECTION
    # ==========================================================

    @staticmethod
    def _detect_response_style(question: str):
        """
        Detect how the user wants the answer formatted.
        """

        question = question.lower().strip()

        # ------------------------------------------------------
        # ONE WORD
        # ------------------------------------------------------

        if re.search(
            r"\b(one\s+word|one-word|single\s+word)\b",
            question,
        ):
            return "one_word"

        # ------------------------------------------------------
        # ONE SENTENCE
        # ------------------------------------------------------

        if re.search(
            r"\b(one\s+sentence|one-sentence|single\s+sentence)\b",
            question,
        ):
            return "one_sentence"

        # ------------------------------------------------------
        # BULLET POINTS
        # ------------------------------------------------------

        if re.search(
            r"\b("
            r"bullet\s+points?"
            r"|in\s+points?"
            r"|point[-\s]?wise"
            r"|as\s+points?"
            r"|list\s+the"
            r"|enlist"
            r")\b",
            question,
        ):
            return "bullet_points"

        # ------------------------------------------------------
        # STEP BY STEP
        # ------------------------------------------------------

        if re.search(
            r"\b("
            r"step\s+by\s+step"
            r"|step-by-step"
            r"|show\s+the\s+steps?"
            r")\b",
            question,
        ):
            return "step_by_step"

        # ------------------------------------------------------
        # BRIEF
        # ------------------------------------------------------

        if re.search(
            r"\b("
            r"in\s+brief"
            r"|briefly"
            r"|brief"
            r"|short\s+answer"
            r"|shortly"
            r"|in\s+short"
            r")\b",
            question,
        ):
            return "brief"

        # ------------------------------------------------------
        # DETAILED
        # ------------------------------------------------------

        if re.search(
            r"\b("
            r"in\s+detail"
            r"|detailed"
            r"|detail"
            r"|in\s+depth"
            r"|in-depth"
            r"|deeply"
            r"|deep\s+explanation"
            r"|explain\s+deeply"
            r")\b",
            question,
        ):
            return "detailed"

        # ------------------------------------------------------
        # BEGINNER
        # ------------------------------------------------------

        if re.search(
            r"\b("
            r"simple\s+language"
            r"|simply"
            r"|simple\s+explanation"
            r"|beginner"
            r"|beginner\s+friendly"
            r"|beginner-friendly"
            r"|for\s+beginners"
            r"|easy\s+language"
            r")\b",
            question,
        ):
            return "beginner"

        # ------------------------------------------------------
        # ADVANCED
        # ------------------------------------------------------

        if re.search(
            r"\b("
            r"advanced"
            r"|advanced\s+explanation"
            r"|technical\s+explanation"
            r"|technically"
            r")\b",
            question,
        ):
            return "advanced"

        # ------------------------------------------------------
        # EXAM
        # ------------------------------------------------------

        if re.search(
            r"\b("
            r"for\s+exam"
            r"|exam\s+oriented"
            r"|exam-oriented"
            r"|examination"
            r"|viva"
            r")\b",
            question,
        ):
            return "exam"

        # ------------------------------------------------------
        # INTERVIEW
        # ------------------------------------------------------

        if re.search(
            r"\b("
            r"for\s+interview"
            r"|interview"
            r"|interview\s+oriented"
            r"|interview-oriented"
            r")\b",
            question,
        ):
            return "interview"

        # ------------------------------------------------------
        # EXAMPLES
        # ------------------------------------------------------

        if re.search(
            r"\b("
            r"with\s+example"
            r"|with\s+examples"
            r"|give\s+an\s+example"
            r"|give\s+examples"
            r"|real\s+life\s+example"
            r"|real-life\s+example"
            r"|analogy"
            r")\b",
            question,
        ):
            return "with_examples"

        # ------------------------------------------------------
        # NORMAL
        # ------------------------------------------------------

        return "normal"

    # ==========================================================
    # INTENT DETECTION
    # ==========================================================

    @staticmethod
    def _detect_intent(question: str):
        """
        Detect what the user wants to do.
        """

        question = question.lower().strip()

        # ======================================================
        # QUIZ
        # ======================================================

        if re.search(
            r"\b(generate|create|make|give)\s+(a\s+)?quiz\b",
            question,
        ):
            return "quiz"

        if any(
            phrase in question
            for phrase in [
                "mcq",
                "mcqs",
                "multiple choice",
                "true or false",
                "fill in the blank",
                "fill in the blanks",
                "viva questions",
                "viva question",
                "practice questions",
                "practice question",
            ]
        ):
            return "quiz"

        # ======================================================
        # FLASHCARDS
        # ======================================================

        if any(
            phrase in question
            for phrase in [
                "flashcard",
                "flashcards",
                "revision card",
                "revision cards",
                "memory card",
                "memory cards",
            ]
        ):
            return "flashcards"

        # ======================================================
        # SUMMARIZATION
        # ======================================================

        if any(
            phrase in question
            for phrase in [
                "summarize",
                "summarise",
                "summary",
                "summarization",
                "summarisation",
                "key takeaways",
                "revision notes",
                "short notes",
                "short note",
            ]
        ):
            return "summarization"

        # ======================================================
        # KEYWORD EXTRACTION
        # ======================================================

        if any(
            phrase in question
            for phrase in [
                "extract keywords",
                "extract keyword",
                "important terms",
                "important term",
                "technical vocabulary",
                "glossary",
                "index terms",
            ]
        ):
            return "keyword_extraction"

        # ======================================================
        # CONCEPT EXTRACTION
        # ======================================================

        if any(
            phrase in question
            for phrase in [
                "main concepts",
                "main concept",
                "core concepts",
                "core concept",
                "list concepts",
                "list concept",
                "concept hierarchy",
                "concept map",
                "relationships between concepts",
                "relationship between concepts",
            ]
        ):
            return "concept_extraction"

        # ======================================================
        # LEARNING OBJECTIVES
        # ======================================================

        if any(
            phrase in question
            for phrase in [
                "learning objectives",
                "learning objective",
                "course outcomes",
                "course outcome",
                "study roadmap",
                "concepts to master",
                "concept to master",
                "what should i learn",
                "what should i study",
            ]
        ):
            return "learning_objectives"

        # ======================================================
        # COMPARISON
        # ======================================================

        if (
            re.search(r"\bcompare\b", question)
            or re.search(r"\bcomparison\b", question)
            or re.search(
                r"\bdifference(?:s)?\s+between\b",
                question,
            )
            or re.search(r"\bversus\b", question)
            or re.search(r"\bvs\.?\b", question)
        ):
            return "comparison"

        # ======================================================
        # PROGRAMMING
        # ======================================================

        if (
            re.search(
                r"\b(write|create|generate|develop|implement|code)\b"
                r".*\b(code|program|script|function|class|algorithm)\b",
                question,
            )
            or re.search(
                r"\b(code|program|script)\b"
                r".*\b(in|using|with)\b"
                r"\b(python|java|c\+\+|cpp|c|javascript|"
                r"typescript|sql|r|matlab|php)\b",
                question,
            )
            or any(
                phrase in question
                for phrase in [
                    "write code",
                    "write a program",
                    "write program",
                    "python code",
                    "java code",
                    "c++ code",
                    "c code",
                    "javascript code",
                    "typescript code",
                    "sql query",
                    "implement in python",
                    "implement in java",
                    "implement in c++",
                    "implement in c",
                    "implement using python",
                    "implement using java",
                    "implement using c++",
                    "dry run",
                    "debug this code",
                    "debug the code",
                    "find the bug in this code",
                    "find the error in this code",
                ]
            )
        ):
            return "programming"

        # ======================================================
        # MATHEMATICAL / PROBLEM SOLVING
        # ======================================================

        if (
            re.search(r"\bsolve\b", question)
            or re.search(r"\bcalculate\b", question)
            or re.search(r"\bderive\b", question)
            or re.search(r"\bderivation\b", question)
            or re.search(
                r"\bsolve\s+the\s+equation\b",
                question,
            )
            or re.search(
                r"\bcalculate\s+the\b",
                question,
            )
            or re.search(
                r"\bfind\s+the\s+(value|answer|solution)\b",
                question,
            )
            or any(
                phrase in question
                for phrase in [
                    "numerical",
                    "numerical problem",
                    "numerical problems",
                    "numerical example",
                    "numerical examples",
                    "practice problem",
                    "practice problems",
                ]
            )
        ):
            return "mathematical"

        # ======================================================
        # EXTERNAL RESOURCES
        # ======================================================

        if any(
            phrase in question
            for phrase in [
                "youtube",
                "video",
                "videos",
                "watch",
                "lecture",
                "lectures",
                "tutorial",
                "tutorials",
                "khan academy",
                "nptel",
                "reference books",
                "reference book",
                "online resources",
                "online resource",
                "additional reading",
            ]
        ):
            return "external_resource"

        # ======================================================
        # EXPLANATION
        # ======================================================

        if any(
            phrase in question
            for phrase in [
                "explain",
                "explanation",
                "what is",
                "what are",
                "define",
                "definition",
                "describe",
                "description",
                "discuss",
                "how does",
                "how do",
                "how is",
                "how are",
                "why does",
                "why do",
                "why is",
                "why are",
            ]
        ):
            return "explanation"

        # ======================================================
        # GENERAL
        # ======================================================

        return "general"

    # ==========================================================
    # DIFFICULTY DETECTION
    # ==========================================================

    @staticmethod
    def _detect_difficulty(
        question: str,
        intent: str,
    ):
        """
        Estimate question difficulty.

        Explicit user instructions always have priority.
        """

        question = question.lower().strip()

        # ======================================================
        # EXPLICIT EASY
        # ======================================================

        if any(
            phrase in question
            for phrase in [
                "easy",
                "beginner level",
                "basic level",
                "basic",
                "simple",
            ]
        ):
            return "Easy"

        # ======================================================
        # EXPLICIT MEDIUM
        # ======================================================

        if any(
            phrase in question
            for phrase in [
                "medium",
                "intermediate",
                "moderate",
            ]
        ):
            return "Medium"

        # ======================================================
        # EXPLICIT HARD
        # ======================================================

        if any(
            phrase in question
            for phrase in [
                "hard",
                "difficult",
                "advanced level",
                "challenging",
                "complex",
            ]
        ):
            return "Hard"

        # ======================================================
        # BASIC QUESTION
        # ======================================================

        if any(
            phrase in question
            for phrase in [
                "define",
                "what is",
                "what are",
                "list",
                "enlist",
            ]
        ):
            return "Easy"

        # ======================================================
        # COMPARISON
        # ======================================================

        if any(
            phrase in question
            for phrase in [
                "compare",
                "comparison",
                "difference",
                "differences",
                "advantages",
                "disadvantages",
            ]
        ):
            return "Medium"

        # ======================================================
        # ADVANCED TASK
        # ======================================================

        if any(
            phrase in question
            for phrase in [
                "design",
                "prove",
                "derive",
                "derivation",
                "optimize",
                "optimization",
            ]
        ):
            return "Hard"

        # ======================================================
        # PROGRAMMING
        # ======================================================

        if intent == "programming":
            return "Medium"

        # ======================================================
        # MATHEMATICAL
        # ======================================================

        if intent == "mathematical":
            return "Medium"

        # ======================================================
        # DEFAULT
        # ======================================================

        return "Medium"
