from sentence_transformers import CrossEncoder

from config.settings import MODEL_DEVICE, RERANKER_MODEL, RERANK_TOP_K


class Reranker:
    """Reranks retrieved legal chunks using a cross-encoder."""

    def __init__(self):
        self.model = CrossEncoder(
            RERANKER_MODEL,
            device=MODEL_DEVICE,
        )

    def rerank(
        self,
        query: str,
        results: list[dict],
        top_k: int = RERANK_TOP_K,
    ) -> list[dict]:
        """Rerank retrieved chunks and return the strongest evidence."""

        if not results:
            return []

        pairs = [
            [query, result["text"]]
            for result in results
        ]

        scores = self.model.predict(pairs)

        ranked_results = []

        for result, score in zip(results, scores):
            ranked_result = result.copy()
            ranked_result["rerank_score"] = float(score)
            ranked_results.append(ranked_result)

        ranked_results.sort(
            key=lambda item: item["rerank_score"],
            reverse=True,
        )

        return ranked_results[:top_k]
