from src.retrieval.vector_search import VectorSearcher
from src.retrieval.reranker import Reranker


def main():
    query = "What is the punishment for murder?"

    searcher = VectorSearcher()
    reranker = Reranker()

    results = searcher.search(
        query,
        top_k=10,
    )

    print(f"Initial retrieval: {len(results)}")

    reranked_results = reranker.rerank(
        query,
        results,
        top_k=5,
    )

    print(f"After reranking: {len(reranked_results)}")

    for index, result in enumerate(
        reranked_results,
        start=1,
    ):
        print(
            f"\n{index}. "
            f"{result['metadata']}"
        )
        print(
            f"Rerank score: "
            f"{result['rerank_score']:.4f}"
        )
        print(
            f"Text: "
            f"{result['text'][:300]}..."
        )


if __name__ == "__main__":
    main()