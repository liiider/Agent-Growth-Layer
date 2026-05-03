from typing import Any

from pydantic import BaseModel, Field


class AuditResponse(BaseModel):
    object_type: str
    object_id: str
    evidence_refs: list[str] = Field(default_factory=list)
    sources: dict[str, list[dict[str, Any]]] = Field(default_factory=dict)
