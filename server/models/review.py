from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

ReviewObjectType = Literal["experience", "cognition", "skill"]
ReviewDecision = Literal["approve", "reject", "revise", "quarantine"]


class ReviewCreate(BaseModel):
    object_type: ReviewObjectType
    object_id: str = Field(min_length=1)
    decision: ReviewDecision
    reviewer: str = Field(min_length=1)
    notes: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class ReviewResponse(BaseModel):
    review_id: str
    object_type: ReviewObjectType
    object_id: str
    decision: ReviewDecision
    reviewer: str
    notes: str
    new_status: str | None = None
