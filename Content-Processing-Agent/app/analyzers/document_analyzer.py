"""
Document Analyzer

Analyzes cleaned text and extracts useful metadata.
"""

import re
from typing import Optional
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
        "AI": [
            "artificial intelligence",
            "ai",
            "machine learning",
            "deep learning",
            "neural network",
            "neural networks",
            "intelligent agent",
            "agent",
            "heuristic",
            "heuristics",
            "a* search",
            "minimax",
            "alpha-beta",
            "knowledge representation",
            "nlp",
            "natural language processing",
            "computer vision",
            "reinforcement learning",
            "supervised learning",
            "unsupervised learning",
            "perceptron",
            "genetic algorithm",
            "expert system",
            "state space",
            "adversarial search",
            "propositional logic",
            "first order logic",
            "inference engine",
            "bayes",
            "naive bayes",
            "decision tree",
            "clustering",
            "regression",
            "prompt engineering",
        ],

        "OOP": [
            "object oriented programming",
            "oop",
            "object oriented",
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
            "collection",
            "method overloading",
            "method overriding",
        ],

        "OS": [
            "operating system",
            "os",
            "process",
            "thread",
            "deadlock",
            "paging",
            "memory management",
            "virtual memory",
            "scheduler",
            "cpu scheduling",
            "kernel",
            "semaphore",
            "mutex",
            "critical section",
            "concurrency",
            "system call",
            "page replacement",
        ],

        "DBMS": [
            "database management system",
            "dbms",
            "database",
            "sql",
            "normalization",
            "1nf",
            "2nf",
            "3nf",
            "bcnf",
            "transaction",
            "acid properties",
            "entity",
            "attribute",
            "relation",
            "relational database",
            "table",
            "primary key",
            "foreign key",
            "er diagram",
            "join",
            "indexing",
        ],

        "CNS": [
            "cryptography",
            "network security",
            "cipher",
            "encryption",
            "decryption",
            "rsa",
            "aes",
            "des",
            "hashing",
            "sha",
            "firewall",
            "ssl",
            "tls",
            "digital signature",
            "authentication",
            "malware",
            "vulnerability",
            "cns",
            "public key",
            "private key",
            "network protocol",
            "ipsec",
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
            "ethernet",
            "subnet",
            "packet",
            "lan",
            "wan",
        ],

        "COA": [
            "computer organization",
            "computer architecture",
            "coa",
            "instruction set",
            "pipeline",
            "pipelining",
            "cache",
            "cache memory",
            "bus",
            "alu",
            "control unit",
            "microprocessor",
            "registers",
            "addressing mode",
            "dma",
            "interrupt",
            "risc",
            "cisc",
            "von neumann",
        ],

        "SE": [
            "software engineering",
            "se",
            "sdlc",
            "agile",
            "scrum",
            "waterfall",
            "software testing",
            "uml",
            "use case",
            "requirements engineering",
            "software design",
            "design pattern",
            "software architecture",
            "quality assurance",
            "verification",
            "validation",
            "maintenance",
            "devops",
        ],

        "ETC": [
            "effective technical communication",
            "etc",
            "technical communication",
            "presentation skills",
            "report writing",
            "communication skills",
            "group discussion",
            "interview skills",
            "resume writing",
            "business letter",
            "email etiquette",
            "body language",
            "listening skills",
        ],

        "DATA STRUCTURE": [
            "data structure",
            "data structures",
            "dsa",
            "array",
            "stack",
            "queue",
            "linked list",
            "tree",
            "binary tree",
            "binary search tree",
            "bst",
            "avl tree",
            "graph",
            "sorting",
            "bubble sort",
            "merge sort",
            "quick sort",
            "searching",
            "binary search",
            "recursion",
            "hash table",
            "heap",
            "trie",
            "time complexity",
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
            "binary tree",
        ],

        "Python": [
            "python",
            "list",
            "tuple",
            "dictionary",
            "lambda",
            "numpy",
            "pandas",
        ],
    }

    @staticmethod
    def analyze(text: str, selected_subject: Optional[str] = None) -> dict:

        if not text.strip():
            return {
                "subject": selected_subject or "General",
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

        keywords = []
        try:
            extractor = yake.KeywordExtractor(
                lan="en",
                n=2,
                top=15,
            )
            keyword_result = extractor.extract_keywords(text)
            keywords = [keyword for keyword, _ in keyword_result]
        except Exception as e:
            print(f"YAKE keyword extraction fallback: {e}")

        # -------------------------------------------------
        # Subject Classification
        # -------------------------------------------------

        lower_text = text.lower()
        scores = {}

        for subject_code, subject_keywords in DocumentAnalyzer.SUBJECT_KEYWORDS.items():
            score = 0
            for keyword in subject_keywords:
                kw_lower = keyword.lower()
                if len(kw_lower) <= 2:
                    # Require word boundaries for short abbreviations like 'ai', 'os', 'se'
                    score += len(re.findall(rf"\b{re.escape(kw_lower)}\b", lower_text))
                else:
                    score += lower_text.count(kw_lower)
            scores[subject_code] = score

        best_subject = max(scores, key=scores.get)

        if scores[best_subject] == 0:
            best_subject = "General"

        # If user explicitly provided a selected_subject, check if document is relevant to it
        if selected_subject:
            norm_selected = selected_subject.strip().upper()
            alias_map = {
                "ARTIFICIAL INTELLIGENCE": "AI",
                "OPERATING SYSTEM": "OS",
                "OBJECT ORIENTED PROGRAMMING": "OOP",
                "DATABASE MANAGEMENT SYSTEM": "DBMS",
                "CRYPTOGRAPHY AND NETWORK SECURITY": "CNS",
                "COMPUTER NETWORKS": "CNS",
                "CN": "CNS",
                "COMPUTER ORGANIZATION AND ARCHITECTURE": "COA",
                "SOFTWARE ENGINEERING": "SE",
                "EFFECTIVE TECHNICAL COMMUNICATION": "ETC",
                "DSA": "DATA STRUCTURE",
            }
            target_key = alias_map.get(norm_selected, norm_selected)
            # If the document has positive matches for the selected subject, or is general
            if scores.get(target_key, 0) > 0 or best_subject in ("General", "Unknown"):
                best_subject = selected_subject

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
            "scores": scores,
        }