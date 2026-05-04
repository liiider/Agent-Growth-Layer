from __future__ import annotations

from typing import Any

from agent_growth.http import HttpResource


class ReviewsClient(HttpResource):
    def create(
        self,
        *,
        object_type: str,
        object_id: str,
        decision: str,
        reviewer: str,
        notes: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self.request(
            "POST",
            "/v1/reviews",
            json={
                "object_type": object_type,
                "object_id": object_id,
                "decision": decision,
                "reviewer": reviewer,
                "notes": notes,
                "metadata": metadata or {},
            },
        )
