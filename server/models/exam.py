from typing import Any, Literal

from pydantic import BaseModel, Field


class ExamCase(BaseModel):
    input: str
    context: dict[str, Any] = Field(default_factory=dict)
    expected_behavior: list[str] = Field(default_factory=list)
    forbidden_behavior: list[str] = Field(default_factory=list)


class ExamRequest(BaseModel):
    evaluator: Literal["manual_score", "llm_judge"] = "manual_score"
    score: float | None = Field(default=None, ge=0, le=1)
    cases: list[ExamCase] = Field(default_factory=list)
    require_human_review: bool = False


class ExamResponse(BaseModel):
    exam_id: str
    skill_id: str
    previous_status: str
    score: float
    passed: bool
    failures: list[str]
    new_status: str
