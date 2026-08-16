
"""
Subject Validator

Responsibilities:

1. Validate uploaded documents against the selected subject.
2. Validate student questions against the selected subject.
3. Avoid unnecessary LLM calls for normal question validation.

IMPORTANT:
- Document validation uses Gemini because document classification
  can require semantic understanding.
- Question validation is primarily rule-based to reduce Gemini
  API usage and avoid unnecessary quota consumption.
"""

import os
import re

from dotenv import load_dotenv
from google import genai

from app.core.config import settings


load_dotenv()


# ==========================================================
# Gemini Client
# ==========================================================

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# ==========================================================
# Subject Definitions
# ==========================================================

SUBJECT_NAMES = {
    "OS": "Operating System",
    "OOP": "Object Oriented Programming",
    "CNS": "Cryptography and Network Security",
    "DBMS": "Database Management System",
    "SE": "Software Engineering",
    "AI": "Artificial Intelligence",
    "ETC": "Effective Technical Communication",
    "COA": "Computer Organization and Architecture",
    "DATA STRUCTURE": "Data Structure",
}


# ==========================================================
# Subject Keywords
# ==========================================================

SUBJECT_KEYWORDS = {

    "OS": {
        "operating system",
        "operating systems",
        "process",
        "processes",
        "process scheduling",
        "cpu scheduling",
        "scheduling",
        "thread",
        "threads",
        "multithreading",
        "deadlock",
        "deadlocks",
        "memory management",
        "virtual memory",
        "paging",
        "segmentation",
        "page replacement",
        "file system",
        "file systems",
        "disk scheduling",
        "disk management",
        "process synchronization",
        "semaphore",
        "semaphores",
        "mutex",
        "critical section",
        "system call",
        "system calls",
        "kernel",
        "multiprogramming",
        "multitasking",
        "cpu utilization",
        "context switching",
        "context switch",
    },

    "OOP": {
        "object oriented programming",
        "object-oriented programming",
        "oop",
        "class",
        "classes",
        "object",
        "objects",
        "inheritance",
        "polymorphism",
        "encapsulation",
        "abstraction",
        "constructor",
        "constructors",
        "destructor",
        "method overloading",
        "method overriding",
        "overloading",
        "overriding",
        "interface",
        "interfaces",
        "java",
        "c++",
        "python oop",
    },

    "CNS": {
        "cryptography",
        "cryptographic",
        "network security",
        "cyber security",
        "cybersecurity",
        "encryption",
        "decryption",
        "cipher",
        "ciphers",
        "rsa",
        "aes",
        "des",
        "diffie hellman",
        "diffie-hellman",
        "digital signature",
        "digital signatures",
        "hashing",
        "hash function",
        "message authentication",
        "authentication",
        "firewall",
        "malware",
        "phishing",
        "security attack",
        "security attacks",
        "ssl",
        "tls",
        "ipsec",
    },

    "DBMS": {
        "database",
        "databases",
        "dbms",
        "database management",
        "relational database",
        "relational databases",
        "sql",
        "mysql",
        "normalization",
        "normal forms",
        "1nf",
        "2nf",
        "3nf",
        "bcnf",
        "functional dependency",
        "functional dependencies",
        "primary key",
        "foreign key",
        "candidate key",
        "super key",
        "database schema",
        "schema",
        "er diagram",
        "entity relationship",
        "transaction",
        "transactions",
        "acid properties",
        "acid",
        "concurrency control",
        "database indexing",
        "indexing",
        "query processing",
    },

    "SE": {
        "software engineering",
        "software development",
        "software process",
        "software life cycle",
        "sdlc",
        "waterfall model",
        "agile",
        "scrum",
        "spiral model",
        "prototype model",
        "requirements engineering",
        "software requirements",
        "functional requirement",
        "non functional requirement",
        "software design",
        "software testing",
        "unit testing",
        "integration testing",
        "system testing",
        "maintenance",
        "software project management",
        "risk management",
        "software metrics",
        "uml",
        "use case diagram",
        "class diagram",
    },

    "AI": {
        "artificial intelligence",
        "artificial intelligence",
        "ai",
        "machine learning",
        "ml",
        "deep learning",
        "neural network",
        "neural networks",
        "cnn",
        "rnn",
        "transformer",
        "natural language processing",
        "nlp",
        "computer vision",
        "expert system",
        "expert systems",
        "knowledge representation",
        "search algorithm",
        "heuristic search",
        "a star",
        "a*",
        "classification",
        "regression",
        "clustering",
        "reinforcement learning",
        "supervised learning",
        "unsupervised learning",
    },

    "ETC": {
        "technical communication",
        "effective technical communication",
        "communication skills",
        "technical writing",
        "report writing",
        "letter writing",
        "business communication",
        "professional communication",
        "presentation skills",
        "presentation",
        "public speaking",
        "group discussion",
        "gd",
        "interview skills",
        "resume writing",
        "email writing",
        "formal letter",
        "informal letter",
        "communication process",
        "barriers to communication",
        "non verbal communication",
        "verbal communication",
    },

    "COA": {
        "computer organization",
        "computer architecture",
        "coa",
        "cpu organization",
        "processor organization",
        "instruction set",
        "instruction cycle",
        "register",
        "registers",
        "alu",
        "arithmetic logic unit",
        "control unit",
        "cache memory",
        "cache",
        "memory hierarchy",
        "main memory",
        "secondary memory",
        "input output",
        "i/o",
        "io organization",
        "pipeline",
        "pipelining",
        "risc",
        "cisc",
        "addressing mode",
        "addressing modes",
    },

    "DATA STRUCTURE": {
        "data structure",
        "data structures",
        "array",
        "arrays",
        "linked list",
        "linked lists",
        "stack",
        "stacks",
        "queue",
        "queues",
        "deque",
        "tree",
        "trees",
        "binary tree",
        "binary search tree",
        "bst",
        "heap",
        "heaps",
        "hash table",
        "hashing",
        "graph",
        "graphs",
        "graph traversal",
        "bfs",
        "dfs",
        "sorting",
        "searching",
        "binary search",
        "linear search",
        "algorithm",
        "algorithms",
        "time complexity",
        "space complexity",
        "big o",
        "big-o",
    },
}


