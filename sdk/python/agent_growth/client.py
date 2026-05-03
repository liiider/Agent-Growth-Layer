from typing import Any

import httpx

from sdk.python.agent_growth.guidance import Guidance


class AgentGrowthClient:
    def __init__(self, base_url: str = "http://localhost:8000") -> None:
        self.base_url = base_url.rstrip("/")

    def get_guidance(
        self,
        *,
        agent_id: str,
        domain: str,
        intent: str,
        context: dict[str, Any] | None = None,
        risk_level: str = "low",
    ) -> Guidance:
        response = httpx.post(
            f"{self.base_url}/v1/guidance",
            json={
                "agent_id": agent_id,
                "domain": domain,
                "intent": intent,
                "context": context or {},
                "risk_level": risk_level,
            },
            timeout=10,
        )
        response.raise_for_status()
        return Guidance(response.json()["guidance"])
