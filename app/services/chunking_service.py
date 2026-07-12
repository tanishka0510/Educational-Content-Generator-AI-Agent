"""
Chunking Service

Creates text chunks from a processed document.
"""

from app.models.document import Document
from app.models.chunk import Chunk
from app.chunkers.text_chunker import TextChunker


class ChunkingService:
    """
    Handles document chunk creation.
    """

    @staticmethod
    def process(document: Document) -> Document:

        chunker = TextChunker()

        split_text = chunker.chunk(document.cleaned_text)

        chunks = []

        for index, text in enumerate(split_text):

            chunk = Chunk(
                document_id=document.document_id,
                chunk_index=index,
                text=text,
                metadata={
                    "filename": document.filename,
                    "subject": document.subject,
                    "language": document.language,
                }
            )

            chunks.append(chunk)

        document.chunks = chunks

        return document