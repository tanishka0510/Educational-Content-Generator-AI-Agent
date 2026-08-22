"""
Chroma Service

Stores document chunks inside ChromaDB.
"""

from app.models.document import Document
from app.database.uploaded_chroma_client import UploadedChromaClient


class ChromaService:
    """
    Handles ChromaDB operations.
    """

    @staticmethod
    def store(document: Document) -> Document:
        """
        Store all document chunks in ChromaDB.
        """

        collection = UploadedChromaClient.get_collection()

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
            print("\n========== UPLOADED DATABASE ==========")
            print("Collection :", collection.name)
            print("Total Documents :", collection.count())
            print("=======================================\n")
        return document
    