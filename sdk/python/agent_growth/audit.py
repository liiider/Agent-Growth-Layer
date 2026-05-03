from __future__ import annotations

from typing import Any

from agent_growth.http import HttpResource


class AuditClient(HttpResource):
    def get(self, object_type: str, object_id: str) -> dict[str, Any]:
        return self.request("GET", f"/v1/audit/{object_type}/{object_id}")
