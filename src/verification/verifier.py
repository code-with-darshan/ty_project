import json
from openai import OpenAI
from config.settings import OLLAMA_BASE_URL, OLLAMA_MODEL


class AnswerVerifier:
    """Implements Chain-of-Verification and Confidence Scoring locally via Ollama."""

    def __init__(self, model_name: str = OLLAMA_MODEL, base_url: str = OLLAMA_BASE_URL):
        self.model_name = model_name
        self.client = OpenAI(
            base_url=base_url,
            api_key="ollama",
        )

    def verify_and_score(
        self,
        query: str,
        generated_answer: str,
        valid_chunks: list[dict],
    ) -> dict:
        if not valid_chunks or generated_answer.startswith("I cannot answer this question"):
            return {
                "verified_answer": generated_answer,
                "unsupported_flag": False,
                "verification_details": [],
                "confidence_score": 0.0,
                "confidence_tier": "Insufficient Evidence — No Answer Generated",
                "status": "refused",
            }

        context_text = ""
        for idx, chunk in enumerate(valid_chunks, start=1):
            context_text += f"[Chunk {idx}]: {chunk['text']}\n"

        verification_prompt = (
            "You are an independent legal verification auditor.\n"
            "Check the DRAFT ANSWER against the PROVIDED EVIDENCE CHUNKS.\n\n"
            "TASKS:\n"
            "1. Decompose the DRAFT ANSWER into discrete claims.\n"
            "2. Determine if each claim is directly supported by the evidence.\n"
            "3. Output valid JSON in this exact structure:\n"
            '{"claims": [{"claim": "...", "supported": true}]}\n\n'
            "Strictly do not use outside knowledge."
        )

        user_content = (
            f"PROVIDED EVIDENCE CHUNKS:\n{context_text}\n\n"
            f"DRAFT ANSWER TO AUDIT:\n{generated_answer}"
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": verification_prompt},
                    {"role": "user", "content": user_content},
                ],
                response_format={"type": "json_object"},
                temperature=0.0,
            )
            raw_content = response.choices[0].message.content.strip()
            
            # Clean up markdown code blocks if Llama 3 ignores json_object format
            if raw_content.startswith("```json"):
                raw_content = raw_content[7:]
            if raw_content.startswith("```"):
                raw_content = raw_content[3:]
            if raw_content.endswith("```"):
                raw_content = raw_content[:-3]
            raw_content = raw_content.strip()

            audit_result = json.loads(raw_content)
            claims_audit = audit_result.get("claims", [])
            
            if not isinstance(claims_audit, list) or not claims_audit:
                raise ValueError("Verifier returned no claims")
            if not all(isinstance(item, dict) and "supported" in item for item in claims_audit):
                raise ValueError("Verifier returned an invalid claim schema")
                
        except Exception as e:
            print(f"[DEBUG] Verification failed: {e}")
            if 'raw_content' in locals():
                print(f"[DEBUG] Raw content was: {raw_content}")
            return {
                "verified_answer": (
                    "I cannot provide a verified answer because the answer-verification "
                    "service was unavailable. Please try again later."
                ),
                "unsupported_flag": True,
                "verification_details": [],
                "confidence_score": 0.0,
                "confidence_tier": "Verification Unavailable — No Answer Generated",
                "status": "verification_unavailable",
            }

        total_claims = len(claims_audit)
        supported_claims = sum(1 for item in claims_audit if item.get("supported", False))

        # 2. Base Verification Ratio
        verification_ratio = (supported_claims / total_claims) if total_claims > 0 else 1.0
        unsupported_flag = supported_claims < total_claims

        # 3. Base Reranker Confidence
        # Reranker scores from MS MARCO usually range -10 to +10. We normalize roughly.
        avg_rerank = sum(c.get("rerank_score", 0.0) for c in valid_chunks) / len(valid_chunks)
        normalized_rerank = max(0.0, min(1.0, (avg_rerank + 1.0) / 2.0))

        # 4. Composite Confidence Score (60% Verification, 40% Retrieval Quality)
        composite_score = round(((verification_ratio * 0.6) + (normalized_rerank * 0.4)) * 100, 1)

        # Layer 2: Verification Quality Refusal
        if composite_score < 40:
            return {
                "verified_answer": (
                    "I cannot provide a verified answer because the retrieved legal "
                    "evidence was not sufficiently relevant to the question."
                ),
                "unsupported_flag": True,
                "verification_details": claims_audit,
                "confidence_score": 0.0,
                "confidence_tier": "Insufficient Evidence — No Answer Generated",
                "status": "refused",
            }

        # Layer 3: Contextual Hallucination Refusal
        if unsupported_flag:
            return {
                "verified_answer": (
                    "I cannot provide a verified answer because one or more claims "
                    "were not supported by the retrieved legal text."
                ),
                "unsupported_flag": True,
                "verification_details": claims_audit,
                "confidence_score": composite_score,
                "confidence_tier": f"Hallucination Detected — No Answer Generated ({composite_score}%)",
                "status": "refused",
            }

        # Layer 4: Verified Answer
        # Final tiering based on combined confidence
        if composite_score >= 80:
            tier = "High Confidence"
        elif 40 <= composite_score < 80:
            tier = "Moderate Confidence"
            
        return {
            "verified_answer": generated_answer,
            "unsupported_flag": False,
            "verification_details": claims_audit,
            "confidence_score": composite_score,
            "confidence_tier": f"{tier} ({composite_score}%)",
            "status": "verified",
        }
