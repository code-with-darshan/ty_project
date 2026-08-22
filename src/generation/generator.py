from openai import OpenAI
from config.settings import OLLAMA_BASE_URL, OLLAMA_MODEL, RELEVANCE_THRESHOLD


class LegalGenerator:
    """Handles evidence filtering, prompt assembly, and local LLM generation via Ollama."""

    def __init__(self, model_name: str = OLLAMA_MODEL, base_url: str = OLLAMA_BASE_URL):
        self.model_name = model_name
        self.client = OpenAI(
            base_url=base_url,
            api_key="ollama",  # Required by OpenAI SDK, ignored by Ollama
        )

    def _filter_chunks(self, ranked_results: list[dict]) -> list[dict]:
        """Stage 5: Discard chunks falling below the relevance threshold."""
        return [
            chunk
            for chunk in ranked_results
            if chunk.get("rerank_score", -999) >= RELEVANCE_THRESHOLD
        ]

    def _assemble_context(self, valid_chunks: list[dict]) -> str:
        """Binds structural metadata directly to text chunks for citation grounding."""
        context_text = ""
        for index, chunk in enumerate(valid_chunks, start=1):
            meta = chunk.get("metadata", {})
            context_text += f"\n--- EVIDENCE CHUNK {index} ---\n"
            context_text += (
                f"[CITATION: Act: {meta.get('act')} | "
                f"Section: {meta.get('section')} | "
                f"Pages: {meta.get('pages')}]\n"
            )
            context_text += f"TEXT: {chunk['text']}\n"
        return context_text

    def generate_answer(self, query: str, ranked_results: list[dict]) -> dict:
        """Executes the Evidence-First RAG protocol with Llama 3.1."""
        valid_chunks = self._filter_chunks(ranked_results)

        # Layer 1: Evidence-First Refusal Protocol
        if not valid_chunks:
            return {
                "answer": (
                    "I cannot answer this question. I did not find sufficient "
                    "supporting evidence within the available Indian legal texts."
                ),
                "citations": [],
                "confidence": "Insufficient Evidence",
                "valid_chunks": [],
            }

        context_string = self._assemble_context(valid_chunks)

        system_prompt = (
            "You are a Hallucination-Aware Legal Assistant for Indian Law. "
            "Explain the legal provisions clearly in plain English.\n\n"
            "STRICT RULES:\n"
            "1. NO OUTSIDE KNOWLEDGE: Base your entire answer ONLY on the provided Evidence Chunks.\n"
            "2. MANDATORY CITATION: For every legal claim, append the exact citation block: "
            "[CITATION: Act: <act> | Section: <section> | Pages: <pages>].\n"
            "3. If the evidence does not fully answer the question, clearly state what information is missing."
        )

        user_prompt = f"USER QUERY:\n{query}\n\nEVIDENCE CHUNKS:\n{context_string}"

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.0,
            )
            answer_text = response.choices[0].message.content
        except Exception:
            return {
                "answer": (
                    "I cannot answer this question because the local answer "
                    "generation service is unavailable. Please try again later."
                ),
                "citations": [],
                "valid_chunks": [],
            }

        return {
            "answer": answer_text,
            "citations": [c.get("metadata") for c in valid_chunks],
            "valid_chunks": valid_chunks,
        }
