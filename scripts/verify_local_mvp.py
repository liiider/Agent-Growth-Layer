from __future__ import annotations

import argparse
import sys
from typing import Any

import httpx


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify Agent Growth Layer local MVP.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    verifier = LocalMvpVerifier(args.base_url)
    verifier.run()
    return 0


class LocalMvpVerifier:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(timeout=20)

    def run(self) -> None:
        self.health()
        self.seed_guidance()
        experience_id, cognition_id = self.experience_learning()
        self.feedback(experience_id)
        imported_skill_id = self.prompt_import()
        skill_id = self.skill_exam(cognition_id)
        self.audit(skill_id, cognition_id)
        self.verified_guidance(skill_id, imported_skill_id)
        print("Local MVP verification passed.")

    def health(self) -> None:
        response = self.client.get(f"{self.base_url}/health")
        response.raise_for_status()
        assert response.json()["status"] == "ok"
        print("health: ok")

    def seed_guidance(self) -> None:
        guidance = self.post(
            "/v1/guidance",
            {
                "agent_id": "support_agent",
                "domain": "customer_support",
                "intent": "refund_question",
                "context": {"message": "Why was my refund rejected?"},
                "risk_level": "medium",
            },
        )
        assert guidance["guidance"]["seed_skills"]
        print(f"seed guidance: {len(guidance['guidance']['seed_skills'])} seed skills")

    def experience_learning(self) -> tuple[str, str]:
        created = self.post(
            "/v1/experiences",
            {
                "agent_id": "support_agent",
                "domain": "customer_support",
                "intent": "refund_question",
                "user_input": "Why was my refund rejected?",
                "agent_output": "Refunds are not available after seven days.",
                "feedback": "Must confirm region and order status before applying refund rules.",
                "result_status": "corrected",
                "risk_level": "medium",
            },
        )
        experience_id = created["experience_id"]
        experience = self.get(f"/v1/experiences/{experience_id}")
        assert experience["extraction_status"] == "succeeded"
        assert experience["cognition_ids"]
        cognition_id = experience["cognition_ids"][0]
        cognition = self.get(f"/v1/cognitions/{cognition_id}")
        assert cognition["status"] == "candidate"
        assert cognition["evidence_refs"] == [experience_id]
        print(f"experience learning: {experience_id} -> {cognition_id}")
        return experience_id, cognition_id

    def feedback(self, experience_id: str) -> None:
        feedback = self.post(
            "/v1/feedback",
            {
                "experience_id": experience_id,
                "feedback_type": "human_corrected",
                "content": "Also check region-specific policy.",
                "score": 0.2,
            },
        )
        assert feedback["feedback_id"].startswith("fb_")
        print(f"feedback: {feedback['feedback_id']}")

    def prompt_import(self) -> str:
        imported = self.post(
            "/v1/skills/import_prompt",
            {
                "agent_id": "support_agent",
                "domain": "customer_support",
                "intent": "refund_question",
                "prompt": (
                    "Always check order status before answering refund questions. "
                    "Never promise refund approval."
                ),
            },
        )
        skill = imported["skill"]
        assert skill["id"].startswith("skill_imported_")
        assert skill["status"] == "candidate"
        print(f"prompt import: {skill['id']}")
        return skill["id"]

    def skill_exam(self, cognition_id: str) -> str:
        built = self.post(
            "/v1/skills/build",
            {
                "agent_id": "support_agent",
                "domain": "customer_support",
                "intent": "refund_question",
                "name": "Refund Policy Handling",
                "cognition_ids": [cognition_id],
            },
        )
        skill_id = built["skill"]["id"]
        exam = self.post(
            f"/v1/skills/{skill_id}/exam",
            {
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
        assert exam["passed"] is True
        assert exam["new_status"] == "verified"
        print(f"skill exam: {skill_id} -> verified")
        return skill_id

    def audit(self, skill_id: str, cognition_id: str) -> None:
        audit = self.get(f"/v1/audit/skill/{skill_id}")
        assert cognition_id in audit["evidence_refs"]
        assert audit["sources"]["cognitions"]
        print(f"audit: {skill_id}")

    def verified_guidance(self, skill_id: str, imported_skill_id: str) -> None:
        guidance = self.post(
            "/v1/guidance",
            {
                "agent_id": "support_agent",
                "domain": "customer_support",
                "intent": "refund_question",
                "context": {"message": "Why was my refund rejected?"},
                "risk_level": "medium",
            },
        )
        verified_ids = {
            skill["id"] for skill in guidance["guidance"]["verified_skills"]
        }
        candidate_ids = {
            skill["id"] for skill in guidance["guidance"]["candidate_skills"]
        }
        assert skill_id in verified_ids
        assert imported_skill_id in candidate_ids
        print("verified guidance: ok")

    def get(self, path: str) -> dict[str, Any]:
        response = self.client.get(f"{self.base_url}{path}")
        response.raise_for_status()
        return response.json()

    def post(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        response = self.client.post(f"{self.base_url}{path}", json=body)
        response.raise_for_status()
        return response.json()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Local MVP verification failed: {exc}", file=sys.stderr)
        raise
