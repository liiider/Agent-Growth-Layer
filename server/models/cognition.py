from typing import Literal

from pydantic import BaseModel, Field

from server.models.experience import RiskLevel

CognitionType = Literal[
    "fact",
    "preference",
    "rule",
    "procedure",
    "constraint",
    "error_pattern",
    "tool_usage",
    "communication_style",
    "decision_pattern",
    "negative_example",
]

CognitionStatus = Literal["candidate", "verified", "deprecated", "quarantined"]
Weight = Literal["low", "medium", "high"]


class CognitionRead(BaseModel):
    id: str
    type: CognitionType
    content: str
    agent_id: str
    domain: str
    intent: str
    confidence: float
    risk_level: RiskLevel
    weight: Weight
    status: CognitionStatus
    evidence_refs: list[str]
    created_at: str
    updated_at: str


class CognitionStatusUpdate(BaseModel):
    status: CognitionStatus


class CognitionCandidate(BaseModel):
    type: CognitionType = "error_pattern"
    content: str = Field(min_length=1)
    confidence: float = Field(ge=0, le=1)
    weight: Weight
