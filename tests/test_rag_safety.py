import json

from src.generation.generator import LegalGenerator
from src.ingestion.chunker import chunk_pages
from src.verification.verifier import AnswerVerifier


class _FailingCompletions:
    def create(self, **_kwargs):
        raise RuntimeError("Ollama is unavailable")


class _UnsupportedCompletions:
    def create(self, **_kwargs):
        return type(
            "Response",
            (), {"choices": [type("Choice", (), {"message": type("Message", (), {"content": json.dumps({"claims": [{"claim": "Unsupported statement", "supported": False}]})})()})()]},
        )()


class _Client:
    def __init__(self, completions):
        self.chat = type("Chat", (), {"completions": completions})()


def test_chunker_preserves_section_and_page_metadata():
    chunks = chunk_pages(
        [{"page_number": 7, "text": "1. First provision. 2. Second provision."}],
        act_name="BNS",
    )

    assert [chunk["section_num"] for chunk in chunks] == ["1", "2"]
    assert all(chunk["pages"] == [7] for chunk in chunks)


def test_generator_refuses_when_all_reranked_chunks_are_below_threshold():
    generator = LegalGenerator.__new__(LegalGenerator)

    result = generator.generate_answer(
        "What is the law on cryptocurrency laundering?",
        [{"text": "Unrelated statute text", "rerank_score": -0.1, "metadata": {}}],
    )

    assert result["answer"].startswith("I cannot answer")
    assert result["valid_chunks"] == []


def test_verifier_fails_closed_when_verification_service_is_unavailable():
    verifier = AnswerVerifier.__new__(AnswerVerifier)
    verifier.client = _Client(_FailingCompletions())
    verifier.model_name = "test"

    result = verifier.verify_and_score(
        "Question",
        "Draft answer",
        [{"text": "Evidence", "rerank_score": 1.0}],
    )

    assert result["status"] == "verification_unavailable"
    assert result["confidence_score"] == 0.0
    assert result["unsupported_flag"] is True


def test_verifier_withholds_an_answer_with_unsupported_claims():
    verifier = AnswerVerifier.__new__(AnswerVerifier)
    verifier.client = _Client(_UnsupportedCompletions())
    verifier.model_name = "test"

    result = verifier.verify_and_score(
        "Question",
        "Draft answer",
        [{"text": "Evidence", "rerank_score": 1.0}],
    )

    assert result["status"] == "refused"
    assert result["confidence_score"] == 0.0
    assert "cannot provide a verified answer" in result["verified_answer"]
