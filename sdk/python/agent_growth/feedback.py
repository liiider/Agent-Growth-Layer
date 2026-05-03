from __future__ import annotations

from typing import Any

from agent_growth.http import HttpResource


class FeedbackClient(HttpResource):
    def create(
        self,
        *,
        experience_id: str,
        feedback_type: str,
        content: str,
        score: float | None = None,
    ) -> dict[str, Any]:
        return self.request(
            "POST",
            "/v1/feedback",
            json={
                "experience_id": experience_id,
                "feedback_type": feedback_type,
                "content": content,
                "score": score,
            },
        )
