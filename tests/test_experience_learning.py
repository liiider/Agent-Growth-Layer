from fastapi.testclient import TestClient

from server.main import app


def test_experience_submission_extracts_candidate_cognition() -> None:
    client = TestClient(app)

    create_response = client.post(
        "/v1/experiences",
        json={
            "agent_id": "support_agent",
            "domain": "customer_support",
            "intent": "refund_question",
            "user_input": "我要退款，为什么不给退？",
            "agent_output": "根据平台规则，订单超过7天不能退款。",
            "tools_used": ["policy_search"],
            "retrieved_context": [
                "退款规则分地区适用，不同地区售后政策不同。"
            ],
            "feedback": "回答错误，必须先确认地区和订单状态。",
            "result_status": "corrected",
            "risk_level": "medium",
            "metadata": {"region": "unknown", "order_status": "unknown"},
        },
    )

    assert create_response.status_code == 200
    created = create_response.json()
    assert created["status"] == "received"
    assert created["extraction_status"] == "queued"

    experience_response = client.get(f"/v1/experiences/{created['experience_id']}")
    assert experience_response.status_code == 200
    experience = experience_response.json()
    assert experience["extraction_status"] == "succeeded"
    assert experience["cognition_ids"]

    cognition_response = client.get(f"/v1/cognitions/{experience['cognition_ids'][0]}")
    assert cognition_response.status_code == 200
    cognition = cognition_response.json()
    assert cognition["status"] == "candidate"
    assert cognition["weight"] == "medium"
    assert cognition["evidence_refs"] == [created["experience_id"]]


def test_manual_extraction_retry_sets_retrying_then_succeeds() -> None:
    client = TestClient(app)

    create_response = client.post(
        "/v1/experiences",
        json={
            "agent_id": "support_agent",
            "domain": "customer_support",
            "intent": "refund_question",
            "user_input": "Refund?",
            "agent_output": "No refund.",
            "feedback": "Ask for order status first.",
            "result_status": "corrected",
            "risk_level": "low",
        },
    )
    experience_id = create_response.json()["experience_id"]

    retry_response = client.post(f"/v1/experiences/{experience_id}/extract")

    assert retry_response.status_code == 200
    assert retry_response.json()["extraction_status"] == "retrying"

    experience = client.get(f"/v1/experiences/{experience_id}").json()
    assert experience["extraction_status"] == "succeeded"
    assert experience["cognition_ids"]
    assert len(experience["cognition_ids"]) == 1


def test_candidate_cognition_enters_next_guidance() -> None:
    client = TestClient(app)

    create_response = client.post(
        "/v1/experiences",
        json={
            "agent_id": "support_agent",
            "domain": "customer_support",
            "intent": "refund_question",
            "user_input": "Why no refund?",
            "agent_output": "No refund after seven days.",
            "feedback": "Must confirm region and order status before applying refund rules.",
            "result_status": "corrected",
            "risk_level": "medium",
        },
    )
    experience_id = create_response.json()["experience_id"]

    guidance_response = client.post(
        "/v1/guidance",
        json={
            "agent_id": "support_agent",
            "domain": "customer_support",
            "intent": "refund_question",
            "context": {"message": "Why was my refund rejected?"},
            "risk_level": "medium",
        },
    )

    assert guidance_response.status_code == 200
    candidate_skills = guidance_response.json()["guidance"]["candidate_skills"]
    assert candidate_skills
    assert candidate_skills[0]["status"] == "candidate"
    assert candidate_skills[0]["weight"] == "medium"
    assert candidate_skills[0]["evidence_refs"] == [experience_id]
