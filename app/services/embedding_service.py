"""
Embedding Service

Generates embeddings for every document chunk.
"""

from app.models.document import Document
from app.embeddings.embedding_model import EmbeddingModel


class EmbeddingService:
    """
    Creates embeddings for all chunks.
    """

    @staticmethod
    def process(document: Document) -> Document:
        """
        Generate embeddings for each chunk.
        """

        # Nothing to embed
        if not document.chunks:
            return document

        # Load embedding model
        model = EmbeddingModel.get_model()

        # Extract text from all chunks
        texts = [chunk.text for chunk in document.chunks]

        # Generate embeddings in one batch
        embeddings = model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=False
        )

        # Attach embedding to its corresponding chunk
        for chunk, embedding in zip(document.chunks, embeddings):
            chunk.embedding = embedding.tolist()

        return document