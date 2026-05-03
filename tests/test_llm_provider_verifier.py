from __future__ import annotations

from typing import Any

from scripts.verify_llm_provider import LlmProviderVerifier


class FakeResponse:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, Any]:
        return self.payload


class FakeClient:
    def __init__(self) -> None:
        self.posts: list[tuple[str, dict[str, Any]]] = []
        self.gets: list[str] = []

    def post(self, url: str, json: dict[str, Any]) -> FakeResponse:
        self.posts.append((url, json))
        if url.endswith("/v1/experiences"):
            return FakeResponse({"experience_id": "exp_1"})
        if url.endswith("/v1/skills/import_prompt"):
            return FakeResponse(
                {
                    "skill": {
                        "id": "skill_imported_1",
                        "status": "candidate",
                        "procedure": ["Check order status"],
                        "constraints": ["Never promise approval"],
                    }
                }
            )
        if url.endswith("/v1/skills/build"):
            return FakeResponse({"skill": {"id": "skill_1"}})
        if url.endswith("/v1/skills/skill_1/exam"):
            return FakeResponse(
                {
                    "score": 0.82,
                    "passed": True,
                    "new_status": "verified",
                    "failures": [],
                }
            )
        return FakeResponse({})

    def get(self, url: str) -> FakeResponse:
        self.gets.append(url)
        if url.endswith("/v1/experiences/exp_1"):
            return FakeResponse(
                {
                    "extraction_status": "succeeded",
                    "cognition_ids": ["cog_1"],
                }
            )
        if url.endswith("/v1/cognitions/cog_1"):
            return FakeResponse(
                {
                    "id": "cog_1",
                    "type": "procedure",
                    "content": "Check refund facts before answering.",
                    "confidence": 0.81,
                    "weight": "medium",
                }
            )
        return FakeResponse({})


def test_llm_provider_verifier_exercises_all_llm_paths() -> None:
    fake_client = FakeClient()
    verifier = LlmProviderVerifier(
        "http://example.test",
        poll_interval_seconds=0,
        max_wait_seconds=1,
    )
    verifier.client = fake_client  # type: ignore[assignment]

    verifier.run()

    posted_urls = [url for url, _ in fake_client.posts]
    assert posted_urls == [
        "http://example.test/v1/experiences",
        "http://example.test/v1/skills/import_prompt",
        "http://example.test/v1/skills/build",
        "http://example.test/v1/skills/skill_1/exam",
    ]
    exam_body = fake_client.posts[-1][1]
    assert exam_body["evaluator"] == "llm_judge"
    assert "score" not in exam_body