# ==========================================================
# Normalize Subject
# ==========================================================

def normalize_subject(subject: str) -> str:
    """
    Converts subject codes/names into a standard subject code.
    """

    if not subject:
        return ""

    subject_clean = subject.strip().lower()

    aliases = {
        "operating system": "OS",
        "operating systems": "OS",
        "os": "OS",

        "object oriented programming": "OOP",
        "object-oriented programming": "OOP",
        "oop": "OOP",

        "cryptography and network security": "CNS",
        "cryptography & network security": "CNS",
        "cns": "CNS",

        "database management system": "DBMS",
        "database management systems": "DBMS",
        "dbms": "DBMS",

        "software engineering": "SE",
        "se": "SE",

        "artificial intelligence": "AI",
        "ai": "AI",

        "effective technical communication": "ETC",
        "technical communication": "ETC",
        "etc": "ETC",

        "computer organization and architecture": "COA",
        "computer organization": "COA",
        "computer architecture": "COA",
        "coa": "COA",

        "data structure": "DATA STRUCTURE",
        "data structures": "DATA STRUCTURE",
        "data structure and algorithms": "DATA STRUCTURE",
        "dsa": "DATA STRUCTURE",
    }

    return aliases.get(
        subject_clean,
        subject.strip().upper(),
    )


# ==========================================================
# Get Full Subject Name
# ==========================================================

def get_subject_name(subject: str) -> str:

    normalized = normalize_subject(subject)

    return SUBJECT_NAMES.get(
        normalized,
        subject,
    )


# ==========================================================
# Validate Uploaded Document Subject
# ==========================================================

