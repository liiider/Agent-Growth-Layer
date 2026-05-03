from typing import Literal

from pydantic import BaseModel, Field


class SeedSkill(BaseModel):
    id: str
    name: str
    version: str
    status: Literal["seed"]
    description: str
    domain: list[str] = Field(default_factory=list)
    intent: list[str] = Field(default_factory=list)
    applies_when: list[str] = Field(default_factory=list)
    instructions: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    negative_examples: list[str] = Field(default_factory=list)
    output_guidance: list[str] = Field(default_factory=list)
    tool_policy: list[str] = Field(default_factory=list)
    risk_level: str = "low"
    tags: list[str] = Field(default_factory=list)
    weight: str = "medium"
