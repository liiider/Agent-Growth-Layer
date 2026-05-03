from __future__ import annotations

from typing import Any

from scripts.verify_local_mvp import LocalMvpVerifier


class FakeResponse:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, Any]:
        return self.payload


class FakeClient:
    def __init__(self) -> None:
        self.calls = 0

    def get(self, url: str) -> FakeResponse:
        self.calls += 1
        if self.calls == 1:
            return FakeResponse(
                {
                    "id": "exp_1",
                    "extraction_status": "processing",
                    "cognition_ids": [],
                }
            )
        return FakeResponse(
            {
                "id": "exp_1",
                "extraction_status": "succeeded",
                "cognition_ids": ["cog_1"],
            }
        )


def test_wait_for_extraction_polls_until_succeeded() -> None:
    verifier = LocalMvpVerifier("http://example.test", poll_interval_seconds=0, max_wait_seconds=1)
    fake_client = FakeClient()
    verifier.client = fake_client  # type: ignore[assignment]

    experience = verifier.wait_for_extraction("exp_1")

    assert experience["extraction_status"] == "succeeded"
    assert experience["cognition_ids"] == ["cog_1"]
    assert fake_client.calls == 2
