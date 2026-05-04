from fastapi.testclient import TestClient

from server.main import app


def _create_cognition(client: TestClient) -> str:
    experience_id = client.post(
        "/v1/experiences",
        json={
            "agent_id": "coding_agent",
            "domain": "coding",
            "intent": "implementation_task",
            "user_input": "Implement a feature.",
            "agent_output": "Changed code but skipped verification notes.",
            "feedback": "Always run tests and write a handoff before closing the task.",
            "result_status": "corrected",
            "risk_level": "medium",
        },
    ).json()["experience_id"]
    return client.get(f"/v1/experiences/{experience_id}").json()["cognition_ids"][0]


def _build_skill(client: TestClient, cognition_id: str) -> str:
    return client.post(
        "/v1/skills/build",
        json={
            "agent_id": "coding_agent",
            "domain": "coding",
            "intent": "implementation_task",
            "name": "Verification Handoff Discipline",
            "cognition_ids": [cognition_id],
        },
    ).json()["skill"]["id"]


def test_review_can_approve_cognition() -> None:
    client = TestClient(app)
    cognition_id = _create_cognition(client)

    response = client.post(
        "/v1/reviews",
        json={
            "object_type": "cognition",
            "object_id": cognition_id,
            "decision": "approve",
            "reviewer": "human_reviewer",
            "notes": "Generalizable project behavior.",
        },
    )

    assert response.status_code == 200
    review = response.json()
    assert review["review_id"].startswith("rev_")
    assert review["new_status"] == "verified"
    cognition = client.get(f"/v1/cognitions/{cognition_id}").json()
    assert cognition["status"] == "verified"


def test_exam_can_require_human_review_before_verification() -> None:
    client = TestClient(app)
    cognition_id = _create_cognition(client)
    skill_id = _build_skill(client, cognition_id)

    exam = client.post(
        f"/v1/skills/{skill_id}/exam",
        json={
            "evaluator": "manual_score",
            "score": 0.9,
            "require_human_review": True,
            "cases": [
                {
                    "input": "Implement a code change",
                    "expected_behavior": ["run tests", "write handoff"],
                    "forbidden_behavior": ["skip verification"],
                }
            ],
        },
    ).json()

    assert exam["passed"] is True
    assert exam["new_status"] == "needs_review"
    skill = client.get(f"/v1/skills/{skill_id}").json()
    assert skill["status"] == "needs_review"

    review = client.post(
        "/v1/reviews",
        json={
            "object_type": "skill",
            "object_id": skill_id,
            "decision": "approve",
            "reviewer": "human_reviewer",
            "notes": "Exam passed and behavior is safe for this project.",
        },
    ).json()

    assert review["new_status"] == "verified"
    skill = client.get(f"/v1/skills/{skill_id}").json()
    assert skill["status"] == "verified"


def test_review_blocks_skill_approval_without_passing_exam() -> None:
    client = TestClient(app)
    cognition_id = _create_cognition(client)
    skill_id = _build_skill(client, cognition_id)

    response = client.post(
        "/v1/reviews",
        json={
            "object_type": "skill",
            "object_id": skill_id,
            "decision": "approve",
            "reviewer": "human_reviewer",
            "notes": "Should not approve without exam.",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Skill approval requires a passing exam."


def test_review_can_record_experience_review_without_status_change() -> None:
    client = TestClient(app)
    experience_id = client.post(
        "/v1/experiences",
        json={
            "agent_id": "coding_agent",
            "domain": "coding",
            "intent": "implementation_task",
            "user_input": "Implement a feature.",
            "agent_output": "Changed code and passed tests.",
            "feedback": "This is useful learning evidence.",
            "result_status": "succeeded",
            "risk_level": "low",
        },
    ).json()["experience_id"]

    review = client.post(
        "/v1/reviews",
        json={
            "object_type": "experience",
            "object_id": experience_id,
            "decision": "approve",
            "reviewer": "human_reviewer",
            "notes": "Useful for learning.",
        },
    ).json()

    assert review["new_status"] is None
    assert review["review_id"].startswith("rev_")
