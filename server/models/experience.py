from typing import Any, Literal

from pydantic import BaseModel, Field

RiskLevel = Literal["low", "medium", "high"]
ExtractionStatus = Literal["queued", "retrying", "processing", "succeeded", "failed"]


class ExperienceCreate(BaseModel):
    agent_id: str = Field(min_length=1)
    domain: str = Field(min_length=1)
    intent: str = Field(min_length=1)
    user_input: str = Field(min_length=1)
    agent_output: str = Field(min_length=1)
    tools_used: list[str] = Field(default_factory=list)
    retrieved_context: list[str] = Field(default_factory=list)
    feedback: str | None = None
    result_status: str = "unknown"
    risk_level: RiskLevel = "low"
    metadata: dict[str, Any] = Field(default_factory=dict)


class ExperienceCreateResponse(BaseModel):
    experience_id: str
    status: Literal["received"]
    extraction_status: ExtractionStatus


class ExperienceRead(BaseModel):
    id: str
    agent_id: str
    domain: str
    intent: str
    user_input: str
    agent_output: str
    tools_used: list[str]
    retrieved_context: list[str]
    feedback: str | None
    result_status: str
    risk_level: RiskLevel
    extraction_status: ExtractionStatus
    cognition_ids: list[str]
    metadata: dict[str, Any]
    created_at: str
    updated_at: str


class ExperienceRetryResponse(BaseModel):
    experience_id: str
    extraction_status: ExtractionStatus