def validate_document_subject(
    selected_subject: str,
    document_text: str,
) -> tuple[bool, str]:
    """
    Uses Gemini to determine whether an uploaded document
    belongs to the selected academic subject.

    This function still uses Gemini because a document can
    contain many different concepts and simple keyword
    matching is less reliable for document-level validation.
    """

    if not document_text or not document_text.strip():
        return False, "Unknown"

    selected_subject_name = get_subject_name(
        selected_subject
    )

    sample = document_text[:5000]

    prompt = f"""
You are an academic document classifier.

Selected Subject:
{selected_subject_name}

Document Content:
{sample}

Task:

Determine whether this document primarily belongs to
the selected subject.

Consider the overall academic topic rather than isolated
words.

Answer ONLY in this format:

YES
Detected Subject: <subject>

OR

NO
Detected Subject: <subject>

Do not provide any explanation.
"""

    try:

        response = client.models.generate_content(
            model=settings.LLM_MODEL,
            contents=prompt,
        )

        text = (
            response.text.strip()
            if response.text
            else ""
        )

        print(
            "\n========== SUBJECT VALIDATION =========="
        )
        print(text)
        print(
            "========================================\n"
        )

        lines = text.splitlines()

        if not lines:
            return False, "Unknown"

        decision = lines[0].strip().upper()

        detected = "Unknown"

        for line in lines:

            if line.lower().startswith(
                "detected subject"
            ):

                if ":" in line:

                    detected = line.split(
                        ":",
                        1
                    )[1].strip()

                break

        return decision == "YES", detected

    except Exception as e:

        print(
            "\n========== DOCUMENT VALIDATION ERROR =========="
        )

        print(e)

        print(
            "===============================================\n"
        )

        # Do not crash the entire application because
        # subject validation failed.

        return True, selected_subject_name


# ==========================================================
# Rule-Based Question Subject Detection
# ==========================================================

def detect_question_subject(
    question: str,
) -> tuple[str, int]:
    """
    Detect the most likely subject using academic keywords.

    Returns:
        (subject_code, score)
    """

    if not question:
        return "Unknown", 0

    question_lower = question.lower()

    scores = {
        subject: 0
        for subject in SUBJECT_KEYWORDS
    }

    for subject, keywords in SUBJECT_KEYWORDS.items():

        for keyword in keywords:

            # Multi-word phrases are checked directly.
            if " " in keyword or "-" in keyword:

                if keyword in question_lower:
                    scores[subject] += 2

            else:

                pattern = rf"\b{re.escape(keyword)}\b"

                if re.search(
                    pattern,
                    question_lower
                ):
                    scores[subject] += 1

    if not scores:
        return "Unknown", 0

    detected_subject = max(
        scores,
        key=scores.get,
    )

    highest_score = scores[
        detected_subject
    ]

    if highest_score == 0:
        return "Unknown", 0

    return detected_subject, highest_score


# ==========================================================
# Validate Question Subject
# ==========================================================

def validate_question_subject(
    selected_subject: str,
    question: str,
) -> tuple[bool, str]:
    """
    Validates whether a student's question belongs to
    the selected academic subject.

    IMPORTANT:

    This function is intentionally rule-based.

    It does NOT call Gemini.

    This prevents every user question from consuming
    one additional Gemini API request.

    Returns:
        (True, selected subject)
        (False, detected subject)
    """

    if not question or not question.strip():

        return False, "Unknown"

    selected_code = normalize_subject(
        selected_subject
    )

    selected_name = get_subject_name(
        selected_subject
    )

    detected_code, score = detect_question_subject(
        question
    )

    print(
        "\n========== QUESTION SUBJECT VALIDATION =========="
    )

    print(
        "Selected Subject :",
        selected_name,
    )

    print(
        "Detected Subject :",
        get_subject_name(detected_code)
        if detected_code != "Unknown"
        else "Unknown",
    )

    print(
        "Keyword Score    :",
        score,
    )

    print(
        "Question         :",
        question,
    )

    print(
        "=================================================\n"
    )

    # ------------------------------------------------------
    # Case 1:
    # No recognizable academic keyword.
    #
    # We allow vague/general questions because questions
    # such as:
    #
    # "Explain this topic"
    # "Explain the concept"
    #
    # cannot reliably be classified from keywords alone.
    # ------------------------------------------------------

    if detected_code == "Unknown":

        return True, selected_name

    # ------------------------------------------------------
    # Case 2:
    # Detected subject matches selected subject.
    # ------------------------------------------------------

    if detected_code == selected_code:

        return True, selected_name

    # ------------------------------------------------------
    # Case 3:
    # Question clearly belongs to another subject.
    # ------------------------------------------------------

    return False, get_subject_name(
        detected_code
    )


# ==========================================================
# Subject Validation Message
# ==========================================================

def get_subject_validation_message(
    selected_subject: str,
) -> str:

    subject_name = get_subject_name(
        selected_subject
    )

    return (
        f"Please ask a question relevant to "
        f"{subject_name}."
    )
