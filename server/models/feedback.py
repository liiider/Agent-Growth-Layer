from typing import Literal

from pydantic import BaseModel, Field

FeedbackType = Literal[
    "user_like",
    "user_dislike",
    "human_corrected",
    "task_success",
    "task_failed",
    "exam_failed",
    "exam_passed",
    "policy_violation",
    "manual_override",
]


class FeedbackCreate(BaseModel):
    experience_id: str = Field(min_length=1)
    feedback_type: FeedbackType
    content: str = Field(min_length=1)
    score: float | None = Field(default=None, ge=0, le=1)


class FeedbackCreateResponse(BaseModel):
    feedback_id: str
    experience_id: str
    feedback_type: FeedbackType
    status: Literal["received"]
