"""
End-to-End Persistence Verification Test
Tests PostgreSQL/SQLite connection, chat sessions, message storage,
quiz attempt persistence, flashcard attempt logging, and uploaded document tracking.
"""
import os
import sys
import unittest
import uuid

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import SessionLocal, engine
from database.models import Base
from database import crud
from database.schemas import (
    ChatSessionCreate, ChatMessageCreate,
    FlashcardAttemptCreate, UploadedDocumentCreate,
    QuizResultCreate
)

class TestDatabasePersistence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        cls.db = SessionLocal()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_01_user_and_guest_fallback(self):
        guest = crud.get_or_create_guest_user(self.db)
        self.assertIsNotNone(guest)
        self.assertEqual(guest.username, "guest")
        self.assertIsNotNone(guest.id)

    def test_02_session_and_chat_history(self):
        guest = crud.get_or_create_guest_user(self.db)
        session_id = f"test-session-{uuid.uuid4()}"
        session_data = ChatSessionCreate(
            id=session_id,
            subject="Physics",
            title="Quantum Computing Study"
        )
        session = crud.create_session(self.db, session_data, user_id=guest.id)
        self.assertIsNotNone(session.id)
        self.assertEqual(session.title, "Quantum Computing Study")

        # Save user message
        msg1_data = ChatMessageCreate(
            role="user",
            content="What is superposition?"
        )
        msg1 = crud.create_chat_message(self.db, msg1_data, session_id=session.id)
        self.assertIsNotNone(msg1.id)

        # Save assistant message with comparison_table and code
        msg2_data = ChatMessageCreate(
            role="assistant",
            content="Superposition allows quantum bits to represent 0 and 1 simultaneously.",
            comparison_table=[{"Parameter": "Classical Bit", "Quantum Bit": "Qubit"}],
            code="# Qubit state\npsi = alpha * |0> + beta * |1>",
            audio_url="/static/audio/test.mp3"
        )
        msg2 = crud.create_chat_message(self.db, msg2_data, session_id=session.id)
        self.assertIsNotNone(msg2.id)

        # Retrieve session with messages
        fetched_session = crud.get_session_by_id(self.db, session.id)
        self.assertIsNotNone(fetched_session)
        self.assertGreaterEqual(len(fetched_session.messages), 2)

        # Rename session
        updated = crud.rename_session(self.db, session.id, "Advanced Quantum Mechanics")
        self.assertEqual(updated.title, "Advanced Quantum Mechanics")

    def test_03_quiz_results_persistence(self):
        guest = crud.get_or_create_guest_user(self.db)
        quiz_data = QuizResultCreate(
            subject="Computer Science",
            topic="Data Structures",
            difficulty="Medium",
            score=8,
            total_questions=10,
            answers_detail=[
                {"question": "What is the time complexity of binary search?", "user_answer": "O(log n)", "correct": True},
                {"question": "Is a stack FIFO or LIFO?", "user_answer": "FIFO", "correct": False}
            ]
        )
        saved_quiz = crud.create_quiz_result(self.db, quiz_data, user_id=guest.id)
        self.assertIsNotNone(saved_quiz.id)
        self.assertEqual(saved_quiz.subject, "Computer Science")

        # Retrieve history
        history = crud.get_user_quizzes(self.db, user_id=guest.id)
        self.assertGreaterEqual(len(history), 1)

    def test_04_flashcard_attempts_persistence(self):
        guest = crud.get_or_create_guest_user(self.db)
        flashcard_data = FlashcardAttemptCreate(
            subject="Biology",
            topic="Cellular Respiration",
            difficulty="Medium",
            total_cards=15,
            cards_reviewed=15,
            easy_count=8,
            medium_count=5,
            hard_count=2
        )
        attempt = crud.create_flashcard_attempt(self.db, flashcard_data, user_id=guest.id)
        self.assertIsNotNone(attempt.id)
        self.assertEqual(attempt.subject, "Biology")
        self.assertEqual(attempt.easy_count, 8)

        # Retrieve history
        attempts = crud.get_user_flashcard_attempts(self.db, user_id=guest.id)
        self.assertGreaterEqual(len(attempts), 1)

    def test_05_uploaded_documents_persistence(self):
        guest = crud.get_or_create_guest_user(self.db)
        doc_data = UploadedDocumentCreate(
            filename="chapter4_thermodynamics.pdf",
            file_type=".pdf",
            file_size=1048576,
            subject="Physics",
            topic="Thermodynamics",
            chunks_count=42,
            status="processed"
        )
        doc = crud.create_uploaded_document(self.db, doc_data, user_id=guest.id)
        self.assertIsNotNone(doc.id)
        self.assertEqual(doc.filename, "chapter4_thermodynamics.pdf")

        # Retrieve documents
        docs = crud.get_user_documents(self.db, user_id=guest.id)
        self.assertTrue(any(d.id == doc.id for d in docs))

        # Retrieve by id
        fetched = crud.get_document_by_id(self.db, doc.id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.filename, "chapter4_thermodynamics.pdf")

        # Delete document
        deleted = crud.delete_uploaded_document(self.db, doc.id, user_id=guest.id)
        self.assertTrue(deleted)
        self.assertIsNone(crud.get_document_by_id(self.db, doc.id))

if __name__ == "__main__":
    unittest.main()
