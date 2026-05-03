from typing import Any

from agent_growth.http import HttpResource


class ExperiencesClient(HttpResource):
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
        return self.request(
            "POST",
            "/v1/experiences",
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
        )

    def get(self, experience_id: str) -> dict[str, Any]:
        return self.request("GET", f"/v1/experiences/{experience_id}")

    def retry_extraction(self, experience_id: str) -> dict[str, Any]:
        return self.request("POST", f"/v1/experiences/{experience_id}/extract")
