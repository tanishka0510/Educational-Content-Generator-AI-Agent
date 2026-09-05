"""
Study Plan Service (Weekly Personalized Learning Schedule & ReportLab PDF Generator)

Project: Educational Content Generator AI
Module: Orchestrator Agent (Gateway)
"""

import json
from io import BytesIO
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from database.models import User, QuizResult, FlashcardProgress, FlashcardAttempt
from database.crud import get_user_quizzes, get_user_flashcard_progress, get_user_flashcard_attempts


ALL_SUBJECTS = [
    "OS",
    "OOP",
    "DBMS",
    "CNS",
    "SE",
    "AI",
    "ETC",
    "COA",
    "DATA STRUCTURE"
]

SUBJECT_FULL_NAMES = {
    "OS": "Operating System",
    "OOP": "Object Oriented Programming",
    "DBMS": "Database Management System",
    "CNS": "Cryptography and Network Security",
    "SE": "Software Engineering",
    "AI": "Artificial Intelligence",
    "ETC": "Effective Technical Communication",
    "COA": "Computer Organization and Architecture",
    "DATA STRUCTURE": "Data Structure"
}

SUBJECT_CORE_TOPICS = {
    "OS": {
        "weak_fallback": [
            "Process Synchronization & Semaphores",
            "Deadlock Prevention & Banker's Algorithm",
            "Virtual Memory & Paging Mechanisms"
        ],
        "practice_fallback": [
            "CPU Scheduling Algorithms (Round Robin, SRTF)",
            "Page Replacement Algorithms (LRU, Optimal)",
            "File System Implementation & Disk Scheduling"
        ],
        "revision_topics": [
            "Critical Section Problem & Mutex Locks",
            "Virtual Memory Address Translation & TLB",
            "Inter-Process Communication (Pipes & Sockets)",
            "System Calls & Kernel Privilege Levels"
        ],
        "improvement_advice": "Focus on step-by-step deadlock state matrices and semaphore wait/signal execution flow."
    },
    "OOP": {
        "weak_fallback": [
            "Dynamic Polymorphism & Virtual Tables",
            "Abstract Classes vs Pure Interfaces",
            "Operator Overloading & Copy Constructors"
        ],
        "practice_fallback": [
            "Inheritance Access Modifiers (public/protected/private)",
            "Encapsulation & Getter/Setter Invariants",
            "Exception Handling Patterns & Resource Cleanup"
        ],
        "revision_topics": [
            "SOLID Object-Oriented Design Principles",
            "Virtual Destructors & Memory Leak Prevention",
            "Method Overloading vs Method Overriding",
            "Composition vs Inheritance Trade-offs"
        ],
        "improvement_advice": "Draw class hierarchy diagrams and trace virtual table (vtable) method dispatch."
    },
    "DBMS": {
        "weak_fallback": [
            "Database Normalization (3NF, BCNF Decomposition)",
            "Two-Phase Locking (2PL) & Serializability",
            "B-Trees & B+ Tree Indexing Operations"
        ],
        "practice_fallback": [
            "Complex SQL Subqueries & Outer Joins",
            "Transaction ACID Properties & Write-Ahead Logging",
            "Entity-Relationship to Relational Schema Mapping"
        ],
        "revision_topics": [
            "Functional Dependencies & Minimal Cover",
            "Clustered vs Non-Clustered Indexes",
            "Deadlock Detection & Wait-For Graphs",
            "Relational Algebra Operators & Query Optimization"
        ],
        "improvement_advice": "Practice identifying candidate keys and decomposing schemas to eliminate anomalies."
    },
    "CNS": {
        "weak_fallback": [
            "Asymmetric Key Cryptography (RSA Algorithm)",
            "Diffie-Hellman Key Exchange Protocol",
            "Digital Signatures & Hash Authentication (HMAC)"
        ],
        "practice_fallback": [
            "Symmetric Ciphers (DES vs AES Modes)",
            "Public Key Infrastructure (PKI & X.509 Certificates)",
            "SSL/TLS Handshake Protocol Stages"
        ],
        "revision_topics": [
            "Symmetric vs Asymmetric Cryptography Trade-offs",
            "Cryptographic Hash Properties (SHA-256)",
            "Common Network Attacks (MITM, Replay, Spoofing)",
            "Firewalls, Packet Filtering & Intrusion Detection"
        ],
        "improvement_advice": "Trace modular arithmetic in RSA (Euler's Totient function) and Diffie-Hellman step-by-step."
    },
    "SE": {
        "weak_fallback": [
            "Software Testing Strategies (Black vs White Box, Cyclomatic Complexity)",
            "Agile Scrum Ceremonies vs Waterfall Lifecycles",
            "Software Architectural Design Patterns"
        ],
        "practice_fallback": [
            "Software Requirements Specification (SRS) & Use Cases",
            "UML Class & Sequence Diagram Modeling",
            "Software Maintenance & Code Refactoring Techniques"
        ],
        "revision_topics": [
            "Software Quality Assurance & ISO/CMMI Standards",
            "CI/CD Pipelines & Version Control Workflows",
            "COCOMO Estimation Model & Risk Management",
            "Cohesion vs Coupling in Component Architecture"
        ],
        "improvement_advice": "Calculate cyclomatic complexity on code samples and map requirements directly to test suites."
    },
    "AI": {
        "weak_fallback": [
            "Informed Search Algorithms (A* Heuristics & Admissibility)",
            "Minimax Algorithm with Alpha-Beta Pruning",
            "Artificial Neural Networks & Backpropagation Math"
        ],
        "practice_fallback": [
            "Propositional & First-Order Predicate Logic",
            "Uncertainty Reasoning & Bayesian Networks",
            "Machine Learning Evaluation Metrics (Precision, Recall, F1)"
        ],
        "revision_topics": [
            "Uninformed vs Informed Search Comparison",
            "Constraint Satisfaction Problems (CSP & Backtracking)",
            "Supervised vs Unsupervised vs Reinforcement Learning",
            "Knowledge Representation & Semantic Networks"
        ],
        "improvement_advice": "Practice pruning game trees by hand and verify whether heuristic functions satisfy admissibility."
    },
    "COA": {
        "weak_fallback": [
            "Instruction Pipelining & Hazard Resolution (Data/Control)",
            "Cache Memory Mapping (Direct, Associative, Set-Associative)",
            "Microprogrammed vs Hardwired Control Unit Design"
        ],
        "practice_fallback": [
            "Computer Arithmetic (Booth's Algorithm & IEEE 754 Floating Point)",
            "Memory Hierarchy & Hit/Miss Latency Calculations",
            "Interrupt Handling & Direct Memory Access (DMA)"
        ],
        "revision_topics": [
            "Von Neumann vs Harvard Computer Architectures",
            "Addressing Modes (Immediate, Direct, Indirect, Indexed)",
            "Branch Prediction Techniques & Pipeline Stalls",
            "Bus Arbitration & IO Organization"
        ],
        "improvement_advice": "Work through concrete cache block address split examples (Tag, Set, Word offset) and pipeline timing charts."
    },
    "DATA STRUCTURE": {
        "weak_fallback": [
            "Self-Balancing Trees (AVL Rotations & Red-Black Invariants)",
            "Graph Shortest Path Algorithms (Dijkstra, Bellman-Ford)",
            "Dynamic Programming Memoization & State Transitions"
        ],
        "practice_fallback": [
            "Stack & Queue Implementations and Applications",
            "Binary Search Trees (Insertion, Deletion, Traversals)",
            "Hash Table Collision Resolution (Chaining vs Open Addressing)"
        ],
        "revision_topics": [
            "Asymptotic Complexity Analysis (Big-O, Omega, Theta)",
            "Divide and Conquer Algorithms (MergeSort, QuickSort)",
            "Graph Traversals (BFS, DFS) & Topological Sorting",
            "Minimum Spanning Trees (Prim's & Kruskal's Algorithms)"
        ],
        "improvement_advice": "Trace tree rotations on unbalanced BSTs and write DP recurrence relations on paper before coding."
    },
    "ETC": {
        "weak_fallback": [
            "Technical Report Structure & Executive Summaries",
            "Group Discussion Leadership & Conflict Resolution",
            "Business Communication Etiquette & Formal Proposals"
        ],
        "practice_fallback": [
            "Oral Presentation Delivery & Slide Visual Design",
            "Professional Email Composition & Technical Inquiries",
            "Technical Vocabulary Precision & Coherence"
        ],
        "revision_topics": [
            "The 7 Cs of Effective Business Communication",
            "Non-Verbal Cues, Kinesics & Active Listening",
            "Resume Writing & Interview Communication Strategies",
            "Overcoming Psychological & Environmental Communication Barriers"
        ],
        "improvement_advice": "Practice writing concise executive summaries and structuring answers with the STAR technique."
    }
}


