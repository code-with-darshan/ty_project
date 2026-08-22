from sentence_transformers import SentenceTransformer

from config.settings import EMBEDDING_MODEL, MODEL_DEVICE


class Embedder:
    """Generates embeddings for legal documents and user queries."""

    def __init__(self):
        self.model = SentenceTransformer(
            EMBEDDING_MODEL,
            device=MODEL_DEVICE,
        )

    def encode(self, text: str):
        """Generate an embedding for a single text."""
        return self.model.encode(
            text,
            normalize_embeddings=True
        )

    def encode_documents(self, texts: list[str]):
        """Generate embeddings for multiple documents."""
        return self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=True
        )

    def encode_query(self, query: str):
        """Generate an embedding for a user query."""
        return self.model.encode(
            query,
            normalize_embeddings=True
        )
