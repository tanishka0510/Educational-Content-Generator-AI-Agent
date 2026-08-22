"""
Database Connection Manager

Project: Educational Content Generator AI
Module: Orchestrator Agent (Gateway)
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Resolves database URL, defaulting to SQLite local database.
# For production, set DATABASE_URL to a PostgreSQL connection string.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database.db")

# Configure connection args based on dialect
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    # Standard PostgreSQL settings
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

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
