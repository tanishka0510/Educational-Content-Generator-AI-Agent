"""
Uploaded ChromaDB Client

Stores uploaded documents separately from
the permanent knowledge base.
"""

import chromadb
from chromadb.config import Settings

from pathlib import Path


class UploadedChromaClient:

    _client = None
    _collection = None

    @classmethod
    def get_collection(cls):

        if cls._client is None:

            base_dir = Path(__file__).resolve().parent.parent.parent

            upload_db = base_dir / "uploaded_db"

            cls._client = chromadb.PersistentClient(
                path=str(upload_db),
                settings=Settings(
                    anonymized_telemetry=False
                )
            )

        if cls._collection is None:

            cls._collection = cls._client.get_or_create_collection(
                name="uploaded_documents"
            )

        return cls._collection