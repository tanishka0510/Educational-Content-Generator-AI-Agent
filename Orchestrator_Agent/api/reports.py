"""
Progress Reports Router (CSV & PDF Exports)

Project: Educational Content Generator AI
Module: Orchestrator Agent (Gateway)
"""

import csv
from io import StringIO, BytesIO
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from database.connection import get_db
from database.crud import get_user_quizzes, get_user_sessions, get_user_flashcard_progress
from database.models import User
from utils.security import get_current_user

router = APIRouter(prefix="/reports", tags=["Progress Reports"])


# ==========================================================
# Metrics Helper
# ==========================================================

def calculate_user_metrics(db: Session, user_id: int):
    """Gathers all database metrics and aggregates user performance statistics."""
    quizzes = get_user_quizzes(db, user_id=user_id)
    sessions = get_user_sessions(db, user_id=user_id)
    flashcards = get_user_flashcard_progress(db, user_id=user_id)

    total_quizzes = len(quizzes)
    total_chats = len(sessions)
    total_cards = len(flashcards)

    # Average score
    avg_score = 0.0
    if total_quizzes > 0:
        total_pct = sum((q.score / q.total_questions) * 100 for q in quizzes)
        avg_score = round(total_pct / total_quizzes, 1)

    # Subject-wise distribution
    subjects = ["OS", "OOP", "DBMS", "CNS", "SE", "AI", "ETC", "COA", "DATA STRUCTURE"]
    subject_stats = {}
    for sub in subjects:
        sub_quizzes = [q for q in quizzes if q.subject == sub]
        sub_chats = [s for s in sessions if s.subject == sub]
        sub_cards = [c for c in flashcards if c.subject == sub]

        q_count = len(sub_quizzes)
        c_count = len(sub_chats)
        card_count = len(sub_cards)
        
        sub_avg = 0.0
        if q_count > 0:
            sub_avg = round(sum((q.score / q.total_questions) * 100 for q in sub_quizzes) / q_count, 1)

        subject_stats[sub] = {
            "quizzes_taken": q_count,
            "quiz_average": sub_avg,
            "chats_started": c_count,
            "flashcards_reviewed": card_count
        }

    return {
        "total_quizzes": total_quizzes,
        "total_chats": total_chats,
        "total_cards": total_cards,
        "average_score": avg_score,
        "quizzes": quizzes,
        "subject_stats": subject_stats
    }


# ==========================================================
# CSV Export Endpoint
# ==========================================================

