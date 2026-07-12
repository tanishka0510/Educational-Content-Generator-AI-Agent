"""
Embedding Model

Loads the embedding model once and reuses it.
"""

from sentence_transformers import SentenceTransformer

from app.core.config import settings


class EmbeddingModel:
    """
    Singleton class for the embedding model.
    """

    _model = None

    @classmethod
    def get_model(cls) -> SentenceTransformer:
        """
        Returns the loaded embedding model.
        """

        if cls._model is None:

            print("=" * 60)
            print("Loading Embedding Model...")
            print(f"Model : {settings.EMBEDDING_MODEL}")

            cls._model = SentenceTransformer(
                settings.EMBEDDING_MODEL
            )

            print("Embedding Model Loaded Successfully.")
            print("=" * 60)

        return cls._model