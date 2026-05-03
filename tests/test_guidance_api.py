from fastapi.testclient import TestClient

from server.main import app


def test_guidance_returns_seed_skills_for_cold_start() -> None:
    client = TestClient(app)

    response = client.post(
        "/v1/guidance",
        json={
            "agent_id": "support_agent",
            "domain": "customer_support",
            "intent": "refund_question",
            "context": {"message": "我要退款，为什么不给退？"},
            "risk_level": "medium",
        },
    )

    assert response.status_code == 200
    body = response.json()

    assert body["agent_id"] == "support_agent"
    assert body["domain"] == "customer_support"
    assert body["intent"] == "refund_question"
    assert body["guidance"]["verified_skills"] == []
    assert body["guidance"]["candidate_skills"] == []
    assert body["guidance"]["seed_skills"]
    assert body["guidance"]["seed_skills"][0]["status"] == "seed"


def test_guidance_filters_seed_skills_by_domain() -> None:
    client = TestClient(app)

    response = client.post(
        "/v1/guidance",
        json={
            "agent_id": "support_agent",
            "domain": "customer_support",
            "intent": "refund_question",
            "context": {"message": "Why was my refund rejected?"},
            "risk_level": "medium",
        },
    )

    assert response.status_code == 200
    seed_skill_ids = {
        skill["id"] for skill in response.json()["guidance"]["seed_skills"]
    }

    assert "seed_customer_support_resolution" in seed_skill_ids
    assert "seed_code_change_checklist" not in seed_skill_ids
    assert "seed_medical_safety_boundary" not in seed_skill_ids


def test_seed_skill_lookup() -> None:
    client = TestClient(app)

    response = client.get("/v1/seed-skills/seed_uncertainty_handling")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == "seed_uncertainty_handling"
    assert body["status"] == "seed"
    assert "instructions" in body
