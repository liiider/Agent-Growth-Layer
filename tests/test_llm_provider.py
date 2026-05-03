from __future__ import annotations

from typing import Any

import httpx
import pytest
from fastapi.testclient import TestClient

from server.api import experiences as experiences_api
from server.api import skills as skills_api
from server.core.llm import OpenAICompatibleChatClient
from server.main import app


class FakeChatClient:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.payload = payload
        self.calls: list[list[dict[str, str]]] = []

    def complete_json(self, messages: list[dict[str, str]]) -> dict[str, Any]:
        self.calls.append(messages)
        return self.payload


def test_openai_compatible_client_sends_byok_chat_completion(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def fake_post(
        url: str,
        *,
        headers: dict[str, str],
        json: dict[str, Any],
        timeout: float,
    ) -> httpx.Response:
        captured.update(
            {
                "url": url,
                "headers": headers,
                "json": json,
                "timeout": timeout,
            }
        )
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": '{"score": 0.9}'}}]},
            request=httpx.Request("POST", url),
        )

    monkeypatch.setattr(httpx, "post", fake_post)
    client = OpenAICompatibleChatClient(
        base_url="https://example.test/v1/",
        api_key="test-key",
        model="glm-test",
        timeout_seconds=12,
    )

    result = client.complete_json([{"role": "user", "content": "judge"}])

    assert result == {"score": 0.9}
    assert captured["url"] == "https://example.test/v1/chat/completions"
    assert captured["headers"]["Authorization"] == "Bearer test-key"
    assert captured["json"]["model"] == "glm-test"
    assert captured["json"]["response_format"] == {"type": "json_object"}
    assert captured["timeout"] == 12


def test_experience_extraction_can_use_llm_client(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_client = FakeChatClient(
        {
            "type": "procedure",
            "content": "Check region and order status before answering refund questions.",
            "confidence": 0.91,
            "weight": "high",
        }
    )
    monkeypatch.setattr(experiences_api, "build_chat_client", lambda settings: fake_client)
    client = TestClient(app)

    experience_id = client.post(
        "/v1/experiences",
        json={
            "agent_id": "support_agent",
            "domain": "customer_support",
            "intent": "refund_question",
            "user_input": "Refund?",
            "agent_output": "No refund.",
            "feedback": "Need better policy checks.",
            "result_status": "corrected",
            "risk_level": "high",
        },
    ).json()["experience_id"]
    experience = client.get(f"/v1/experiences/{experience_id}").json()
    cognition = client.get(f"/v1/cognitions/{experience['cognition_ids'][0]}").json()

    assert cognition["type"] == "procedure"
    assert (
        cognition["content"]
        == "Check region and order status before answering refund questions."
    )
    assert cognition["confidence"] == 0.91
    assert cognition["weight"] == "high"
    assert fake_client.calls


def test_experience_extraction_normalizes_provider_schema_variants(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_client = FakeChatClient(
        {
            "type": "check",
            "content": "Check refund facts before answering.",
            "confidence": "0.84",
            "weight": 0.8,
        }
    )
    monkeypatch.setattr(experiences_api, "build_chat_client", lambda settings: fake_client)
    client = TestClient(app)

    experience_id = client.post(
        "/v1/experiences",
        json={
            "agent_id": "support_agent",
            "domain": "customer_support",
            "intent": "refund_question",
            "user_input": "Refund?",
            "agent_output": "No refund.",
            "feedback": "Need better policy checks.",
            "result_status": "corrected",
            "risk_level": "medium",
        },
    ).json()["experience_id"]
    experience = client.get(f"/v1/experiences/{experience_id}").json()
    cognition = client.get(f"/v1/cognitions/{experience['cognition_ids'][0]}").json()

    assert cognition["type"] == "rule"
    assert cognition["confidence"] == 0.84
    assert cognition["weight"] == "high"


def test_prompt_import_can_use_llm_client(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_client = FakeChatClient(
        {
            "name": "Refund Guardrails",
            "procedure": ["Check order status", "Check region policy"],
            "constraints": ["Never promise approval"],
            "confidence": 0.88,
            "weight": "medium",
        }
    )
    monkeypatch.setattr(skills_api, "build_chat_client", lambda settings: fake_client)
    client = TestClient(app)

    response = client.post(
        "/v1/skills/import_prompt",
        json={
            "agent_id": "support_agent",
            "domain": "customer_support",
            "intent": "refund_question",
            "prompt": "Always check order status. Never promise refund approval.",
        },
    )

    assert response.status_code == 200
    skill = response.json()["skill"]
    assert skill["name"] == "Refund Guardrails"
    assert skill["procedure"] == ["Check order status", "Check region policy"]
    assert skill["constraints"] == ["Never promise approval"]
    assert skill["confidence"] == 0.88
    assert fake_client.calls


def test_llm_judge_can_score_exam_with_byok_client(monkeypatch: pytest.MonkeyPatch) -> None:
    client = TestClient(app)
    experience_id = client.post(
        "/v1/experiences",
        json={
            "agent_id": "support_agent",
            "domain": "customer_support",
            "intent": "refund_question",
            "user_input": "Refund?",
            "agent_output": "No refund.",
            "feedback": "Check order status first.",
            "result_status": "corrected",
            "risk_level": "medium",
        },
    ).json()["experience_id"]
    cognition_id = client.get(f"/v1/experiences/{experience_id}").json()["cognition_ids"][0]
    skill = client.post(
        "/v1/skills/build",
        json={
            "agent_id": "support_agent",
            "domain": "customer_support",
            "intent": "refund_question",
            "name": "Refund Policy Handling",
            "cognition_ids": [cognition_id],
        },
    ).json()["skill"]

    fake_client = FakeChatClient({"score": 0.82, "failures": []})
    monkeypatch.setattr(skills_api, "build_chat_client", lambda settings: fake_client)
    exam = client.post(
        f"/v1/skills/{skill['id']}/exam",
        json={
            "evaluator": "llm_judge",
            "cases": [
                {
                    "input": "I want a refund",
                    "expected_behavior": ["check order status"],
                    "forbidden_behavior": ["promise approval"],
                }
            ],
        },
    ).json()

    assert exam["score"] == 0.82
    assert exam["passed"] is True
    assert exam["new_status"] == "verified"
    assert fake_client.calls
