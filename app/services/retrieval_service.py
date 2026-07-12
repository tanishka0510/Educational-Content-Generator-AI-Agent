"""
Retrieval Service

Performs semantic search on ChromaDB.
"""

from app.database.chroma_client import ChromaClient
from app.embeddings.embedding_model import EmbeddingModel


class RetrievalService:
    """
    Performs semantic retrieval from ChromaDB.
    """

    @staticmethod
    def search(
        query: str,
        top_k: int = 5
    ) -> dict:
        """
        Search the vector database.
        """

        # -------------------------------
        # Load embedding model
        # -------------------------------
        model = EmbeddingModel.get_model()

        # -------------------------------
        # Generate query embedding
        # -------------------------------
        query_embedding = model.encode(
            query,
            convert_to_numpy=True
        ).tolist()

        # -------------------------------
        # Get Chroma collection
        # -------------------------------
        collection = ChromaClient.get_collection()

        # -------------------------------
        # Perform similarity search
        # Fetch extra results to remove duplicates
        # -------------------------------
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k * 3,
            include=[
                "documents",
                "metadatas",
                "distances"
            ]
        )

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        unique_documents = []
        unique_metadatas = []
        unique_distances = []

        seen_text = set()

        for doc, meta, dist in zip(documents, metadatas, distances):

            # Use first 200 characters as a fingerprint
            text_key = " ".join(doc.split())[:300]

            if text_key in seen_text:
                continue

            seen_text.add(text_key)

            unique_documents.append(doc)
            unique_metadatas.append(meta)
            unique_distances.append(dist)

            if len(unique_documents) == top_k:
                break

        return {
            "documents": [unique_documents],
            "metadatas": [unique_metadatas],
            "distances": [unique_distances]
        }