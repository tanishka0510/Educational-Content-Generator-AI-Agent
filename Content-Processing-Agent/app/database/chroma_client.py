"""
ChromaDB Client

Creates and returns the ChromaDB collection.
"""

import chromadb
from chromadb.config import Settings

from app.core.config import settings


class ChromaClient:
    """
    Singleton ChromaDB client.
    """

    _client = None
    _collection = None

    @classmethod
    def get_collection(cls):
        """
        Returns the Chroma collection.
        """

        if cls._client is None:

            cls._client = chromadb.PersistentClient(
                path=settings.CHROMA_DB_PATH,
                settings=Settings(
                    anonymized_telemetry=False
                )
            )

        if cls._collection is None:

            cls._collection = cls._client.get_or_create_collection(
                name="educational_documents"
            )

        return cls._collection