@router.get("/csv")
def export_csv(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generates a CSV report detailing student performance across subjects."""
    metrics = calculate_user_metrics(db, current_user.id)
    
    stream = StringIO()
    writer = csv.writer(stream)
    
    # Header Info
    writer.writerow(["STUDENT PROGRESS REPORT"])
    writer.writerow(["Student Username", current_user.username])
    writer.writerow(["Student Email", current_user.email])
    writer.writerow(["Export Date", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")])
    writer.writerow([])
    
    # Overall Performance Summary
    writer.writerow(["OVERALL SUMMARY"])
    writer.writerow(["Metric", "Value"])
    writer.writerow(["Total Quizzes Taken", metrics["total_quizzes"]])
    writer.writerow(["Average Quiz Score (%)", f"{metrics['average_score']}%"])
    writer.writerow(["Total Chat Sessions", metrics["total_chats"]])
    writer.writerow(["Total Spaced Repetition Cards", metrics["total_cards"]])
    writer.writerow([])
    
    # Subject breakdown
    writer.writerow(["SUBJECT-WISE PERFORMANCE"])
    writer.writerow(["Subject", "Quizzes Taken", "Average Quiz Score (%)", "Chat Sessions", "Flashcards Reviewed"])
    for sub, stats in metrics["subject_stats"].items():
        writer.writerow([
            sub,
            stats["quizzes_taken"],
            f"{stats['quiz_average']}%" if stats["quizzes_taken"] > 0 else "N/A",
            stats["chats_started"],
            stats["flashcards_reviewed"]
        ])
    writer.writerow([])
    
    # Detailed Quiz Log
    writer.writerow(["QUIZ HISTORY LOG"])
    writer.writerow(["Date", "Subject", "Topic", "Difficulty", "Score", "Total Questions", "Percentage"])
    for q in metrics["quizzes"]:
        pct = round((q.score / q.total_questions) * 100, 1)
        writer.writerow([
            q.created_at.strftime("%Y-%m-%d %H:%M"),
            q.subject,
            q.topic or "General",
            q.difficulty.title(),
            q.score,
            q.total_questions,
            f"{pct}%"
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
    """Generates a beautifully formatted PDF report containing study statistics."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="PDF generation library is not loaded on server."
        )

    metrics = calculate_user_metrics(db, current_user.id)
    buffer = BytesIO()
    
    # Initialize Document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        name="TitleStyle",
        parent=styles["Heading1"],
        fontSize=24,
        textColor=colors.HexColor("#0f172a"),  # slate-900
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        name="SubtitleStyle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#64748b"),  # slate-500
        spaceAfter=20
    )
    
    section_title_style = ParagraphStyle(
        name="SectionTitle",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.HexColor("#1e293b"),  # slate-800
        spaceBefore=15,
        spaceAfter=10
    )
    
    body_style = ParagraphStyle(
        name="BodyTextCustom",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#334155")   # slate-700
    )
    
    story = []
    
    # Header
    story.append(Paragraph("Educational AI Agent Platform", subtitle_style))
    story.append(Paragraph("Student Academic Progress Report", title_style))
    story.append(Paragraph(f"<b>Student:</b> {current_user.username} ({current_user.email})", body_style))
    story.append(Paragraph(f"<b>Report Generated:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", body_style))
    story.append(Spacer(1, 15))
    
    # Summary Card Table
    story.append(Paragraph("Overall Statistics", section_title_style))
    summary_data = [
        ["Quizzes Taken", "Average Quiz Score", "Chat Sessions", "Flashcards Reviewed"],
        [
            str(metrics["total_quizzes"]),
            f"{metrics['average_score']}%",
            str(metrics["total_chats"]),
            str(metrics["total_cards"])
        ]
    ]
    summary_table = Table(summary_data, colWidths=[130, 130, 130, 130])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),  # slate-100
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, 1), 12),
        ('TEXTCOLOR', (0, 1), (-1, 1), colors.HexColor("#0f172a")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),   # slate-300
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 15))
    
    # Subject breakdown Table
    story.append(Paragraph("Subject Performance Breakdown", section_title_style))
    subject_table_data = [
        ["Subject", "Quizzes Taken", "Average Score", "Chat Sessions", "Flashcards"]
    ]
    for sub, stats in metrics["subject_stats"].items():
        subject_table_data.append([
            sub,
            str(stats["quizzes_taken"]),
            f"{stats['quiz_average']}%" if stats["quizzes_taken"] > 0 else "N/A",
            str(stats["chats_started"]),
            str(stats["flashcards_reviewed"])
        ])
    
    subject_table = Table(subject_table_data, colWidths=[160, 90, 90, 90, 90])
    subject_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#475569")),  # slate-600
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Left align subject names
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),   # slate-200
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")])
    ]))
    story.append(subject_table)
    story.append(Spacer(1, 15))
    
    # Quiz log Table (Show last 10 entries to avoid overflow)
    story.append(Paragraph("Recent Quiz Log (Last 10 Quizzes)", section_title_style))
    quiz_table_data = [
        ["Date", "Subject", "Topic", "Difficulty", "Score", "Percentage"]
    ]
    recent_quizzes = metrics["quizzes"][:10]
    for q in recent_quizzes:
        pct = round((q.score / q.total_questions) * 100, 1)
        quiz_table_data.append([
            q.created_at.strftime("%Y-%m-%d"),
            q.subject,
            q.topic or "General",
            q.difficulty.title(),
            f"{q.score}/{q.total_questions}",
            f"{pct}%"
        ])
        
    if len(recent_quizzes) == 0:
        story.append(Paragraph("No quiz activity recorded yet.", body_style))
    else:
        quiz_table = Table(quiz_table_data, colWidths=[80, 100, 160, 60, 60, 60])
        quiz_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f172a")),  # slate-900
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'LEFT'),  # Left align topics
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#f1f5f9")),   # slate-100
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")])
        ]))
        story.append(quiz_table)
        
    # Build Document
    doc.build(story)
    
    buffer.seek(0)
    response = StreamingResponse(buffer, media_type="application/pdf")
    response.headers["Content-Disposition"] = f"attachment; filename=progress_report_{current_user.username}.pdf"
    return response
