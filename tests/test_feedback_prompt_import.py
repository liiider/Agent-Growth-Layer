from fastapi.testclient import TestClient

from server.main import app


def test_feedback_can_be_submitted_for_experience() -> None:
    client = TestClient(app)
    experience_id = client.post(
        "/v1/experiences",
        json={
            "agent_id": "support_agent",
            "domain": "customer_support",
            "intent": "refund_question",
            "user_input": "Refund?",
            "agent_output": "No refund.",
            "feedback": "Ask for order status first.",
            "result_status": "corrected",
            "risk_level": "medium",
        },
    ).json()["experience_id"]

    response = client.post(
        "/v1/feedback",
        json={
            "experience_id": experience_id,
            "feedback_type": "human_corrected",
            "content": "Also check region-specific policy.",
            "score": 0.2,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["feedback_id"].startswith("fb_")
    assert body["experience_id"] == experience_id
    assert body["feedback_type"] == "human_corrected"


def test_prompt_import_returns_skill_and_enters_guidance() -> None:
    client = TestClient(app)

    response = client.post(
        "/v1/skills/import_prompt",
        json={
            "agent_id": "support_agent",
            "domain": "customer_support",
            "intent": "refund_question",
            "prompt": (
                "Always check order status before answering refund questions. "
                "Never promise refund approval."
            ),
        },
    )

    assert response.status_code == 200
    skill = response.json()["skill"]
    assert skill["id"].startswith("skill_imported_")
    assert skill["status"] == "candidate"
    assert skill["evidence_refs"][0].startswith("prompt_import_")
    assert "Check order status" in skill["procedure"][0]
    assert "Never promise refund approval" in skill["constraints"][0]

    guidance = client.post(
        "/v1/guidance",
        json={
            "agent_id": "support_agent",
            "domain": "customer_support",
            "intent": "refund_question",
            "context": {"message": "Why was my refund rejected?"},
            "risk_level": "medium",
        },
    ).json()

    candidate_ids = {
        candidate["id"] for candidate in guidance["guidance"]["candidate_skills"]
    }
    assert skill["id"] in candidate_ids
