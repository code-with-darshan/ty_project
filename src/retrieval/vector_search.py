import chromadb
from rank_bm25 import BM25Okapi

from config.settings import (
    CHROMA_DB_DIR,
    COLLECTION_NAME,
    INITIAL_RETRIEVAL_K,
)
from src.embeddings.embedder import Embedder

class VectorSearcher:
    """Performs Hybrid Search (Semantic + BM25) over the legal knowledge base."""

    def __init__(self):
        self.embedder = Embedder()
        self.client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))
        self.collection = self.client.get_collection(name=COLLECTION_NAME)

        # Fetch all documents from ChromaDB to build the BM25 Index in memory
        print("Initializing Hybrid Search Index (BM25 + Dense Vectors)...")
        all_data = self.collection.get(include=["documents", "metadatas"])
        self.all_ids = all_data["ids"]
        self.all_documents = all_data["documents"]
        self.all_metadatas = all_data["metadatas"]

        # Simple tokenization for the sparse BM25 index
        tokenized_corpus = [doc.lower().split() for doc in self.all_documents]
        self.bm25 = BM25Okapi(tokenized_corpus)

    def search(
        self,
        query: str,
        top_k: int = INITIAL_RETRIEVAL_K,
    ) -> list[dict]:
        """Retrieve chunks using both Dense Vectors and Sparse BM25 Keyword matching."""

        # -----------------------------------------
        # 1. DENSE VECTOR SEARCH (Semantic Meaning)
        # -----------------------------------------
        query_embedding = self.embedder.encode_query(query)
        vector_results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            include=["documents", "metadatas"],
        )

        # -----------------------------------------
        # 2. SPARSE BM25 SEARCH (Exact Keywords)
        # -----------------------------------------
        tokenized_query = query.lower().split()
        bm25_scores = self.bm25.get_scores(tokenized_query)
        
        # Get the indices of the top_k BM25 scores
        top_bm25_indices = sorted(
            range(len(bm25_scores)), 
            key=lambda i: bm25_scores[i], 
            reverse=True
        )[:top_k]

        # -----------------------------------------
        # 3. RECIPROCAL RANK FUSION (RRF)
        # -----------------------------------------
        # RRF Formula: Score = 1 / (k + rank)
        rrf_k = 60
        fused_scores = {}

        # Add Vector Search Results to Fusion pool
        for rank, doc_id in enumerate(vector_results["ids"][0]):
            if doc_id not in fused_scores:
                fused_scores[doc_id] = {
                    "score": 0.0, 
                    "text": vector_results["documents"][0][rank], 
                    "metadata": vector_results["metadatas"][0][rank]
                }
            fused_scores[doc_id]["score"] += 1.0 / (rrf_k + rank + 1)

        # Add BM25 Results to Fusion pool
        for rank, idx in enumerate(top_bm25_indices):
            doc_id = self.all_ids[idx]
            if doc_id not in fused_scores:
                fused_scores[doc_id] = {
                    "score": 0.0, 
                    "text": self.all_documents[idx], 
                    "metadata": self.all_metadatas[idx]
                }
            fused_scores[doc_id]["score"] += 1.0 / (rrf_k + rank + 1)

        # -----------------------------------------
        # 4. SORT AND RETURN
        # -----------------------------------------
        # Sort the fused dictionary by the highest RRF score
        sorted_fused = sorted(fused_scores.items(), key=lambda x: x[1]["score"], reverse=True)

        retrieved_chunks = []
        for doc_id, data in sorted_fused[:top_k]:
            retrieved_chunks.append(
                {
                    "text": data["text"],
                    "metadata": data["metadata"],
                    "rrf_score": data["score"],  # Passing the fusion score instead of raw distance
                }
            )

        return retrieved_chunks