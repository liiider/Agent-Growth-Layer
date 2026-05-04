from __future__ import annotations

import argparse
import sys
import time
from typing import Any

import httpx


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify MVP behavior in a project scenario.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    verifier = ProjectMvpVerifier(args.base_url)
    verifier.run()
    return 0


class ProjectMvpVerifier:
    def __init__(
        self,
        base_url: str,
        *,
        poll_interval_seconds: float = 0.2,
        max_wait_seconds: float = 10,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(timeout=30)
        self.poll_interval_seconds = poll_interval_seconds
        self.max_wait_seconds = max_wait_seconds

    def run(self) -> None:
        self.health()
        initial_seed_count = self.initial_guidance()
        experience_id, cognition_id = self.capture_project_experience()
        self.review_experience(experience_id)
        self.review_cognition(cognition_id)
        skill_id = self.build_skill(cognition_id)
        self.exam_requires_human_review(skill_id)
        self.approve_skill(skill_id)
        self.verified_guidance(skill_id)
        print(
            "Project MVP verification passed: "
            f"initial_seed_skills={initial_seed_count}, experience={experience_id}, "
            f"cognition={cognition_id}, verified_skill={skill_id}"
        )

    def health(self) -> None:
        response = self.client.get(f"{self.base_url}/health")
        response.raise_for_status()
        assert response.json()["status"] == "ok"

    def initial_guidance(self) -> int:
        guidance = self.post(
            "/v1/guidance",
            {
                "agent_id": "coding_agent",
                "domain": "coding",
                "intent": "implementation_task",
                "context": {
                    "project": "Agent Growth Layer",
                    "task": "Implement a reviewed code change with tests and handoff.",
                },
                "risk_level": "medium",
            },
        )
        seed_skills = guidance["guidance"]["seed_skills"]
        assert seed_skills
        print(f"project initial guidance: {len(seed_skills)} seed skills")
        return len(seed_skills)

    def capture_project_experience(self) -> tuple[str, str]:
        created = self.post(
            "/v1/experiences",
            {
                "agent_id": "coding_agent",
                "domain": "coding",
                "intent": "implementation_task",
                "user_input": "Add a project workflow change.",
                "agent_output": (
                    "The change was implemented, but the first pass missed a clear "
                    "handoff note and did not explicitly report validation commands."
                ),
                "tools_used": ["pytest", "ruff", "compileall"],
                "retrieved_context": [
                    "AGENTS.md requires tests, verification, and stage handoff files.",
                    "Generated artifacts must be moved to D:\\temp instead of deleted.",
                ],
                "feedback": (
                    "For every code stage, explicitly run verification, document failures, "
                    "move generated artifacts to D:\\temp, and write a handoff before closing."
                ),
                "result_status": "corrected",
                "risk_level": "medium",
                "metadata": {
                    "project": "Agent Growth Layer",
                    "value_signal": "prevents repeated missed verification and handoff work",
                },
            },
        )
        experience_id = created["experience_id"]
        experience = self.wait_for_extraction(experience_id)
        cognition_id = experience["cognition_ids"][0]
        print(f"project experience: {experience_id} -> {cognition_id}")
        return experience_id, cognition_id

    def wait_for_extraction(self, experience_id: str) -> dict[str, Any]:
        deadline = time.monotonic() + self.max_wait_seconds
        last_status = "unknown"
        while time.monotonic() <= deadline:
            experience = self.get(f"/v1/experiences/{experience_id}")
            last_status = experience["extraction_status"]
            if last_status == "succeeded":
                assert experience["cognition_ids"]
                return experience
            if last_status == "failed":
                raise AssertionError(f"Project extraction failed for {experience_id}")
            time.sleep(self.poll_interval_seconds)
        raise AssertionError(
            f"Project extraction timed out for {experience_id}; last status: {last_status}"
        )

    def review_experience(self, experience_id: str) -> None:
        review = self.post(
            "/v1/reviews",
            {
                "object_type": "experience",
                "object_id": experience_id,
                "decision": "approve",
                "reviewer": "project_owner",
                "notes": "This experience captures a repeatable project quality rule.",
            },
        )
        assert review["review_id"].startswith("rev_")
        assert review["new_status"] is None
        print(f"project experience review: {review['review_id']}")

    def review_cognition(self, cognition_id: str) -> None:
        review = self.post(
            "/v1/reviews",
            {
                "object_type": "cognition",
                "object_id": cognition_id,
                "decision": "approve",
                "reviewer": "project_owner",
                "notes": "The extracted cognition is safe and generalizable for this project.",
            },
        )
        assert review["new_status"] == "verified"
        print(f"project cognition review: {cognition_id} -> verified")

    def build_skill(self, cognition_id: str) -> str:
        built = self.post(
            "/v1/skills/build",
            {
                "agent_id": "coding_agent",
                "domain": "coding",
                "intent": "implementation_task",
                "name": "Project Verification Handoff Discipline",
                "cognition_ids": [cognition_id],
            },
        )
        skill_id = built["skill"]["id"]
        assert built["skill"]["status"] == "candidate"
        print(f"project skill build: {skill_id}")
        return skill_id

    def exam_requires_human_review(self, skill_id: str) -> None:
        exam = self.post(
            f"/v1/skills/{skill_id}/exam",
            {
                "evaluator": "manual_score",
                "score": 0.9,
                "require_human_review": True,
                "cases": [
                    {
                        "input": "Finish a code stage in Agent Growth Layer.",
                        "context": {"risk": "medium", "generated_artifacts": True},
                        "expected_behavior": [
                            "run tests and lint",
                            "move generated artifacts to D:\\temp",
                            "write a handoff file",
                        ],
                        "forbidden_behavior": [
                            "claim completion without validation",
                            "delete generated artifacts",
                        ],
                    }
                ],
            },
        )
        assert exam["passed"] is True
        assert exam["new_status"] == "needs_review"
        print(f"project exam: {skill_id} -> needs_review")

    def approve_skill(self, skill_id: str) -> None:
        review = self.post(
            "/v1/reviews",
            {
                "object_type": "skill",
                "object_id": skill_id,
                "decision": "approve",
                "reviewer": "project_owner",
                "notes": "Passing exam and project owner review approve this skill.",
            },
        )
        assert review["new_status"] == "verified"
        print(f"project skill review: {skill_id} -> verified")

    def verified_guidance(self, skill_id: str) -> None:
        guidance = self.post(
            "/v1/guidance",
            {
                "agent_id": "coding_agent",
                "domain": "coding",
                "intent": "implementation_task",
                "context": {
                    "project": "Agent Growth Layer",
                    "task": "Run the next implementation stage.",
                },
                "risk_level": "medium",
            },
        )
        verified_ids = {
            skill["id"] for skill in guidance["guidance"]["verified_skills"]
        }
        assert skill_id in verified_ids
        print("project verified guidance: ok")

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
        print(f"Project MVP verification failed: {exc}", file=sys.stderr)
        raise
