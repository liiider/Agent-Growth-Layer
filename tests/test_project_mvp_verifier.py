from __future__ import annotations

from typing import Any

from scripts.verify_project_mvp import ProjectMvpVerifier


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

    def get(self, url: str) -> FakeResponse:
        if url.endswith("/health"):
            return FakeResponse({"status": "ok"})
        if url.endswith("/v1/experiences/exp_1"):
            return FakeResponse(
                {
                    "extraction_status": "succeeded",
                    "cognition_ids": ["cog_1"],
                }
            )
        return FakeResponse({})

    def post(self, url: str, json: dict[str, Any]) -> FakeResponse:
        self.posts.append((url, json))
        if url.endswith("/v1/guidance") and len([u for u, _ in self.posts if u == url]) == 1:
            return FakeResponse({"guidance": {"seed_skills": [{"id": "seed_1"}]}})
        if url.endswith("/v1/experiences"):
            return FakeResponse({"experience_id": "exp_1"})
        if url.endswith("/v1/reviews") and json["object_type"] == "experience":
            return FakeResponse({"review_id": "rev_1", "new_status": None})
        if url.endswith("/v1/reviews") and json["object_type"] == "cognition":
            return FakeResponse({"review_id": "rev_2", "new_status": "verified"})
        if url.endswith("/v1/skills/build"):
            return FakeResponse({"skill": {"id": "skill_1", "status": "candidate"}})
        if url.endswith("/v1/skills/skill_1/exam"):
            return FakeResponse({"passed": True, "new_status": "needs_review"})
        if url.endswith("/v1/reviews") and json["object_type"] == "skill":
            return FakeResponse({"review_id": "rev_3", "new_status": "verified"})
        if url.endswith("/v1/guidance"):
            return FakeResponse(
                {
                    "guidance": {
                        "seed_skills": [],
                        "verified_skills": [{"id": "skill_1"}],
                    }
                }
            )
        return FakeResponse({})


def test_project_mvp_verifier_runs_project_review_gate_flow() -> None:
    verifier = ProjectMvpVerifier(
        "http://example.test",
        poll_interval_seconds=0,
        max_wait_seconds=1,
    )
    fake_client = FakeClient()
    verifier.client = fake_client  # type: ignore[assignment]

    verifier.run()

    posted_urls = [url for url, _ in fake_client.posts]
    assert posted_urls == [
        "http://example.test/v1/guidance",
        "http://example.test/v1/experiences",
        "http://example.test/v1/reviews",
        "http://example.test/v1/reviews",
        "http://example.test/v1/skills/build",
        "http://example.test/v1/skills/skill_1/exam",
        "http://example.test/v1/reviews",
        "http://example.test/v1/guidance",
    ]
    exam_body = fake_client.posts[5][1]
    assert exam_body["require_human_review"] is True
