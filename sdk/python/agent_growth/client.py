from typing import Any

import httpx
from agent_growth.audit import AuditClient
from agent_growth.cognitions import CognitionsClient
from agent_growth.experiences import ExperiencesClient
from agent_growth.feedback import FeedbackClient
from agent_growth.guidance import Guidance
from agent_growth.skills import SkillsClient


class AgentGrowthClient:
    def __init__(self, base_url: str = "http://localhost:8000", *, timeout: float = 10) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.experiences = ExperiencesClient(self.base_url, self.timeout)
        self.feedback = FeedbackClient(self.base_url, self.timeout)
        self.cognitions = CognitionsClient(self.base_url, self.timeout)
        self.skills = SkillsClient(self.base_url, self.timeout)
        self.audit = AuditClient(self.base_url, self.timeout)

    def get_guidance(
        self,
        *,
        agent_id: str,
        domain: str,
        intent: str,
        context: dict[str, Any] | None = None,
        risk_level: str = "low",
    ) -> Guidance:
        response = httpx.request(
            "POST",
            f"{self.base_url}/v1/guidance",
            json={
                "agent_id": agent_id,
                "domain": domain,
                "intent": intent,
                "context": context or {},
                "risk_level": risk_level,
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        return Guidance(response.json()["guidance"])
