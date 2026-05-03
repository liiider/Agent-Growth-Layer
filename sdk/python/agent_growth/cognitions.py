from __future__ import annotations

from typing import Any

from agent_growth.http import HttpResource


class CognitionsClient(HttpResource):
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
            "/v1/cognitions",
            params={
                "agent_id": agent_id,
                "domain": domain,
                "intent": intent,
                "status": status,
                "limit": limit,
            },
        )

    def get(self, cognition_id: str) -> dict[str, Any]:
        return self.request("GET", f"/v1/cognitions/{cognition_id}")

    def update_status(self, cognition_id: str, status: str) -> dict[str, Any]:
        return self.request(
            "PATCH",
            f"/v1/cognitions/{cognition_id}/status",
            json={"status": status},
        )
