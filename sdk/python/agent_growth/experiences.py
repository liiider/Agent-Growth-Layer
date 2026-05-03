from typing import Any

import httpx


class ExperiencesClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    def create(
        self,
        *,
        agent_id: str,
        domain: str,
        intent: str,
        user_input: str,
        agent_output: str,
        tools_used: list[str] | None = None,
        retrieved_context: list[str] | None = None,
        feedback: str | None = None,
        result_status: str = "unknown",
        risk_level: str = "low",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        response = httpx.post(
            f"{self.base_url}/v1/experiences",
            json={
                "agent_id": agent_id,
                "domain": domain,
                "intent": intent,
                "user_input": user_input,
                "agent_output": agent_output,
                "tools_used": tools_used or [],
                "retrieved_context": retrieved_context or [],
                "feedback": feedback,
                "result_status": result_status,
                "risk_level": risk_level,
                "metadata": metadata or {},
            },
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
