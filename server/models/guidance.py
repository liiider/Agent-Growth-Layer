from typing import Any, Literal

from pydantic import BaseModel, Field

from server.models.seed_skill import SeedSkill


class GuidanceRequest(BaseModel):
    agent_id: str = Field(min_length=1)
    domain: str = Field(min_length=1)
    intent: str = Field(min_length=1)
    context: dict[str, Any] = Field(default_factory=dict)
    risk_level: Literal["low", "medium", "high"] = "low"


class GuidancePayload(BaseModel):
    verified_skills: list[dict[str, Any]] = Field(default_factory=list)
    candidate_skills: list[dict[str, Any]] = Field(default_factory=list)
    seed_skills: list[SeedSkill] = Field(default_factory=list)
    error_patterns: list[str] = Field(default_factory=list)
    output_guidance: list[str] = Field(default_factory=list)
    tool_policy: list[str] = Field(default_factory=list)


class GuidanceResponse(BaseModel):
    id: str
    agent_id: str
    domain: str
    intent: str
    guidance: GuidancePayload
