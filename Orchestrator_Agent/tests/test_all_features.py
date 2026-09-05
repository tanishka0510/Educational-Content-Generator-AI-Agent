"""
Comprehensive End-to-End Test Suite for All 3 Feature Requirements
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import SessionLocal, engine, Base
from database.models import User, QuizResult
from database.schemas import QuizResultCreate
from database.crud import create_quiz_result, get_user_quizzes
from api.reports import calculate_user_metrics, export_csv, export_pdf, get_analytics
from api.quizzes import QuizGenerateGatewayRequest
from api.flashcards import FlashcardGenerateGatewayRequest
import json

def test_full_system():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        print("=== 1. VERIFYING USER CREATION & TEST SETUP ===")
        user = db.query(User).filter(User.username == "student_test_user").first()
        if not user:
            user = User(
                username="student_test_user",
                email="student_test@university.edu",
                hashed_password="hashed_secure_password"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        print(f"Verified User: {user.username} (ID: {user.id})")

        print("\n=== 2. VERIFYING QUIZ ATTEMPTS & CONCEPT REMEDIATION TRACKING ===")
        # Scenario: User takes CNS quiz
        # Question 1: initially answered WRONGLY
        q1_attempt_1 = {
            "question": "Which symmetric cipher uses a 56-bit key size?",
            "selected_answer": "AES-256",
            "correct_answer": "DES",
            "is_correct": False,
            "topic": "Symmetric Encryption"
        }
        # Question 2: answered CORRECTLY
        q2_attempt_1 = {
            "question": "What is the primary function of a digital signature?",
            "selected_answer": "Non-repudiation and authentication",
            "correct_answer": "Non-repudiation and authentication",
            "is_correct": True,
            "topic": "Digital Signatures"
        }
        res1 = QuizResultCreate(
            subject="CNS",
            topic="Cryptography Fundamentals",
            difficulty="medium",
            score=1,
            total_questions=2,
            answers_detail=[q1_attempt_1, q2_attempt_1]
        )
        saved1 = create_quiz_result(db, res1, user.id)
        assert saved1.id is not None, "Quiz result 1 should be saved"
        assert saved1.answers_detail is not None, "answers_detail should be stored in DB"
        print(f"Attempt 1 Saved: Score {saved1.score}/{saved1.total_questions}")

        # Scenario 2: User retakes CNS quiz.
        # Question 1 is retaken and NOW ANSWERED CORRECTLY -> Learning progress / Remediation!
        q1_attempt_2 = {
            "question": "Which symmetric cipher uses a 56-bit key size?",
            "selected_answer": "DES",
            "correct_answer": "DES",
            "is_correct": True,
            "topic": "Symmetric Encryption"
        }
        q3_attempt_2 = {
            "question": "What type of attack involves intercepting communication between two parties?",
            "selected_answer": "Man-in-the-middle",
            "correct_answer": "Man-in-the-middle",
            "is_correct": True,
            "topic": "Network Attacks"
        }
        res2 = QuizResultCreate(
            subject="CNS",
            topic="Cryptography Fundamentals",
            difficulty="medium",
            score=2,
            total_questions=2,
            answers_detail=[q1_attempt_2, q3_attempt_2]
        )
        saved2 = create_quiz_result(db, res2, user.id)
        assert saved2.id is not None, "Quiz result 2 should be saved"
        print(f"Attempt 2 Saved: Score {saved2.score}/{saved2.total_questions}")

        print("\n=== 3. VERIFYING COMPREHENSIVE LEARNING METRICS ENGINE ===")
        metrics = calculate_user_metrics(db, user)

        # 1. User Name & Email
        assert metrics["user_name"] == "student_test_user", "User Name must match"
        assert metrics["student_email"] == "student_test@university.edu", "Student Email must match"
        print(f"[OK] User Info: {metrics['user_name']} ({metrics['student_email']})")

        # 2. Report Date
        assert "report_date" in metrics and len(metrics["report_date"]) > 0, "Report Date must be present"
        print(f"[OK] Report Date: {metrics['report_date']}")

        # 3. Overall Progress Status & Narrative
        assert "overall_progress_status" in metrics, "Overall Progress Status must be present"
        print(f"[OK] Overall Progress Status: {metrics['overall_progress_status']}")

        # 4. Comparison of report (delta, trend)
        assert "comparison" in metrics, "Comparison of report must be present"
        print(f"[OK] Report Comparison: Baseline={metrics['comparison']['baseline_avg']}%, Recent={metrics['comparison']['recent_avg']}%, Growth Delta={metrics['comparison']['growth_delta']}%")

        # 5. Learning Progress (Subject-wise & Answer Comparison)
        cns_prog = metrics["subject_learning_progress"]["CNS"]
        assert cns_prog["quizzes_taken"] >= 2, "CNS must have at least 2 quizzes"
        print(f"[OK] CNS Learning Progress: Initial={cns_prog['initial_score']}%, Latest={cns_prog['latest_score']}%, Delta={cns_prog['delta']}%")
        print(f"[OK] Progress Description: {cns_prog['description']}")

        # 6. Remediated Questions
        assert len(metrics["remediated_questions"]) >= 1, "Must detect at least 1 remediated question concept"
        remediated = metrics["remediated_questions"][0]
        print(f"[OK] Remediated Concept Detected: '{remediated['question']}'")
        print(f"[OK] Remediation Story: {remediated['explanation']}")

        # 7. Strengths, Areas for Improvement, Learning Goals, Achievements
        assert len(metrics["strengths"]) > 0, "Strengths must be populated"
        assert len(metrics["areas_for_improvement"]) > 0, "Areas for improvement must be populated"
        assert len(metrics["learning_goals"]) > 0, "Learning goals must be populated"
        assert len(metrics["achievements"]) > 0, "Achievements must be populated"
        print(f"[OK] Strengths Count: {len(metrics['strengths'])}")
        print(f"[OK] Areas for Improvement Count: {len(metrics['areas_for_improvement'])}")
        print(f"[OK] Learning Goals Count: {len(metrics['learning_goals'])}")
        print(f"[OK] Achievements Unlocked: {[a['name'] for a in metrics['achievements'] if a['unlocked']]}")

        print("\n=== 4. VERIFYING CSV EXPORT ===")
        import asyncio
        async def read_streaming_response(resp):
            chunks = []
            async for chunk in resp.body_iterator:
                chunks.append(chunk.encode("utf-8") if isinstance(chunk, str) else chunk)
            return b"".join(chunks)

        csv_resp = export_csv(current_user=user, db=db)
        csv_content = asyncio.run(read_streaming_response(csv_resp)).decode("utf-8")
        assert "STUDENT ACADEMIC PROGRESS & LEARNING REPORT" in csv_content
        assert "student_test_user" in csv_content
        assert "student_test@university.edu" in csv_content
        assert "LEARNING PROGRESS BY SUBJECT" in csv_content
        assert "SUBJECT-WISE PERFORMANCE" in csv_content
        assert "QUIZ / TEST SCORES LOG" in csv_content
        assert "KEY STRENGTHS" in csv_content
        assert "AREAS FOR IMPROVEMENT" in csv_content
        assert "TARGETED LEARNING GOALS" in csv_content
        assert "ACHIEVEMENT MILESTONES" in csv_content
        assert "OVERALL SUMMARY & COMPARISON OF REPORT" in csv_content
        print("[OK] CSV Export contains all 11 required sections perfectly!")

        print("\n=== 5. VERIFYING PDF EXPORT ===")
        pdf_resp = export_pdf(current_user=user, db=db)
        pdf_bytes = asyncio.run(read_streaming_response(pdf_resp))
        assert len(pdf_bytes) > 0, "PDF binary must not be empty"
        print(f"[OK] PDF Export generated successfully ({len(pdf_bytes)} bytes) without errors!")

        print("\n=== 6. VERIFYING ANALYTICS JSON ENDPOINT ===")
        analytics = get_analytics(current_user=user, db=db)
        assert analytics["user_name"] == "student_test_user"
        assert "subject_learning_progress" in analytics
        print("[OK] Analytics JSON endpoint functions perfectly!")

        print("\n>>> ALL SYSTEM TESTS PASSED SUCCESSFULLY! <<<")

    finally:
        db.close()

if __name__ == "__main__":
    test_full_system()
