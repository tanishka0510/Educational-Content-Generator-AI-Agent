"""
Progress Reports Router (CSV & PDF Exports with In-Depth Learning Analytics)

Project: Educational Content Generator AI
Module: Orchestrator Agent (Gateway)
"""

import csv
import json
from io import StringIO, BytesIO
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from database.connection import get_db
from database.crud import get_user_quizzes, get_user_sessions, get_user_flashcard_progress
from database.models import User
from utils.security import get_current_user
from api.study_plan_service import generate_weekly_study_plan, generate_study_plan_pdf

router = APIRouter(prefix="/reports", tags=["Progress Reports"])

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


# ==========================================================
# Comprehensive Learning Metrics Calculation
# ==========================================================

def calculate_user_metrics(db: Session, user: User) -> Dict[str, Any]:
    """
    Analyzes quiz scores, answer choices, and study activities to produce
    all required performance insights:
    - User Name & Email
    - Report Date
    - Overall Progress Status & Comparison of Report
    - Subject-Wise Performance
    - Detailed Quiz / Test Scores Log
    - Learning Progress (answering accuracy progression & remediated questions)
    - Strengths & Areas for Improvement
    - Learning Goals
    - Achievements
    """
    user_id = user.id
    quizzes = get_user_quizzes(db, user_id=user_id)  # returned in desc order by created_at
    quizzes_chrono = list(reversed(quizzes))         # chronological order
    sessions = get_user_sessions(db, user_id=user_id)
    flashcards = get_user_flashcard_progress(db, user_id=user_id)

    total_quizzes = len(quizzes)
    total_chats = len(sessions)
    total_cards = len(flashcards)

    total_questions_attempted = sum(q.total_questions for q in quizzes)
    total_questions_correct = sum(q.score for q in quizzes)

    # 1. Average Score Overall
    overall_avg_score = 0.0
    if total_quizzes > 0:
        total_pct = sum((q.score / q.total_questions) * 100 for q in quizzes)
        overall_avg_score = round(total_pct / total_quizzes, 1)

    # 2. Detailed Question-Level Answer Analysis & Remediation Tracking
    # Tracks question prompt -> list of attempts in chronological order
    question_history: Dict[str, List[Dict[str, Any]]] = {}
    parsed_answers_count = 0

    for q in quizzes_chrono:
        if q.answers_detail:
            try:
                answers = json.loads(q.answers_detail) if isinstance(q.answers_detail, str) else q.answers_detail
                if isinstance(answers, list):
                    for a in answers:
                        q_text = (a.get("question") or "").strip()
                        if not q_text:
                            continue
                        parsed_answers_count += 1
                        is_corr = bool(a.get("is_correct"))
                        record = {
                            "quiz_id": q.id,
                            "subject": q.subject,
                            "topic": q.topic,
                            "created_at": q.created_at,
                            "is_correct": is_corr,
                            "selected_answer": a.get("selected_answer", ""),
                            "correct_answer": a.get("correct_answer", "")
                        }
                        if q_text not in question_history:
                            question_history[q_text] = []
                        question_history[q_text].append(record)
            except Exception:
                pass

    # Detect remediated questions: initially wrong, subsequently answered correctly
    remediated_questions: List[Dict[str, Any]] = []
    for q_text, attempts in question_history.items():
        if len(attempts) >= 2:
            first_attempt = attempts[0]
            if not first_attempt["is_correct"]:
                # Check if any later attempt was correct
                for later_attempt in attempts[1:]:
                    if later_attempt["is_correct"]:
                        remediated_questions.append({
                            "question": q_text,
                            "subject": later_attempt["subject"],
                            "topic": later_attempt["topic"] or "General",
                            "initial_date": first_attempt["created_at"].strftime("%Y-%m-%d %H:%M"),
                            "remediated_date": later_attempt["created_at"].strftime("%Y-%m-%d %H:%M"),
                            "explanation": f"Question initially answered incorrectly on {first_attempt['created_at'].strftime('%Y-%m-%d')}, then answered correctly on {later_attempt['created_at'].strftime('%Y-%m-%d')}."
                        })
                        break

    # 3. Subject-Wise Performance & Learning Progress Trajectory
    subject_stats: Dict[str, Dict[str, Any]] = {}
    subject_learning_progress: Dict[str, Dict[str, Any]] = {}

    for sub in ALL_SUBJECTS:
        sub_quizzes_chrono = [q for q in quizzes_chrono if q.subject == sub]
        sub_chats = [s for s in sessions if s.subject == sub]
        sub_cards = [c for c in flashcards if c.subject == sub]

        q_count = len(sub_quizzes_chrono)
        c_count = len(sub_chats)
        card_count = len(sub_cards)

        sub_avg = 0.0
        high_score = 0.0
        low_score = 0.0

        if q_count > 0:
            scores_pct = [(q.score / q.total_questions) * 100 for q in sub_quizzes_chrono]
            sub_avg = round(sum(scores_pct) / q_count, 1)
            high_score = round(max(scores_pct), 1)
            low_score = round(min(scores_pct), 1)

        # Proficiency tier
        if q_count == 0:
            tier = "Not Started"
        elif sub_avg >= 85:
            tier = "Mastery"
        elif sub_avg >= 70:
            tier = "Proficient"
        elif sub_avg >= 50:
            tier = "Developing"
        else:
            tier = "Needs Practice"

        subject_stats[sub] = {
            "full_name": SUBJECT_FULL_NAMES.get(sub, sub),
            "quizzes_taken": q_count,
            "quiz_average": sub_avg,
            "highest_score": high_score,
            "lowest_score": low_score,
            "chats_started": c_count,
            "flashcards_reviewed": card_count,
            "tier": tier
        }

        # Calculate Learning Progress for this subject
        sub_remediated = [r for r in remediated_questions if r["subject"] == sub]
        remediated_count = len(sub_remediated)

        if q_count >= 2:
            first_pct = round((sub_quizzes_chrono[0].score / sub_quizzes_chrono[0].total_questions) * 100, 1)
            latest_pct = round((sub_quizzes_chrono[-1].score / sub_quizzes_chrono[-1].total_questions) * 100, 1)
            delta = round(latest_pct - first_pct, 1)
            
            if delta > 0:
                prog_desc = f"Demonstrated positive learning progress: score improved by +{delta}% (from {first_pct}% to {latest_pct}%). {remediated_count} concept(s) mastered upon re-attempt."
            elif delta == 0:
                prog_desc = f"Maintained consistent performance at {latest_pct}%. {remediated_count} remediated concept(s)."
            else:
                prog_desc = f"Recent quiz scored {latest_pct}% (overall average {sub_avg}%). Targeted practice recommended to reinforce retention."

            subject_learning_progress[sub] = {
                "initial_score": first_pct,
                "latest_score": latest_pct,
                "delta": delta,
                "remediated_count": remediated_count,
                "description": prog_desc,
                "quizzes_taken": q_count
            }
        elif q_count == 1:
            score_pct = round((sub_quizzes_chrono[0].score / sub_quizzes_chrono[0].total_questions) * 100, 1)
            subject_learning_progress[sub] = {
                "initial_score": score_pct,
                "latest_score": score_pct,
                "delta": 0.0,
                "remediated_count": remediated_count,
                "description": f"Baseline established at {score_pct}%. Solid initial comprehension demonstrated; further quizzes will track progression.",
                "quizzes_taken": 1
            }
        else:
            subject_learning_progress[sub] = {
                "initial_score": 0.0,
                "latest_score": 0.0,
                "delta": 0.0,
                "remediated_count": 0,
                "description": "No quizzes taken yet in this subject.",
                "quizzes_taken": 0
            }

    # 4. Comparison of Report (Baseline vs Recent Performance)
    comparison: Dict[str, Any] = {
        "baseline_avg": 0.0,
        "recent_avg": 0.0,
        "growth_delta": 0.0,
        "trend": "Baseline establishing"
    }

    if total_quizzes >= 2:
        midpoint = max(1, total_quizzes // 2)
        early_quizzes = quizzes_chrono[:midpoint]
        late_quizzes = quizzes_chrono[midpoint:]

        early_avg = round(sum((q.score / q.total_questions) * 100 for q in early_quizzes) / len(early_quizzes), 1)
        late_avg = round(sum((q.score / q.total_questions) * 100 for q in late_quizzes) / len(late_quizzes), 1)
        growth = round(late_avg - early_avg, 1)

        if growth > 0:
            trend = f"Upward trajectory: +{growth}% score growth from baseline"
        elif growth == 0:
            trend = "Steady & consistent mastery maintained across sessions"
        else:
            trend = f"Slight score variance ({growth}%); review advised"

        comparison = {
            "baseline_avg": early_avg,
            "recent_avg": late_avg,
            "growth_delta": growth,
            "trend": trend
        }
    elif total_quizzes == 1:
        single_pct = round((quizzes[0].score / quizzes[0].total_questions) * 100, 1)
        comparison = {
            "baseline_avg": single_pct,
            "recent_avg": single_pct,
            "growth_delta": 0.0,
            "trend": "Initial benchmark established"
        }

    # 5. Strengths Identification
    strengths: List[str] = []
    # High scoring subjects
    high_subs = [s for s, st in subject_stats.items() if st["quizzes_taken"] > 0 and st["quiz_average"] >= 75]
    for hs in high_subs:
        st = subject_stats[hs]
        strengths.append(f"Strong proficiency in {SUBJECT_FULL_NAMES.get(hs, hs)} with an average score of {st['quiz_average']}%.")
    
    # Perfect score quizzes
    perfect_quizzes = [q for q in quizzes if q.score == q.total_questions]
    if perfect_quizzes:
        perfect_topics = set((q.topic or SUBJECT_FULL_NAMES.get(q.subject, q.subject)) for q in perfect_quizzes)
        strengths.append(f"Achieved perfect scores (100%) on {len(perfect_quizzes)} quiz(zes), including: {', '.join(list(perfect_topics)[:3])}.")

    # Concept remediation strength
    if remediated_questions:
        strengths.append(f"Active learning resilience: successfully corrected and mastered {len(remediated_questions)} previously missed question concept(s).")

    # High card review or chats
    if total_cards >= 5:
        strengths.append(f"Consistent active recall habit with {total_cards} spaced repetition flashcard reviews completed.")

    if not strengths:
        strengths.append("Foundational learning in progress. Continue taking quizzes to build measurable strengths.")

    # 6. Areas for Improvement
    areas_for_improvement: List[str] = []
    # Low scoring subjects
    low_subs = [s for s, st in subject_stats.items() if st["quizzes_taken"] > 0 and st["quiz_average"] < 70]
    for ls in low_subs:
        st = subject_stats[ls]
        areas_for_improvement.append(f"Review core principles in {SUBJECT_FULL_NAMES.get(ls, ls)} (current average score: {st['quiz_average']}%).")

    # Hard difficulty struggling
    hard_quizzes = [q for q in quizzes if q.difficulty == "hard"]
    if hard_quizzes:
        hard_avg = round(sum((q.score / q.total_questions) * 100 for q in hard_quizzes) / len(hard_quizzes), 1)
        if hard_avg < 65:
            areas_for_improvement.append(f"Challenging concepts at Hard difficulty level require deeper review (average hard quiz score: {hard_avg}%).")

    # Subjects not yet attempted
    untested_subs = [s for s, st in subject_stats.items() if st["quizzes_taken"] == 0]
    if untested_subs and len(untested_subs) <= 5:
        untested_names = [SUBJECT_FULL_NAMES.get(s, s) for s in untested_subs[:3]]
        areas_for_improvement.append(f"Broaden knowledge coverage by testing unexplored subjects: {', '.join(untested_names)}.")

    if not areas_for_improvement:
        areas_for_improvement.append("Overall scores are solid. Challenge yourself with 'Hard' difficulty quizzes or new topics.")

    # 7. Personalized Learning Goals
    learning_goals: List[str] = []
    if low_subs:
        weakest = min(low_subs, key=lambda s: subject_stats[s]["quiz_average"])
        learning_goals.append(f"Raise quiz performance in {SUBJECT_FULL_NAMES.get(weakest, weakest)} above 80% through targeted topic revision.")
    else:
        learning_goals.append("Maintain an overall academic quiz average of 85% or higher across all active subjects.")

    if remediated_questions:
        learning_goals.append(f"Continue re-testing remediated topics to ensure long-term retention of previously challenging concepts.")
    else:
        learning_goals.append("Retake quizzes on topics where mistakes occurred to verify learning progress and remediation.")

    if untested_subs:
        learning_goals.append(f"Complete at least one quiz in {SUBJECT_FULL_NAMES.get(untested_subs[0], untested_subs[0])} to build balanced syllabus mastery.")
    else:
        learning_goals.append("Engage in spaced repetition flashcards daily to cement cross-subject mastery.")

    # 8. Achievements & Badges
    achievements: List[Dict[str, Any]] = [
        {
            "name": "First Step Scholar",
            "unlocked": total_quizzes >= 1,
            "description": "Completed first academic quiz on the platform."
        },
        {
            "name": "Concept Master",
            "unlocked": any(q.score == q.total_questions for q in quizzes),
            "description": "Scored 100% on a quiz session."
        },
        {
            "name": "Comeback Scholar",
            "unlocked": len(remediated_questions) > 0 or comparison["growth_delta"] > 0,
            "description": "Demonstrated measurable learning progress by mastering previously missed questions."
        },
        {
            "name": "Subject Explorer",
            "unlocked": len([s for s, st in subject_stats.items() if st["quizzes_taken"] > 0]) >= 3,
            "description": "Tested knowledge across 3 or more distinct subjects."
        },
        {
            "name": "Dedicated Scholar",
            "unlocked": total_quizzes >= 5,
            "description": "Completed 5 or more quizzes."
        },
        {
            "name": "High Achiever",
            "unlocked": total_quizzes >= 3 and overall_avg_score >= 80,
            "description": "Maintained an overall average score of 80% or higher across multiple quizzes."
        }
    ]

    # 9. Overall Progress Status
    if total_quizzes == 0:
        overall_status = "Getting Started (No Quizzes Taken)"
        status_narrative = "Welcome to the Educational AI Platform! Begin taking quizzes and flashcards to build your learning profile."
    elif total_quizzes >= 3 and overall_avg_score >= 85:
        overall_status = "Advanced Mastery (Tier 4/4)"
        status_narrative = f"Exceptional academic standing. Maintained an outstanding average score of {overall_avg_score}% across {total_quizzes} quiz sessions."
    elif overall_avg_score >= 70:
        overall_status = "Proficient & Advancing (Tier 3/4)"
        status_narrative = f"Strong and consistent comprehension with an average score of {overall_avg_score}%. Regular practice is demonstrating solid learning progress."
    elif overall_avg_score >= 50:
        overall_status = "Developing Competency (Tier 2/4)"
        status_narrative = f"Active progress with an average score of {overall_avg_score}%. Re-testing missed concepts will accelerate mastery."
    else:
        overall_status = "Foundational / Needs Practice (Tier 1/4)"
        status_narrative = f"Baseline established at {overall_avg_score}%. Focused study using chat explanations and flashcards is recommended."

    report_date_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    return {
        "user_name": user.username,
        "student_email": user.email,
        "report_date": report_date_str,
        "overall_progress_status": overall_status,
        "status_narrative": status_narrative,
        "total_quizzes": total_quizzes,
        "total_questions_attempted": total_questions_attempted,
        "total_questions_correct": total_questions_correct,
        "average_score": overall_avg_score,
        "total_chats": total_chats,
        "total_cards": total_cards,
        "comparison": comparison,
        "subject_stats": subject_stats,
        "subject_learning_progress": subject_learning_progress,
        "remediated_questions": remediated_questions,
        "quizzes": quizzes,  # desc order
        "strengths": strengths,
        "areas_for_improvement": areas_for_improvement,
        "learning_goals": learning_goals,
        "achievements": achievements
    }


# ==========================================================
# Analytics API Endpoint (JSON for Frontend Dashboard)
# ==========================================================

@router.get("/analytics")
def get_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns calculated progress metrics and analytics for interactive dashboard view."""
    metrics = calculate_user_metrics(db, current_user)
    # Filter non-serializable objects (like raw model instances)
    serializable = {k: v for k, v in metrics.items() if k != "quizzes"}
    return serializable


# ==========================================================
# CSV Export Endpoint
# ==========================================================

@router.get("/csv")
def export_csv(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generates a structured CSV report detailing student performance,
    learning progress comparison, strengths, goals, and achievements.
    """
    metrics = calculate_user_metrics(db, current_user)
    
    stream = StringIO()
    writer = csv.writer(stream)
    
    # 1. Header & Student Info
    writer.writerow(["=" * 60])
    writer.writerow(["STUDENT ACADEMIC PROGRESS & LEARNING REPORT"])
    writer.writerow(["=" * 60])
    writer.writerow(["User Name", metrics["user_name"]])
    writer.writerow(["Student Email ID", metrics["student_email"]])
    writer.writerow(["Report Date", metrics["report_date"]])
    writer.writerow(["Overall Progress Status", metrics["overall_progress_status"]])
    writer.writerow(["Status Evaluation", metrics["status_narrative"]])
    writer.writerow([])
    
    # 2. Executive Summary & Comparison of Report
    writer.writerow(["-" * 40])
    writer.writerow(["OVERALL SUMMARY & COMPARISON OF REPORT"])
    writer.writerow(["-" * 40])
    writer.writerow(["Metric", "Value"])
    writer.writerow(["Total Quizzes Taken", metrics["total_quizzes"]])
    writer.writerow(["Total Questions Answered", metrics["total_questions_attempted"]])
    writer.writerow(["Total Correct Answers", metrics["total_questions_correct"]])
    writer.writerow(["Overall Average Quiz Score (%)", f"{metrics['average_score']}%"])
    writer.writerow(["Baseline Average Score (%)", f"{metrics['comparison']['baseline_avg']}%"])
    writer.writerow(["Recent Average Score (%)", f"{metrics['comparison']['recent_avg']}%"])
    writer.writerow(["Overall Score Growth / Delta (%)", f"{metrics['comparison']['growth_delta']}%"])
    writer.writerow(["Progress Trend Analysis", metrics["comparison"]["trend"]])
    writer.writerow(["Total Question Concepts Remediated", len(metrics["remediated_questions"])])
    writer.writerow(["Total Chat Sessions", metrics["total_chats"]])
    writer.writerow(["Flashcards Reviewed", metrics["total_cards"]])
    writer.writerow([])
    
    # 3. Learning Progress (Subject-Wise & Answer Comparison)
    writer.writerow(["-" * 40])
    writer.writerow(["LEARNING PROGRESS BY SUBJECT"])
    writer.writerow(["(Evaluates progress by comparing answers & test attempts over time)"])
    writer.writerow(["-" * 40])
    writer.writerow(["Subject", "Quizzes Taken", "Initial Score (%)", "Latest Score (%)", "Score Delta (%)", "Remediated Concepts", "Learning Progress Description"])
    for sub, prog in metrics["subject_learning_progress"].items():
        if prog["quizzes_taken"] > 0:
            writer.writerow([
                SUBJECT_FULL_NAMES.get(sub, sub),
                prog["quizzes_taken"],
                f"{prog['initial_score']}%",
                f"{prog['latest_score']}%",
                f"{prog['delta']:+}%",
                prog["remediated_count"],
                prog["description"]
            ])
    writer.writerow([])

    # Remediated Questions Detail
    if metrics["remediated_questions"]:
        writer.writerow(["REMEDIATED CONCEPTS LOG (Initial Error -> Subsequent Correct Answer)"])
        writer.writerow(["Subject", "Topic", "Question Prompt", "Initial Mistake Date", "Mastered Date", "Remediation Status"])
        for rq in metrics["remediated_questions"]:
            writer.writerow([
                SUBJECT_FULL_NAMES.get(rq["subject"], rq["subject"]),
                rq["topic"],
                rq["question"],
                rq["initial_date"],
                rq["remediated_date"],
                "Remediated & Mastered"
            ])
        writer.writerow([])

    # 4. Subject-Wise Performance Breakdown
    writer.writerow(["-" * 40])
    writer.writerow(["SUBJECT-WISE PERFORMANCE"])
    writer.writerow(["-" * 40])
    writer.writerow(["Subject", "Quizzes Taken", "Average Score (%)", "Highest Score (%)", "Lowest Score (%)", "Proficiency Tier", "Chats", "Flashcards"])
    for sub, stats in metrics["subject_stats"].items():
        writer.writerow([
            SUBJECT_FULL_NAMES.get(sub, sub),
            stats["quizzes_taken"],
            f"{stats['quiz_average']}%" if stats["quizzes_taken"] > 0 else "N/A",
            f"{stats['highest_score']}%" if stats["quizzes_taken"] > 0 else "N/A",
            f"{stats['lowest_score']}%" if stats["quizzes_taken"] > 0 else "N/A",
            stats["tier"],
            stats["chats_started"],
            stats["flashcards_reviewed"]
        ])
    writer.writerow([])
    
    # 5. Detailed Quiz / Test Scores Log
    writer.writerow(["-" * 40])
    writer.writerow(["QUIZ / TEST SCORES LOG"])
    writer.writerow(["-" * 40])
    writer.writerow(["Date", "Subject", "Topic", "Difficulty", "Score", "Total Questions", "Percentage (%)", "Status"])
    for q in metrics["quizzes"]:
        pct = round((q.score / q.total_questions) * 100, 1)
        status_label = "Perfect Score" if pct == 100 else ("Passed" if pct >= 70 else "Needs Review")
        writer.writerow([
            q.created_at.strftime("%Y-%m-%d %H:%M"),
            SUBJECT_FULL_NAMES.get(q.subject, q.subject),
            q.topic or "General Assessment",
            q.difficulty.title(),
            q.score,
            q.total_questions,
            f"{pct}%",
            status_label
        ])
    writer.writerow([])

    # 6. Strengths
    writer.writerow(["-" * 40])
    writer.writerow(["KEY STRENGTHS"])
    writer.writerow(["-" * 40])
    for s in metrics["strengths"]:
        writer.writerow([f"• {s}"])
    writer.writerow([])

    # 7. Areas for Improvement
    writer.writerow(["-" * 40])
    writer.writerow(["AREAS FOR IMPROVEMENT"])
    writer.writerow(["-" * 40])
    for a in metrics["areas_for_improvement"]:
        writer.writerow([f"• {a}"])
    writer.writerow([])

    # 8. Learning Goals
    writer.writerow(["-" * 40])
    writer.writerow(["TARGETED LEARNING GOALS"])
    writer.writerow(["-" * 40])
    for g in metrics["learning_goals"]:
        writer.writerow([f"• {g}"])
    writer.writerow([])

    # 9. Achievements
    writer.writerow(["-" * 40])
    writer.writerow(["ACHIEVEMENT MILESTONES"])
    writer.writerow(["-" * 40])
    writer.writerow(["Badge", "Status", "Description"])
    for ach in metrics["achievements"]:
        writer.writerow([
            ach["name"],
            "UNLOCKED" if ach["unlocked"] else "IN PROGRESS",
            ach["description"]
        ])
        
    stream.seek(0)
    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename=progress_report_{current_user.username}.csv"
    return response


# ==========================================================
# PDF Export Endpoint
# ==========================================================

@router.get("/pdf")
def export_pdf(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generates a beautifully styled, professional academic progress PDF report
    containing all 11 required sections with elegant tables, badges, and learning analytics.
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
        )
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="PDF generation library (reportlab) is not loaded on server."
        )

    metrics = calculate_user_metrics(db, current_user)
    buffer = BytesIO()
    
    # Initialize Document with balanced margins
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Palette
    COLOR_PRIMARY = colors.HexColor("#0f172a")    # slate-900
    COLOR_SECONDARY = colors.HexColor("#334155")  # slate-700
    COLOR_ACCENT = colors.HexColor("#0284c7")     # sky-600
    COLOR_LIGHT = colors.HexColor("#f8fafc")      # slate-50
    COLOR_BORDER = colors.HexColor("#cbd5e1")     # slate-300
    COLOR_MUTED = colors.HexColor("#64748b")      # slate-500
    COLOR_SUCCESS = colors.HexColor("#059669")    # emerald-600
    COLOR_WARN = colors.HexColor("#d97706")       # amber-600

    # Typography Styles
    title_style = ParagraphStyle(
        name="DocTitle",
        parent=styles["Heading1"],
        fontSize=20,
        leading=24,
        textColor=COLOR_PRIMARY,
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        name="DocSubtitle",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        textColor=COLOR_MUTED,
        spaceAfter=12
    )
    
    section_style = ParagraphStyle(
        name="SectionHeader",
        parent=styles["Heading2"],
        fontSize=12,
        leading=16,
        textColor=COLOR_PRIMARY,
        spaceBefore=12,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        name="CustomBody",
        parent=styles["Normal"],
        fontSize=8.5,
        leading=12,
        textColor=COLOR_SECONDARY
    )

    body_bold = ParagraphStyle(
        name="CustomBodyBold",
        parent=styles["Normal"],
        fontSize=8.5,
        leading=12,
        textColor=COLOR_PRIMARY,
        fontName="Helvetica-Bold"
    )

    badge_unlocked_style = ParagraphStyle(
        name="BadgeUnlocked",
        parent=styles["Normal"],
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#047857"),
        fontName="Helvetica-Bold"
    )

    badge_progress_style = ParagraphStyle(
        name="BadgeProgress",
        parent=styles["Normal"],
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#64748b"),
        fontName="Helvetica"
    )

    table_cell_style = ParagraphStyle(
        name="TableCell",
        parent=styles["Normal"],
        fontSize=8,
        leading=10,
        textColor=COLOR_SECONDARY
    )

    table_cell_bold = ParagraphStyle(
        name="TableCellBold",
        parent=styles["Normal"],
        fontSize=8,
        leading=10,
        textColor=COLOR_PRIMARY,
        fontName="Helvetica-Bold"
    )

    story = []
    
    # ---------------------------------------------------------
    # 1. Header & Title Block
    # ---------------------------------------------------------
    story.append(Paragraph("AI Educational Learning Assistant", subtitle_style))
    story.append(Paragraph("Student Academic Progress & Learning Report", title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=COLOR_ACCENT, spaceBefore=4, spaceAfter=10))

    # ---------------------------------------------------------
    # 2. Student Metadata & Status Card
    # ---------------------------------------------------------
    info_table_data = [
        [
            Paragraph(f"<b>Student Name:</b> {metrics['user_name']}", body_style),
            Paragraph(f"<b>Student Email:</b> {metrics['student_email']}", body_style),
        ],
        [
            Paragraph(f"<b>Report Date:</b> {metrics['report_date']}", body_style),
            Paragraph(f"<b>Overall Progress Status:</b> <font color='#0284c7'><b>{metrics['overall_progress_status']}</b></font>", body_style),
        ]
    ]
    info_table = Table(info_table_data, colWidths=[270, 270])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
        ('BOX', (0, 0), (-1, -1), 1, COLOR_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 8))

    # ---------------------------------------------------------
    # 3. Overall Summary & Comparison of Report KPIs
    # ---------------------------------------------------------
    story.append(Paragraph("Overall Performance Summary & Comparison of Report", section_style))
    growth_str = f"+{metrics['comparison']['growth_delta']}%" if metrics['comparison']['growth_delta'] > 0 else f"{metrics['comparison']['growth_delta']}%"
    kpi_data = [
        ["Total Quizzes", "Average Score", "Baseline Score", "Recent Score", "Score Growth", "Concepts Remediated"],
        [
            str(metrics["total_quizzes"]),
            f"{metrics['average_score']}%",
            f"{metrics['comparison']['baseline_avg']}%",
            f"{metrics['comparison']['recent_avg']}%",
            growth_str,
            str(len(metrics["remediated_questions"]))
        ]
    ]
    kpi_table = Table(kpi_data, colWidths=[90, 90, 90, 90, 90, 90])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, 1), COLOR_LIGHT),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, 1), 10),
        ('TEXTCOLOR', (0, 1), (-1, 1), COLOR_PRIMARY),
        ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
    ]))
    story.append(kpi_table)
    
    # Growth description
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<b>Comparison Analysis:</b> {metrics['comparison']['trend']}. {metrics['status_narrative']}", body_style))
    story.append(Spacer(1, 8))

    # ---------------------------------------------------------
    # 4. Learning Progress (Answer Comparison & Evolution)
    # ---------------------------------------------------------
    story.append(Paragraph("Learning Progress (Progress over Time & Concept Remediation)", section_style))
    story.append(Paragraph(
        "<i>Describes progression in each subject by comparing user answers across test attempts. When a question is answered incorrectly on first attempt and subsequently answered correctly, it is recorded as a mastered concept.</i>",
        subtitle_style
    ))

    # Subject progress comparison table
    active_progress = [
        (sub, prog) for sub, prog in metrics["subject_learning_progress"].items()
        if prog["quizzes_taken"] > 0
    ]
    
    if active_progress:
        prog_table_data = [
            ["Subject", "Quizzes", "Initial Score", "Latest Score", "Progression Delta", "Concepts Remediated", "Progress Evaluation"]
        ]
        for sub, prog in active_progress:
            delta_fmt = f"+{prog['delta']}%" if prog['delta'] > 0 else f"{prog['delta']}%"
            prog_table_data.append([
                Paragraph(f"<b>{SUBJECT_FULL_NAMES.get(sub, sub)}</b>", table_cell_style),
                Paragraph(str(prog["quizzes_taken"]), table_cell_style),
                Paragraph(f"{prog['initial_score']}%", table_cell_style),
                Paragraph(f"{prog['latest_score']}%", table_cell_style),
                Paragraph(f"<b>{delta_fmt}</b>", table_cell_style),
                Paragraph(str(prog["remediated_count"]), table_cell_style),
                Paragraph(prog["description"], table_cell_style),
            ])
        
        prog_table = Table(prog_table_data, colWidths=[95, 45, 55, 55, 60, 55, 175])
        prog_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#334155")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (5, -1), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 7.5),
            ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, COLOR_LIGHT])
        ]))
        story.append(prog_table)
    else:
        story.append(Paragraph("No subject quiz progress recorded yet.", body_style))

    # Highlight remediated questions if any
    if metrics["remediated_questions"]:
        story.append(Spacer(1, 6))
        story.append(Paragraph("<b>Specific Concept Remediation Log:</b>", body_bold))
        for rq in metrics["remediated_questions"][:3]:  # Top 3 to prevent overflow
            q_snippet = rq['question'][:100] + "..." if len(rq['question']) > 100 else rq['question']
            story.append(Paragraph(
                f"• <b>{SUBJECT_FULL_NAMES.get(rq['subject'], rq['subject'])}</b> ({rq['topic']}): <i>\"{q_snippet}\"</i> — initially missed on {rq['initial_date']}, correctly answered on {rq['remediated_date']}.",
                body_style
            ))

    story.append(Spacer(1, 8))

    # ---------------------------------------------------------
    # 5. Subject-Wise Performance Breakdown
    # ---------------------------------------------------------
    story.append(Paragraph("Subject-Wise Performance Breakdown", section_style))
    sub_table_data = [
        ["Subject", "Quizzes", "Average Score", "Highest Score", "Lowest Score", "Proficiency Tier", "Chats", "Flashcards"]
    ]
    for sub, stats in metrics["subject_stats"].items():
        if stats["quizzes_taken"] > 0 or stats["chats_started"] > 0 or stats["flashcards_reviewed"] > 0:
            sub_table_data.append([
                Paragraph(f"<b>{SUBJECT_FULL_NAMES.get(sub, sub)}</b>", table_cell_style),
                str(stats["quizzes_taken"]),
                f"{stats['quiz_average']}%" if stats["quizzes_taken"] > 0 else "N/A",
                f"{stats['highest_score']}%" if stats["quizzes_taken"] > 0 else "N/A",
                f"{stats['lowest_score']}%" if stats["quizzes_taken"] > 0 else "N/A",
                stats["tier"],
                str(stats["chats_started"]),
                str(stats["flashcards_reviewed"])
            ])
    
    if len(sub_table_data) > 1:
        sub_table = Table(sub_table_data, colWidths=[140, 50, 65, 65, 65, 75, 40, 40])
        sub_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e293b")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7.5),
            ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, COLOR_LIGHT])
        ]))
        story.append(sub_table)
    else:
        story.append(Paragraph("No subject activity recorded yet.", body_style))

    story.append(Spacer(1, 8))

    # ---------------------------------------------------------
    # 6. Quiz / Test Scores Log (Recent Quizzes)
    # ---------------------------------------------------------
    story.append(Paragraph("Quiz / Test Scores Log", section_style))
    quiz_table_data = [
        ["Date", "Subject", "Topic", "Difficulty", "Score", "Percentage", "Outcome"]
    ]
    recent_quizzes = metrics["quizzes"][:8]  # Show recent 8 attempts
    for q in recent_quizzes:
        pct = round((q.score / q.total_questions) * 100, 1)
        outcome_label = "Perfect (100%)" if pct == 100 else ("Passed" if pct >= 70 else "Needs Review")
        quiz_table_data.append([
            q.created_at.strftime("%Y-%m-%d"),
            Paragraph(SUBJECT_FULL_NAMES.get(q.subject, q.subject), table_cell_style),
            Paragraph(q.topic or "General", table_cell_style),
            q.difficulty.title(),
            f"{q.score}/{q.total_questions}",
            f"{pct}%",
            outcome_label
        ])

    if recent_quizzes:
        quiz_table = Table(quiz_table_data, colWidths=[65, 120, 125, 55, 50, 60, 65])
        quiz_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 1), (2, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7.5),
            ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, COLOR_LIGHT])
        ]))
        story.append(quiz_table)
    else:
        story.append(Paragraph("No quiz scores recorded yet.", body_style))

    story.append(Spacer(1, 8))

    # ---------------------------------------------------------
    # 7. Strengths & Areas for Improvement (Side-by-Side)
    # ---------------------------------------------------------
    story.append(Paragraph("Diagnostic Insights: Strengths & Areas for Improvement", section_style))
    
    strengths_paragraphs = [Paragraph(f"• {s}", body_style) for s in metrics["strengths"]]
    areas_paragraphs = [Paragraph(f"• {a}", body_style) for a in metrics["areas_for_improvement"]]
    
    insights_table_data = [
        [
            Paragraph("<b>Identified Strengths</b>", table_cell_bold),
            Paragraph("<b>Areas for Improvement</b>", table_cell_bold)
        ],
        [
            strengths_paragraphs,
            areas_paragraphs
        ]
    ]
    insights_table = Table(insights_table_data, colWidths=[270, 270])
    insights_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor("#ecfdf5")),  # emerald-50
        ('BACKGROUND', (1, 0), (1, 0), colors.HexColor("#fffbeb")),  # amber-50
        ('TEXTCOLOR', (0, 0), (0, 0), colors.HexColor("#065f46")),
        ('TEXTCOLOR', (1, 0), (1, 0), colors.HexColor("#92400e")),
        ('BACKGROUND', (0, 1), (-1, 1), colors.white),
        ('BOX', (0, 0), (-1, -1), 1, COLOR_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(insights_table)
    story.append(Spacer(1, 8))

    # ---------------------------------------------------------
    # 8. Learning Goals & Achievements
    # ---------------------------------------------------------
    story.append(Paragraph("Targeted Learning Goals & Achievement Milestones", section_style))
    
    goals_paragraphs = [Paragraph(f"• {g}", body_style) for g in metrics["learning_goals"]]
    
    ach_rows = []
    for ach in metrics["achievements"]:
        status_para = Paragraph("[UNLOCKED]", badge_unlocked_style) if ach["unlocked"] else Paragraph("[IN PROGRESS]", badge_progress_style)
        ach_rows.append(Paragraph(f"• <b>{ach['name']}</b>: {ach['description']} {status_para.text}", body_style))

    goals_ach_table_data = [
        [
            Paragraph("<b>Personalized Learning Goals</b>", table_cell_bold),
            Paragraph("<b>Platform Achievements</b>", table_cell_bold)
        ],
        [
            goals_paragraphs,
            ach_rows
        ]
    ]
    goals_ach_table = Table(goals_ach_table_data, colWidths=[270, 270])
    goals_ach_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor("#eff6ff")),  # blue-50
        ('BACKGROUND', (1, 0), (1, 0), colors.HexColor("#faf5ff")),  # purple-50
        ('TEXTCOLOR', (0, 0), (0, 0), colors.HexColor("#1e40af")),
        ('TEXTCOLOR', (1, 0), (1, 0), colors.HexColor("#6b21a8")),
        ('BACKGROUND', (0, 1), (-1, 1), colors.white),
        ('BOX', (0, 0), (-1, -1), 1, COLOR_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(goals_ach_table)

    # ---------------------------------------------------------
    # Build Document
    # ---------------------------------------------------------
    doc.build(story)
    
    buffer.seek(0)
    response = StreamingResponse(buffer, media_type="application/pdf")
    response.headers["Content-Disposition"] = f"attachment; filename=progress_report_{current_user.username}.pdf"
    return response


# ==========================================================
# Personalized Weekly Study Plan Endpoints
# ==========================================================

@router.get("/study-plan")
def get_study_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generates a personalized Weekly Study Plan based on the student's progress report,
    focusing on weak points, suggested improvement strategies, and subject-wise
    recommendations (needs improvement, consistent practice, important revision topics).
    """
    metrics = calculate_user_metrics(db, current_user)
    plan = generate_weekly_study_plan(db, current_user, metrics)
    return plan


@router.get("/study-plan/pdf")
def export_study_plan_pdf(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generates a beautifully styled, downloadable academic Weekly Study Plan PDF
    using ReportLab, detailing student weak points, actionable remediation strategies,
    a 7-day structured study schedule, and cognitive study habits.
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
        )
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="PDF generation library (reportlab) is not loaded on server."
        )

    metrics = calculate_user_metrics(db, current_user)
    plan = generate_weekly_study_plan(db, current_user, metrics)
    pdf_buffer = generate_study_plan_pdf(plan, current_user)

    response = StreamingResponse(pdf_buffer, media_type="application/pdf")
    response.headers["Content-Disposition"] = f"attachment; filename=study_plan_{current_user.username}.pdf"
    return response

