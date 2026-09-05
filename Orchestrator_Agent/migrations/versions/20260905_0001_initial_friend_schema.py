"""Create the existing Friend database schema.

Revision ID: 20260905_0001
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = "20260905_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=100), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_users_id", "users", ["id"], unique=False)
    op.create_index("ix_users_username", "users", ["username"], unique=True)
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "chat_sessions",
        sa.Column("id", sa.String(length=50), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("subject", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_chat_sessions_id", "chat_sessions", ["id"], unique=False)

    op.create_table(
        "chat_messages",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("session_id", sa.String(length=50), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("comparison_table", sa.Text(), nullable=True),
        sa.Column("code", sa.Text(), nullable=True),
        sa.Column("audio_url", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["session_id"], ["chat_sessions.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_chat_messages_id", "chat_messages", ["id"], unique=False)

    op.create_table(
        "quiz_results",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("subject", sa.String(length=50), nullable=False),
        sa.Column("topic", sa.String(length=100), nullable=True),
        sa.Column("difficulty", sa.String(length=20), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("total_questions", sa.Integer(), nullable=False),
        sa.Column("answers_detail", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_quiz_results_id", "quiz_results", ["id"], unique=False)

    op.create_table(
        "flashcard_progress",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("subject", sa.String(length=50), nullable=False),
        sa.Column("topic", sa.String(length=100), nullable=True),
        sa.Column("card_id", sa.String(length=100), nullable=False),
        sa.Column("ease_factor", sa.Float(), nullable=True),
        sa.Column("repetitions", sa.Integer(), nullable=True),
        sa.Column("interval_days", sa.Integer(), nullable=True),
        sa.Column("next_review_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_flashcard_progress_id", "flashcard_progress", ["id"], unique=False)

    op.create_table(
        "flashcard_attempts",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("subject", sa.String(length=50), nullable=False),
        sa.Column("topic", sa.String(length=100), nullable=True),
        sa.Column("difficulty", sa.String(length=20), nullable=True),
        sa.Column("total_cards", sa.Integer(), nullable=False),
        sa.Column("cards_reviewed", sa.Integer(), nullable=False),
        sa.Column("easy_count", sa.Integer(), nullable=True),
        sa.Column("medium_count", sa.Integer(), nullable=True),
        sa.Column("hard_count", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_flashcard_attempts_id", "flashcard_attempts", ["id"], unique=False)

    op.create_table(
        "uploaded_documents",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("file_type", sa.String(length=50), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=True),
        sa.Column("subject", sa.String(length=50), nullable=False),
        sa.Column("topic", sa.String(length=150), nullable=True),
        sa.Column("chunks_count", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_uploaded_documents_id", "uploaded_documents", ["id"], unique=False)


def downgrade() -> None:
    op.drop_table("uploaded_documents")
    op.drop_table("flashcard_attempts")
    op.drop_table("flashcard_progress")
    op.drop_table("quiz_results")
    op.drop_table("chat_messages")
    op.drop_table("chat_sessions")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_username", table_name="users")
    op.drop_index("ix_users_id", table_name="users")
    op.drop_table("users")
