from typing import Any, Literal

from pydantic import BaseModel, Field

SkillStatus = Literal[
    "seed",
    "candidate",
    "testing",
    "verified",
    "failed",
    "deprecated",
    "quarantined",
]


class SkillBuildRequest(BaseModel):
    agent_id: str = Field(min_length=1)
    domain: str = Field(min_length=1)
    intent: str = Field(min_length=1)
    name: str = Field(min_length=1)
    cognition_ids: list[str] = Field(min_length=1)


class LatestExam(BaseModel):
    exam_id: str
    evaluator: str
    score: float
    passed: bool
    status_before: str
    status_after: str
    failures: list[str]
    created_at: str


class SkillRead(BaseModel):
    id: str
    agent_id: str
    name: str
    domain: str
    intent: str
    status: SkillStatus
    weight: str
    confidence: float
    version: str
    procedure: list[str]
    constraints: list[str]
    error_patterns: list[str]
    negative_examples: list[str]
    tool_policy: list[str]
    output_guidance: list[str]
    evidence_refs: list[str]
    exam_score: float | None
    latest_exam: LatestExam | None
    created_at: str
    updated_at: str


class SkillBuildResponse(BaseModel):
    skill: SkillRead


class SkillUpdateRequest(BaseModel):
    name: str | None = None
    procedure: list[str] | None = None
    constraints: list[str] | None = None
    output_guidance: list[str] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class SkillStatusUpdate(BaseModel):
    status: SkillStatus
