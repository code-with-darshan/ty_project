from src.retrieval.vector_search import VectorSearcher
from src.retrieval.reranker import Reranker
from src.retrieval.query_expander import QueryExpander
from src.generation.generator import LegalGenerator
from src.verification.verifier import AnswerVerifier
from src.safety.incident_response import get_incident_guide

class LegalRAGPipeline:
    """End-to-End Hallucination-Aware RAG Lifecycle."""

    def __init__(self):
        self.expander = QueryExpander()                                                                       
        self.searcher = VectorSearcher()
        self.reranker = Reranker()
        self.generator = LegalGenerator()
        self.verifier = AnswerVerifier()

    def query(self, user_query: str) -> dict:
        incident_guide = get_incident_guide(user_query)
        # 0. Query Expansion (Translate slang to legal terms)
        expanded_search_query = self.expander.expand_query(user_query)
        print(f"\n[DEBUG] Expanded Query: {expanded_search_query}")

        # 1. Similarity Search (ChromaDB + BM25 using the EXPANDED query)
        raw_results = self.searcher.search(expanded_search_query)

        # 2. Re-ranking Pass (Cross-Encoder using the ORIGINAL query for accurate relevance to the user)
        ranked_results = self.reranker.rerank(user_query, raw_results)

        # 3 & 4. Relevance Filter & Evidence-First Generation
        generation_output = self.generator.generate_answer(user_query, ranked_results)
        valid_chunks = generation_output.get("valid_chunks", [])

        # 5 & 6. Secondary Verification & Confidence Scoring
        final_response = self.verifier.verify_and_score(
            user_query, 
            generation_output["answer"], 
            valid_chunks
        )

        answer_allowed = final_response["status"] == "verified"

        return {
            "query": user_query,
            "answer": final_response["verified_answer"],
            "citations": generation_output.get("citations", []) if answer_allowed else [],
            "confidence_score": final_response["confidence_score"],
            "confidence_tier": final_response["confidence_tier"],
            "unsupported_content_flag": final_response["unsupported_flag"],
            "verification_details": final_response["verification_details"],
            "answer_status": final_response["status"],
            "incident_guide": incident_guide,
        }
if __name__ == "__main__":
    pipeline = LegalRAGPipeline()
    sample_query = "What is the punishment for murder under BNS?"
    result = pipeline.query(sample_query)
    
    print("\n" + "=" * 60)
    print("FINAL RESPONSE")
    print("=" * 60)
    print(f"Answer:\n{result['answer']}\n")
    print(f"Confidence Tier: {result['confidence_tier']} ({result['confidence_score']}%)")
    print(f"Citations: {result['citations']}")
