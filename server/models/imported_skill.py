from pydantic import BaseModel, Field


class PromptImportRequest(BaseModel):
    agent_id: str = Field(min_length=1)
    domain: str = Field(min_length=1)
    intent: str = Field(min_length=1)
    prompt: str = Field(min_length=1)


class ImportedSkill(BaseModel):
    id: str
    name: str
    status: str
    agent_id: str
    domain: str
    intent: str
    procedure: list[str]
    constraints: list[str]
    evidence_refs: list[str]
    weight: str = "medium"
    confidence: float = 0.7


class PromptImportResponse(BaseModel):
    skill: ImportedSkill
