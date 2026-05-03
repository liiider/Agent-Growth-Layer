from fastapi.testclient import TestClient

from server.main import app


def _create_candidate_cognition(client: TestClient) -> str:
    experience_id = client.post(
        "/v1/experiences",
        json={
            "agent_id": "support_agent",
            "domain": "customer_support",
            "intent": "refund_question",
            "user_input": "Why no refund?",
            "agent_output": "No refund after seven days.",
            "feedback": "Check region and order status before applying refund rules.",
            "result_status": "corrected",
            "risk_level": "medium",
        },
    ).json()["experience_id"]
    experience = client.get(f"/v1/experiences/{experience_id}").json()
    return experience["cognition_ids"][0]


def test_build_skill_from_cognition() -> None:
    client = TestClient(app)
    cognition_id = _create_candidate_cognition(client)

    response = client.post(
        "/v1/skills/build",
        json={
            "agent_id": "support_agent",
            "domain": "customer_support",
            "intent": "refund_question",
            "name": "Refund Policy Handling",
            "cognition_ids": [cognition_id],
        },
    )

    assert response.status_code == 200
    skill = response.json()["skill"]
    assert skill["id"].startswith("skill_")
    assert skill["status"] == "candidate"
    assert skill["weight"] == "medium"
    assert skill["evidence_refs"] == [cognition_id]
    assert skill["latest_exam"] is None


def test_exam_promotes_skill_to_verified_and_guidance() -> None:
    client = TestClient(app)
    cognition_id = _create_candidate_cognition(client)
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

    exam_response = client.post(
        f"/v1/skills/{skill['id']}/exam",
        json={
            "evaluator": "manual_score",
            "score": 0.9,
            "cases": [
                {
                    "input": "I want a refund",
                    "context": {"region": "unknown", "order_status": "unknown"},
                    "expected_behavior": ["check region", "check order status"],
                    "forbidden_behavior": ["promise refund approval"],
                }
            ],
        },
    )

    assert exam_response.status_code == 200
    exam = exam_response.json()
    assert exam["passed"] is True
    assert exam["new_status"] == "verified"

    fetched = client.get(f"/v1/skills/{skill['id']}").json()
    assert fetched["status"] == "verified"
    assert fetched["latest_exam"]["score"] == 0.9

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
        verified["id"] for verified in guidance["guidance"]["verified_skills"]
    }
    assert skill["id"] in verified_ids


def test_failed_exam_sets_skill_failed() -> None:
    client = TestClient(app)
    cognition_id = _create_candidate_cognition(client)
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

    exam = client.post(
        f"/v1/skills/{skill['id']}/exam",
        json={"evaluator": "manual_score", "score": 0.4, "cases": []},
    ).json()

    assert exam["passed"] is False
    assert exam["new_status"] == "failed"
