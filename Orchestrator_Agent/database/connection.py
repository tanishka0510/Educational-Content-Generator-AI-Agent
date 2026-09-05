"""
Database Connection Manager

Project: Educational Content Generator AI
Module: Orchestrator Agent (Gateway)
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_SQLITE_PATH = os.path.join(BASE_DIR, "database.db").replace("\\", "/")

def get_database_url() -> str:
    """Return the configured URL, retaining the existing local SQLite default."""
    database_url = os.getenv("DATABASE_URL", "").strip()
    if not database_url or database_url in ("sqlite:///./database.db", "sqlite:///database.db"):
        return f"sqlite:///{DEFAULT_SQLITE_PATH}"

    # Some hosted PostgreSQL services still provide the legacy postgres:// form.
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    return database_url


DATABASE_URL = get_database_url()

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    # Do not silently fall back to SQLite when production PostgreSQL is unavailable.
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    FastAPI Dependency that provides a database session.
    Ensures the connection is closed when the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

