from pathlib import Path
import os
import torch

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
UPLOADS_DIR = BASE_DIR / "data" / "uploads"
CHROMA_DB_DIR = BASE_DIR / "data" / "chroma_db"
STATIC_DOCUMENTS_DIR = BASE_DIR / "src" / "ui" / "static" / "documents"

# Chunking Parameters
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Embedding Model (from your tech stack)
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

# Reranker Model
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
INITIAL_RETRIEVAL_K = 25
RERANK_TOP_K = 4
# Cross-encoder logits below zero are treated as insufficiently relevant.
# Tune this only against a labelled evaluation set.
RELEVANCE_THRESHOLD = -3.0

# Set MODEL_DEVICE=cpu or MODEL_DEVICE=cuda to override automatic selection.
MODEL_DEVICE = os.getenv(
    "MODEL_DEVICE", "cuda" if torch.cuda.is_available() else "cpu"
)

# Local LLM (Ollama)
OLLAMA_BASE_URL = "http://localhost:11434/v1"
OLLAMA_MODEL = "llama3.1"  # Matches Llama 3.1 8B Instruct

# ChromaDB Collection
COLLECTION_NAME = "indian_law"
