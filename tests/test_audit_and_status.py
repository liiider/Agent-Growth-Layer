from fastapi.testclient import TestClient

from server.main import app


def test_audit_returns_skill_evidence_chain() -> None:
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
    skill_id = client.post(
        "/v1/skills/build",
        json={
            "agent_id": "support_agent",
            "domain": "customer_support",
            "intent": "refund_question",
            "name": "Refund Policy Handling",
            "cognition_ids": [cognition_id],
        },
    ).json()["skill"]["id"]

    response = client.get(f"/v1/audit/skill/{skill_id}")

    assert response.status_code == 200
    audit = response.json()
    assert audit["object_type"] == "skill"
    assert audit["object_id"] == skill_id
    assert cognition_id in audit["evidence_refs"]
    assert audit["sources"]["cognitions"][0]["id"] == cognition_id


def test_quarantined_skill_does_not_enter_guidance() -> None:
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
    skill_id = client.post(
        "/v1/skills/build",
        json={
            "agent_id": "support_agent",
            "domain": "customer_support",
            "intent": "refund_question",
            "name": "Refund Policy Handling",
            "cognition_ids": [cognition_id],
        },
    ).json()["skill"]["id"]
    client.patch(f"/v1/skills/{skill_id}/status", json={"status": "quarantined"})

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

    verified_ids = {
        skill["id"] for skill in guidance["guidance"]["verified_skills"]
    }
    candidate_ids = {
        skill["id"] for skill in guidance["guidance"]["candidate_skills"]
    }
    assert skill_id not in verified_ids
    assert skill_id not in candidate_ids
