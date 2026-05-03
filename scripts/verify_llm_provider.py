from __future__ import annotations

import argparse
import sys
import time
from typing import Any

import httpx


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify configured BYOK LLM provider paths.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    verifier = LlmProviderVerifier(args.base_url)
    verifier.run()
    return 0


class LlmProviderVerifier:
    def __init__(
        self,
        base_url: str,
        *,
        poll_interval_seconds: float = 0.5,
        max_wait_seconds: float = 30,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(timeout=45)
        self.poll_interval_seconds = poll_interval_seconds
        self.max_wait_seconds = max_wait_seconds

    def run(self) -> None:
        cognition_id = self.verify_llm_extraction()
        imported_skill_id = self.verify_llm_prompt_import()
        skill_id = self.verify_llm_judge(cognition_id)
        print(
            "LLM provider verification passed: "
            f"cognition={cognition_id}, imported_skill={imported_skill_id}, skill={skill_id}"
        )

    def verify_llm_extraction(self) -> str:
        created = self.post(
            "/v1/experiences",
            {
                "agent_id": "support_agent",
                "domain": "customer_support",
                "intent": "refund_question",
                "user_input": "Why was my refund rejected?",
                "agent_output": "Refunds are never available after seven days.",
                "feedback": (
                    "Correct the behavior: first check order status, region, and policy version "
                    "before answering refund eligibility."
                ),
                "result_status": "corrected",
                "risk_level": "medium",
            },
        )
        experience_id = created["experience_id"]
        experience = self.wait_for_extraction(experience_id)
        assert experience["extraction_status"] == "succeeded"
        assert experience["cognition_ids"]
        cognition_id = experience["cognition_ids"][0]
        cognition = self.get(f"/v1/cognitions/{cognition_id}")
        assert cognition["content"]
        assert 0 <= cognition["confidence"] <= 1
        assert cognition["weight"] in {"low", "medium", "high"}
        print(f"llm extraction: {experience_id} -> {cognition_id}")
        return cognition_id

    def wait_for_extraction(self, experience_id: str) -> dict[str, Any]:
        deadline = time.monotonic() + self.max_wait_seconds
        last_status = "unknown"
        while time.monotonic() <= deadline:
            experience = self.get(f"/v1/experiences/{experience_id}")
            last_status = experience["extraction_status"]
            if last_status == "succeeded":
                return experience
            if last_status == "failed":
                raise AssertionError(f"LLM extraction failed for {experience_id}")
            time.sleep(self.poll_interval_seconds)
        raise AssertionError(
            f"LLM extraction timed out for {experience_id}; last status: {last_status}"
        )

    def verify_llm_prompt_import(self) -> str:
        imported = self.post(
            "/v1/skills/import_prompt",
            {
                "agent_id": "support_agent",
                "domain": "customer_support",
                "intent": "refund_question",
                "prompt": (
                    "Always check order status, region, and policy version before answering. "
                    "Never promise refund approval without confirmed policy evidence."
                ),
            },
        )
        skill = imported["skill"]
        assert skill["id"].startswith("skill_imported_")
        assert skill["status"] == "candidate"
        assert skill["procedure"]
        assert skill["constraints"]
        print(f"llm prompt import: {skill['id']}")
        return skill["id"]

    def verify_llm_judge(self, cognition_id: str) -> str:
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
                "evaluator": "llm_judge",
                "cases": [
                    {
                        "input": "I want a refund but I have not shared my order status.",
                        "context": {"region": "unknown", "order_status": "unknown"},
                        "expected_behavior": [
                            "ask for order status",
                            "check region",
                            "avoid promising refund approval",
                        ],
                        "forbidden_behavior": ["promise refund approval"],
                    }
                ],
            },
        )
        assert 0 <= exam["score"] <= 1
        assert exam["new_status"] in {"verified", "failed"}
        print(f"llm judge: {skill_id} score={exam['score']}")
        return skill_id

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
        print(f"LLM provider verification failed: {exc}", file=sys.stderr)
        raise
