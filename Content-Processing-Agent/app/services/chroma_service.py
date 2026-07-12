"""
Chroma Service

Stores document chunks inside ChromaDB.
"""

from app.models.document import Document
from app.database.chroma_client import ChromaClient


class ChromaService:
    """
    Handles ChromaDB operations.
    """

    @staticmethod
    def store(document: Document) -> Document:
        """
        Store all document chunks in ChromaDB.
        """

        collection = ChromaClient.get_collection()

        for chunk in document.chunks:

            collection.add(

                ids=[
                    chunk.chunk_id
                ],

                documents=[
                    chunk.text
                ],

                embeddings=[
                    chunk.embedding
                ],

                metadatas=[

                    {

                        "document_id": document.document_id,

                        "filename": document.filename,

                        "subject": document.subject,

                        "language": document.language,

                        "chunk_index": chunk.chunk_index

                    }

                ]

            )

        return document