# ==========================================================
# Study Plan Generation Engine
# ==========================================================

def generate_weekly_study_plan(db: Session, user: User, metrics: Dict[str, Any]) -> Dict[str, Any]:
    """
    Synthesizes the student's learning diagnostics, quiz error history,
    flashcard retention, and subject mastery tiers to produce a concrete,
    personalized 7-day study plan with subject-wise topic suggestions.
    """
    user_id = user.id
    quizzes = get_user_quizzes(db, user_id=user_id)
    flashcards = get_user_flashcard_progress(db, user_id=user_id)
    flashcard_attempts = get_user_flashcard_attempts(db, user_id=user_id)

    # 1. Parse Missed Questions & Specific Error Topics
    missed_questions: List[Dict[str, Any]] = []
    missed_topics_by_subject: Dict[str, List[str]] = {}

    for q in quizzes:
        if q.answers_detail:
            try:
                answers = json.loads(q.answers_detail) if isinstance(q.answers_detail, str) else q.answers_detail
                if isinstance(answers, list):
                    for a in answers:
                        if not a.get("is_correct"):
                            q_text = (a.get("question") or "").strip()
                            if q_text:
                                item = {
                                    "question": q_text,
                                    "subject": q.subject,
                                    "topic": q.topic or (a.get("topic") if isinstance(a, dict) else "") or "General",
                                    "selected_answer": a.get("selected_answer", ""),
                                    "correct_answer": a.get("correct_answer", ""),
                                    "explanation": a.get("explanation", "")
                                }
                                missed_questions.append(item)
                                sub_key = q.subject
                                if sub_key not in missed_topics_by_subject:
                                    missed_topics_by_subject[sub_key] = []
                                top_name = item["topic"]
                                if top_name and top_name != "General" and top_name not in missed_topics_by_subject[sub_key]:
                                    missed_topics_by_subject[sub_key].append(top_name)
            except Exception:
                pass

    # 2. Extract Hard Flashcards & Struggling Topics
    hard_flashcard_topics: Dict[str, int] = {}
    for att in flashcard_attempts:
        if att.hard_count > 0 and att.topic:
            hard_flashcard_topics[att.topic] = hard_flashcard_topics.get(att.topic, 0) + att.hard_count

    # 3. Categorize Subject Proficiencies
    subject_stats = metrics.get("subject_stats", {})
    weak_subjects: List[str] = []
    practice_subjects: List[str] = []
    strong_subjects: List[str] = []
    untested_subjects: List[str] = []

    for sub in ALL_SUBJECTS:
        st = subject_stats.get(sub, {})
        q_count = st.get("quizzes_taken", 0)
        avg = st.get("quiz_average", 0.0)
        if q_count == 0:
            untested_subjects.append(sub)
        elif avg < 70.0:
            weak_subjects.append(sub)
        elif avg < 85.0:
            practice_subjects.append(sub)
        else:
            strong_subjects.append(sub)

    # Sort weak subjects by lowest score first
    weak_subjects.sort(key=lambda s: subject_stats.get(s, {}).get("quiz_average", 0.0))

    # Determine primary and secondary focus subjects
    primary_weak_subject = weak_subjects[0] if weak_subjects else (practice_subjects[0] if practice_subjects else (ALL_SUBJECTS[0]))
    secondary_weak_subject = weak_subjects[1] if len(weak_subjects) > 1 else (
        practice_subjects[0] if practice_subjects and practice_subjects[0] != primary_weak_subject else (
            untested_subjects[0] if untested_subjects else ALL_SUBJECTS[1]
        )
    )

    # 4. Formulate Concrete Priority Weak Points & How to Improve
    priority_weak_points: List[Dict[str, Any]] = []

    # A. Specific missed question concepts
    if missed_questions:
        # Group by subject and pick up to 3 notable concepts
        missed_by_sub: Dict[str, List[Dict[str, Any]]] = {}
        for mq in missed_questions:
            missed_by_sub.setdefault(mq["subject"], []).append(mq)

        for sub, qlist in list(missed_by_sub.items())[:3]:
            sub_name = SUBJECT_FULL_NAMES.get(sub, sub)
            sample_q = qlist[0]
            core_info = SUBJECT_CORE_TOPICS.get(sub, {})
            advice = core_info.get("improvement_advice", "Review definitions, verify key formulas, and retake the topic quiz.")
            
            topics_list = list(set([q["topic"] for q in qlist if q["topic"] and q["topic"] != "General"]))
            topic_str = f" ({', '.join(topics_list)})" if topics_list else ""
            
            priority_weak_points.append({
                "subject": sub,
                "subject_name": sub_name,
                "issue": f"{len(qlist)} question(s) answered incorrectly in {sub_name}{topic_str}.",
                "example_concept": sample_q["question"][:120] + ("..." if len(sample_q["question"]) > 120 else ""),
                "improvement_strategy": advice,
                "priority_level": "High"
            })

    # B. Subjects with low scores but no detailed questions parsed
    for sub in weak_subjects:
        if not any(wp["subject"] == sub for wp in priority_weak_points):
            sub_name = SUBJECT_FULL_NAMES.get(sub, sub)
            st = subject_stats.get(sub, {})
            core_info = SUBJECT_CORE_TOPICS.get(sub, {})
            fallback_topics = core_info.get("weak_fallback", ["Core Principles"])
            priority_weak_points.append({
                "subject": sub,
                "subject_name": sub_name,
                "issue": f"Overall quiz average is currently {st.get('quiz_average', 0)}% (Needs Practice tier).",
                "example_concept": f"Challenging areas include {', '.join(fallback_topics[:2])}.",
                "improvement_strategy": core_info.get("improvement_advice", "Study foundational diagrams, review comparison tables, and test recall."),
                "priority_level": "High"
            })

    # C. If no weaknesses found (brand new student or high performer)
    if not priority_weak_points:
        if len(quizzes) == 0:
            priority_weak_points.append({
                "subject": primary_weak_subject,
                "subject_name": SUBJECT_FULL_NAMES.get(primary_weak_subject, primary_weak_subject),
                "issue": "No baseline quiz benchmarks established yet.",
                "example_concept": "Foundational syllabus coverage required across core engineering subjects.",
                "improvement_strategy": "Complete diagnostic quizzes in Operating Systems and Data Structures to map your knowledge baseline.",
                "priority_level": "Moderate"
            })
        else:
            priority_weak_points.append({
                "subject": primary_weak_subject,
                "subject_name": SUBJECT_FULL_NAMES.get(primary_weak_subject, primary_weak_subject),
                "issue": "Strong baseline performance across active topics! High-tier mastery maintained.",
                "example_concept": "Advanced edge cases and time-pressured hard difficulty questions.",
                "improvement_strategy": "Challenge yourself with 'Hard' difficulty quizzes and multi-concept synthesis problems.",
                "priority_level": "Moderate"
            })

    # 5. Build Comprehensive Subject-Wise Recommendations (3 Tracks)
    # Track 1: Topics needing improvement
    # Track 2: Topics needing consistent practice
    # Track 3: Important high-yield topics to revise
    subject_wise_recommendations: List[Dict[str, Any]] = []

    # Order: active weak subjects first, then practice, then strong, then untested
    display_order = weak_subjects + practice_subjects + strong_subjects + [s for s in ALL_SUBJECTS if s in untested_subjects]
    seen_subs = set()
    ordered_subs = []
    for s in display_order:
        if s not in seen_subs and s in ALL_SUBJECTS:
            seen_subs.add(s)
            ordered_subs.append(s)

    for sub in ordered_subs:
        st = subject_stats.get(sub, {})
        core_info = SUBJECT_CORE_TOPICS.get(sub, {})
        sub_name = SUBJECT_FULL_NAMES.get(sub, sub)
        
        # Track 1: Topics Needing Improvement
        user_missed = missed_topics_by_subject.get(sub, [])
        if user_missed:
            improvement_topics = user_missed[:3]
        elif sub in weak_subjects:
            improvement_topics = core_info.get("weak_fallback", [])[:3]
        elif sub in untested_subjects:
            improvement_topics = [f"Initial syllabus orientation: {core_info.get('weak_fallback', ['Basics'])[0]}"]
        else:
            improvement_topics = [f"Advanced applications in {core_info.get('weak_fallback', ['Edge Cases'])[0]}"]

        # Track 2: Topics Needing Consistent Practice
        practice_topics = core_info.get("practice_fallback", [])[:3]

        # Track 3: Important Topics to Revise
        revision_topics = core_info.get("revision_topics", [])[:4]

        # Specific action plans
        remediation_action = (
            f"Review theoretical principles, consult the AI Chat Assistant for step-by-step breakdowns, "
            f"and re-take a 5-question quiz at Medium difficulty."
        )
        practice_action = (
            f"Perform a 10-minute active recall flashcard drill and practice solving 5 practice questions "
            f"to strengthen speed and retention."
        )
        revision_action = (
            f"Prepare a concise one-page formula / diagram cheat sheet and revise high-yield exam invariants."
        )

        subject_wise_recommendations.append({
            "subject": sub,
            "subject_name": sub_name,
            "status_tier": st.get("tier", "Not Started"),
            "quizzes_taken": st.get("quizzes_taken", 0),
            "quiz_average": st.get("quiz_average", 0.0),
            "topics_needing_improvement": improvement_topics,
            "improvement_action": remediation_action,
            "topics_needing_practice": practice_topics,
            "practice_action": practice_action,
            "important_revision_topics": revision_topics,
            "revision_action": revision_action
        })

    # 6. Build the Personalized 7-Day Day-by-Day Study Plan
    # Monday to Sunday structured schedule
    days_data = [
        {
            "day_number": 1,
            "day_name": "Day 1 (Monday)",
            "subject": primary_weak_subject,
            "subject_name": SUBJECT_FULL_NAMES.get(primary_weak_subject, primary_weak_subject),
            "session_title": "Targeted Remediation & Core Fundamentals",
            "focus_topics": (missed_topics_by_subject.get(primary_weak_subject) or SUBJECT_CORE_TOPICS.get(primary_weak_subject, {}).get("weak_fallback", []))[:2],
            "learning_activity": "Missed Concept Review & AI Explanations",
            "estimated_minutes": 50,
            "steps": [
                "Review the specific questions missed in recent quizzes and note down core misconceptions.",
                "Ask the AI Assistant for detailed real-world analogies and step-by-step concept explanations.",
                "Write down a 3-bullet takeaway summary before moving on to practice."
            ]
        },
        {
            "day_number": 2,
            "day_name": "Day 2 (Tuesday)",
            "subject": secondary_weak_subject,
            "subject_name": SUBJECT_FULL_NAMES.get(secondary_weak_subject, secondary_weak_subject),
            "session_title": "Deep Remediation & Algorithmic Walkthrough",
            "focus_topics": (missed_topics_by_subject.get(secondary_weak_subject) or SUBJECT_CORE_TOPICS.get(secondary_weak_subject, {}).get("weak_fallback", []))[:2],
            "learning_activity": "Interactive Walkthrough & Step-by-Step Problem Solving",
            "estimated_minutes": 45,
            "steps": [
                "Work through 2-3 standard problems (e.g. state matrices, address translation, or tree rotations).",
                "Generate comparison tables between confusing terms to clearly distinguish edge cases.",
                "Test comprehension with a short 5-question targeted quiz."
            ]
        },
        {
            "day_number": 3,
            "day_name": "Day 3 (Wednesday)",
            "subject": "Spaced Repetition Drill",
            "subject_name": "Cross-Subject Flashcards",
            "session_title": "Active Recall & Spaced Repetition Reinforcement",
            "focus_topics": [f"{primary_weak_subject} Flashcards", f"{secondary_weak_subject} Key Definitions"],
            "learning_activity": "Timed Spaced Repetition Flashcard Drill",
            "estimated_minutes": 40,
            "steps": [
                "Open the Flashcards module and complete all due cards scheduled for review.",
                "Pay special attention to cards previously marked 'Hard'; rate them honestly.",
                "Review audio pronunciation and summaries using the Multimedia Voice assistant."
            ]
        },
        {
            "day_number": 4,
            "day_name": "Day 4 (Thursday)",
            "subject": practice_subjects[0] if practice_subjects else (ALL_SUBJECTS[2] if len(ALL_SUBJECTS) > 2 else "DBMS"),
            "subject_name": SUBJECT_FULL_NAMES.get(practice_subjects[0] if practice_subjects else "DBMS", "Database Management System"),
            "session_title": "High-Yield Revision: Core Exam Essentials",
            "focus_topics": SUBJECT_CORE_TOPICS.get(practice_subjects[0] if practice_subjects else "DBMS", {}).get("revision_topics", [])[:3],
            "learning_activity": "High-Yield Summary Notes & Architecture Mapping",
            "estimated_minutes": 45,
            "steps": [
                "Revisit high-yield foundational concepts (e.g. ACID, Normalization, Virtual Memory, Big-O).",
                "Construct a one-page visual mental map connecting key components and protocols.",
                "Explain the architecture out loud using the Feynman technique."
            ]
        },
        {
            "day_number": 5,
            "day_name": "Day 5 (Friday)",
            "subject": primary_weak_subject,
            "subject_name": SUBJECT_FULL_NAMES.get(primary_weak_subject, primary_weak_subject),
            "session_title": "Applied Practice Challenge: Timed Testing",
            "focus_topics": SUBJECT_CORE_TOPICS.get(primary_weak_subject, {}).get("practice_fallback", [])[:2],
            "learning_activity": "Timed Diagnostic Quiz Session (Medium & Hard)",
            "estimated_minutes": 50,
            "steps": [
                "Take a timed 10-question quiz at Medium or Hard difficulty on your primary remediation subject.",
                "Examine explanations immediately for every question answered incorrectly.",
                "Verify whether previously remediated questions are now answered accurately."
            ]
        },
        {
            "day_number": 6,
            "day_name": "Day 6 (Saturday)",
            "subject": untested_subjects[0] if untested_subjects else (ALL_SUBJECTS[3] if len(ALL_SUBJECTS) > 3 else "CNS"),
            "subject_name": SUBJECT_FULL_NAMES.get(untested_subjects[0] if untested_subjects else "CNS", "Cryptography and Network Security"),
            "session_title": "Syllabus Expansion & Document Exploration",
            "focus_topics": SUBJECT_CORE_TOPICS.get(untested_subjects[0] if untested_subjects else "CNS", {}).get("revision_topics", [])[:2],
            "learning_activity": "Lecture Slide Review & Document-Based Learning",
            "estimated_minutes": 45,
            "steps": [
                "Upload or select a course lecture PPT/PDF in the Previous Documents Library.",
                "Generate a structured concept summary and explore unfamiliar terminology.",
                "Complete a foundational 5-question quiz to establish a baseline proficiency score."
            ]
        },
        {
            "day_number": 7,
            "day_name": "Day 7 (Sunday)",
            "subject": "Comprehensive Assessment",
            "subject_name": "All Active Subjects",
            "session_title": "Weekly Retrospective & Milestone Evaluation",
            "focus_topics": ["Cross-Subject Synthesis", "Remediation Verification"],
            "learning_activity": "Comprehensive Assessment Quiz & Progress Review",
            "estimated_minutes": 40,
            "steps": [
                "Take a comprehensive weekly review quiz covering topics practiced Monday through Friday.",
                "Review the Learning Dashboard to observe score growth delta and newly unlocked badges.",
                "Download the updated Weekly Progress Report and set learning goals for next week."
            ]
        }
    ]

    total_study_minutes = sum(d["estimated_minutes"] for d in days_data)
    total_hours = round(total_study_minutes / 60, 1)

    # 7. Actionable Study Tips & Techniques
    actionable_tips = [
        {
            "title": "Error-Log Remediation",
            "icon": "🎯",
            "description": "Never skip missed quiz questions. Re-test missed concepts within 48 hours to prevent misconceptions from consolidating into long-term memory."
        },
        {
            "title": "Spaced Active Recall",
            "icon": "🧠",
            "description": "Use flashcards with the SM-2 algorithm daily. Active recall before checking the answer stimulates synaptic plasticity far more than passive re-reading."
        },
        {
            "title": "25/5 Pomodoro Focus",
            "icon": "⏱️",
            "description": "Study in distraction-free 25-minute sprints followed by 5-minute cognitive breaks to maintain peak executive function and focus."
        },
        {
            "title": "Multi-Modal Audio Recap",
            "icon": "🎧",
            "description": "Generate audio summaries in the AI Assistant to listen to high-yield topic overviews while walking or during downtime."
        }
    ]

    week_start = datetime.utcnow().strftime("%B %d, %Y")
    week_end = (datetime.utcnow() + timedelta(days=6)).strftime("%B %d, %Y")
    target_week_str = f"{week_start} to {week_end}"

    # Executive focus narrative
    weak_sub_names = [SUBJECT_FULL_NAMES.get(s, s) for s in weak_subjects]
    if weak_sub_names:
        focus_narrative = (
            f"This week's academic plan is prioritized around closing knowledge gaps in "
            f"{', '.join(weak_sub_names[:2])}, addressing {len(missed_questions)} specific quiz missed concepts, "
            f"and maintaining consistent active recall across your strongest subjects."
        )
    else:
        focus_narrative = (
            f"This week's academic plan focuses on building broad multi-subject mastery across "
            f"{SUBJECT_FULL_NAMES.get(primary_weak_subject, primary_weak_subject)} and core syllabus essentials, "
            f"reinforcing retention through active recall flashcards and timed problem solving."
        )

    return {
        "student_name": user.username,
        "student_email": user.email,
        "generated_date": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        "target_week": target_week_str,
        "overall_status": metrics.get("overall_progress_status", "Developing Competency"),
        "total_planned_hours": total_hours,
        "total_planned_minutes": total_study_minutes,
        "primary_focus_subject": SUBJECT_FULL_NAMES.get(primary_weak_subject, primary_weak_subject),
        "weekly_focus_summary": focus_narrative,
        "priority_weak_points": priority_weak_points,
        "subject_wise_recommendations": subject_wise_recommendations,
        "day_by_day_plan": days_data,
        "actionable_tips": actionable_tips
    }


