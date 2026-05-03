from __future__ import annotations

from typing import Any

from agent_growth.http import HttpResource


class SkillsClient(HttpResource):
    def import_prompt(
        self,
        *,
        agent_id: str,
        domain: str,
        intent: str,
        prompt: str,
    ) -> dict[str, Any]:
        return self.request(
            "POST",
            "/v1/skills/import_prompt",
            json={
                "agent_id": agent_id,
                "domain": domain,
                "intent": intent,
                "prompt": prompt,
            },
        )

    def build(
        self,
        *,
        agent_id: str,
        domain: str,
        intent: str,
        name: str,
        cognition_ids: list[str],
    ) -> dict[str, Any]:
        return self.request(
            "POST",
            "/v1/skills/build",
            json={
                "agent_id": agent_id,
                "domain": domain,
                "intent": intent,
                "name": name,
                "cognition_ids": cognition_ids,
            },
        )

    def list(
        self,
        *,
        agent_id: str | None = None,
        domain: str | None = None,
        intent: str | None = None,
        status: str | None = None,
        limit: int = 50,
    ) -> dict[str, Any]:
        return self.request(
            "GET",
            "/v1/skills",
            params={
                "agent_id": agent_id,
                "domain": domain,
                "intent": intent,
                "status": status,
                "limit": limit,
            },
        )

    def get(self, skill_id: str) -> dict[str, Any]:
        return self.request("GET", f"/v1/skills/{skill_id}")

    def update(
        self,
        skill_id: str,
        *,
        name: str | None = None,
        procedure: list[str] | None = None,
        constraints: list[str] | None = None,
        error_patterns: list[str] | None = None,
        negative_examples: list[str] | None = None,
        evidence_refs: list[str] | None = None,
        confidence: float | None = None,
        weight: str | None = None,
    ) -> dict[str, Any]:
        payload = {
            key: value
            for key, value in {
                "name": name,
                "procedure": procedure,
                "constraints": constraints,
                "error_patterns": error_patterns,
                "negative_examples": negative_examples,
                "evidence_refs": evidence_refs,
                "confidence": confidence,
                "weight": weight,
            }.items()
            if value is not None
        }
        return self.request("PATCH", f"/v1/skills/{skill_id}", json=payload)

    def update_status(self, skill_id: str, status: str) -> dict[str, Any]:
        return self.request(
            "PATCH",
            f"/v1/skills/{skill_id}/status",
            json={"status": status},
        )

    def run_exam(
        self,
        skill_id: str,
        *,
        evaluator: str = "manual_score",
        score: float | None = None,
        cases: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        return self.request(
            "POST",
            f"/v1/skills/{skill_id}/exam",
            json={
                "evaluator": evaluator,
                "score": score,
                "cases": cases or [],
            },
        )