# ==========================================================
# ReportLab PDF Generator for Study Plan
# ==========================================================

def generate_study_plan_pdf(study_plan: Dict[str, Any], user: User) -> BytesIO:
    """
    Renders a clean, beautifully styled academic Weekly Study Plan PDF
    using ReportLab, matching the design aesthetic of the Progress Report.
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors

    buffer = BytesIO()

    # Balanced margins
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Color Palette matching modern educational theme
    COLOR_PRIMARY = colors.HexColor("#0f172a")     # slate-900
    COLOR_SECONDARY = colors.HexColor("#334155")   # slate-700
    COLOR_ACCENT = colors.HexColor("#4f46e5")      # indigo-600
    COLOR_SKY = colors.HexColor("#0284c7")         # sky-600
    COLOR_BORDER = colors.HexColor("#cbd5e1")      # slate-300
    COLOR_MUTED = colors.HexColor("#64748b")       # slate-500
    COLOR_RED = colors.HexColor("#dc2626")         # red-600
    COLOR_AMBER = colors.HexColor("#d97706")       # amber-600
    COLOR_EMERALD = colors.HexColor("#059669")     # emerald-600

    # Custom Typography Styles
    title_style = ParagraphStyle(
        name="StudyPlanTitle",
        parent=styles["Heading1"],
        fontSize=18,
        leading=22,
        textColor=COLOR_PRIMARY,
        spaceAfter=3
    )

    subtitle_style = ParagraphStyle(
        name="StudyPlanSubtitle",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        textColor=COLOR_MUTED,
        spaceAfter=10
    )

    section_style = ParagraphStyle(
        name="SectionHeader",
        parent=styles["Heading2"],
        fontSize=11.5,
        leading=15,
        textColor=COLOR_PRIMARY,
        spaceBefore=10,
        spaceAfter=5
    )

    body_style = ParagraphStyle(
        name="CustomBody",
        parent=styles["Normal"],
        fontSize=8,
        leading=11,
        textColor=COLOR_SECONDARY
    )

    body_bold = ParagraphStyle(
        name="CustomBodyBold",
        parent=styles["Normal"],
        fontSize=8,
        leading=11,
        textColor=COLOR_PRIMARY,
        fontName="Helvetica-Bold"
    )

    table_header_style = ParagraphStyle(
        name="TableHeader",
        parent=styles["Normal"],
        fontSize=8,
        leading=10,
        textColor=colors.white,
        fontName="Helvetica-Bold"
    )

    table_cell_style = ParagraphStyle(
        name="TableCell",
        parent=styles["Normal"],
        fontSize=7.5,
        leading=10,
        textColor=COLOR_SECONDARY
    )

    table_cell_bold = ParagraphStyle(
        name="TableCellBold",
        parent=styles["Normal"],
        fontSize=7.5,
        leading=10,
        textColor=COLOR_PRIMARY,
        fontName="Helvetica-Bold"
    )

    badge_red_style = ParagraphStyle(
        name="BadgeRed",
        parent=styles["Normal"],
        fontSize=7,
        leading=9,
        textColor=COLOR_RED,
        fontName="Helvetica-Bold"
    )

    badge_amber_style = ParagraphStyle(
        name="BadgeAmber",
        parent=styles["Normal"],
        fontSize=7,
        leading=9,
        textColor=COLOR_AMBER,
        fontName="Helvetica-Bold"
    )

    badge_emerald_style = ParagraphStyle(
        name="BadgeEmerald",
        parent=styles["Normal"],
        fontSize=7,
        leading=9,
        textColor=COLOR_EMERALD,
        fontName="Helvetica-Bold"
    )

    story = []

    # ---------------------------------------------------------
    # 1. Header & Title Block
    # ---------------------------------------------------------
    story.append(Paragraph("AI Educational Learning Assistant • Academic Coaching System", subtitle_style))
    story.append(Paragraph("Personalized Weekly Study Plan & Remediation Guide", title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=COLOR_ACCENT, spaceBefore=3, spaceAfter=8))

    # ---------------------------------------------------------
    # 2. Student Metadata & Target Week Card
    # ---------------------------------------------------------
    info_table_data = [
        [
            Paragraph(f"<b>Student Name:</b> {study_plan['student_name']}", body_style),
            Paragraph(f"<b>Student Email:</b> {study_plan['student_email']}", body_style),
        ],
        [
            Paragraph(f"<b>Target Schedule:</b> {study_plan['target_week']}", body_style),
            Paragraph(f"<b>Weekly Study Goal:</b> <font color='#4f46e5'><b>{study_plan['total_planned_hours']} Hours ({study_plan['total_planned_minutes']} mins)</b></font>", body_style),
        ],
        [
            Paragraph(f"<b>Primary Focus Subject:</b> <b>{study_plan['primary_focus_subject']}</b>", body_style),
            Paragraph(f"<b>Progress Standing:</b> {study_plan['overall_status']}", body_style),
        ]
    ]
    info_table = Table(info_table_data, colWidths=[270, 270])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('BOX', (0, 0), (-1, -1), 1, COLOR_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 6))

    # ---------------------------------------------------------
    # 3. Executive Weekly Focus Summary
    # ---------------------------------------------------------
    story.append(Paragraph("Weekly Strategic Focus & Remediation Objective", section_style))
    summary_para = Paragraph(f"<b>Strategic Objective:</b> {study_plan['weekly_focus_summary']}", body_style)
    summary_table = Table([[summary_para]], colWidths=[540])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#eef2ff")),  # indigo-50
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#c7d2fe")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 6))

    # ---------------------------------------------------------
    # 4. Priority Weak Points & Actionable Improvement Strategies
    # ---------------------------------------------------------
    story.append(Paragraph("Priority Weak Points & Actionable Remediation Strategies", section_style))
    
    weak_table_data = [
        [
            Paragraph("Subject", table_header_style),
            Paragraph("Identified Issue / Missed Area", table_header_style),
            Paragraph("Actionable Strategy to Improve", table_header_style),
            Paragraph("Priority", table_header_style)
        ]
    ]

    for wp in study_plan["priority_weak_points"][:4]:
        prio_color = "#dc2626" if wp["priority_level"] == "High" else "#d97706"
        prio_badge = Paragraph(f"<font color='{prio_color}'><b>{wp['priority_level']}</b></font>", table_cell_bold)
        
        issue_text = f"<b>{wp['issue']}</b>"
        if wp.get("example_concept"):
            issue_text += f"<br/><font color='#64748b'><i>Ref: {wp['example_concept']}</i></font>"

        weak_table_data.append([
            Paragraph(f"<b>{wp['subject_name']}</b><br/>({wp['subject']})", table_cell_bold),
            Paragraph(issue_text, table_cell_style),
            Paragraph(wp["improvement_strategy"], table_cell_style),
            prio_badge
        ])

    weak_table = Table(weak_table_data, colWidths=[100, 200, 190, 50])
    weak_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_PRIMARY),
        ('BOX', (0, 0), (-1, -1), 1, COLOR_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#fef2f2")]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(weak_table)
    story.append(Spacer(1, 8))

    # ---------------------------------------------------------
    # 5. 7-Day Structured Day-by-Day Study Schedule Table
    # ---------------------------------------------------------
    story.append(Paragraph("7-Day Structured Weekly Study Schedule", section_style))

    schedule_table_data = [
        [
            Paragraph("Day", table_header_style),
            Paragraph("Subject & Session Focus", table_header_style),
            Paragraph("Target Topics", table_header_style),
            Paragraph("Planned Learning Activity", table_header_style),
            Paragraph("Time", table_header_style)
        ]
    ]

    for day in study_plan["day_by_day_plan"]:
        topics_str = ", ".join(day["focus_topics"]) if isinstance(day["focus_topics"], list) else str(day["focus_topics"])
        steps_summary = "<br/>".join([f"• {s}" for s in day["steps"][:2]])

        schedule_table_data.append([
            Paragraph(f"<b>{day['day_name']}</b>", table_cell_bold),
            Paragraph(f"<b>{day['subject_name']}</b><br/><font color='#4f46e5'>{day['session_title']}</font>", table_cell_style),
            Paragraph(f"<font color='#0f172a'><b>{topics_str}</b></font>", table_cell_style),
            Paragraph(f"<b>{day['learning_activity']}</b><br/>{steps_summary}", table_cell_style),
            Paragraph(f"<b>{day['estimated_minutes']}m</b>", table_cell_bold)
        ])

    schedule_table = Table(schedule_table_data, colWidths=[70, 130, 110, 190, 40])
    schedule_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_ACCENT),
        ('BOX', (0, 0), (-1, -1), 1, COLOR_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(schedule_table)
    story.append(Spacer(1, 8))

    # ---------------------------------------------------------
    # 6. Subject-Wise Topic Breakdown (Improvement, Practice, Revision)
    # ---------------------------------------------------------
    story.append(Paragraph("Subject-Wise Topic Diagnostics & Action Plan", section_style))

    sub_table_data = [
        [
            Paragraph("Subject", table_header_style),
            Paragraph("Topics Needing Improvement", table_header_style),
            Paragraph("Topics for Consistent Practice", table_header_style),
            Paragraph("Important Topics to Revise", table_header_style)
        ]
    ]

    # Show up to 5 most relevant subjects in PDF
    for rec in study_plan["subject_wise_recommendations"][:5]:
        imp_items = "<br/>".join([f"• {t}" for t in rec["topics_needing_improvement"][:2]])
        prac_items = "<br/>".join([f"• {t}" for t in rec["topics_needing_practice"][:2]])
        rev_items = "<br/>".join([f"• {t}" for t in rec["important_revision_topics"][:2]])

        sub_table_data.append([
            Paragraph(f"<b>{rec['subject_name']}</b><br/><font color='#64748b'>Tier: {rec['status_tier']}</font>", table_cell_bold),
            Paragraph(f"<font color='#dc2626'>{imp_items}</font>", table_cell_style),
            Paragraph(f"<font color='#d97706'>{prac_items}</font>", table_cell_style),
            Paragraph(f"<font color='#059669'>{rev_items}</font>", table_cell_style)
        ])

    sub_table = Table(sub_table_data, colWidths=[110, 145, 140, 145])
    sub_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_SECONDARY),
        ('BOX', (0, 0), (-1, -1), 1, COLOR_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(sub_table)
    story.append(Spacer(1, 8))

    # ---------------------------------------------------------
    # 7. Actionable Learning Habits & Study Techniques
    # ---------------------------------------------------------
    story.append(Paragraph("Proven Cognitive Study Techniques for Accelerated Mastery", section_style))

    tips_paragraphs = [
        Paragraph(f"• <b>{t['title']}:</b> {t['description']}", body_style) for t in study_plan["actionable_tips"]
    ]

    tips_table = Table([[tips_paragraphs]], colWidths=[540])
    tips_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f0fdf4")),  # emerald-50
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#bbf7d0")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(tips_table)

    # ---------------------------------------------------------
    # Build Document
    # ---------------------------------------------------------
    doc.build(story)
    buffer.seek(0)
    return buffer
