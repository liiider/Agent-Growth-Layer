from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from server.config import Settings, get_settings
from server.models.audit import AuditResponse
from server.storage.repositories import CognitionRepository, SkillRepository

router = APIRouter(prefix="/v1/audit", tags=["audit"])


def get_cognition_repository(
    settings: Annotated[Settings, Depends(get_settings)],
) -> CognitionRepository:
    return CognitionRepository(settings.database_url)


def get_skill_repository(
    settings: Annotated[Settings, Depends(get_settings)],
) -> SkillRepository:
    return SkillRepository(settings.database_url)


@router.get("/{object_type}/{object_id}", response_model=AuditResponse)
def get_audit(
    object_type: str,
    object_id: str,
    cognition_repository: Annotated[CognitionRepository, Depends(get_cognition_repository)],
    skill_repository: Annotated[SkillRepository, Depends(get_skill_repository)],
) -> AuditResponse:
    if object_type == "skill":
        skill = skill_repository.get(object_id)
        if skill is None:
            raise HTTPException(status_code=404, detail="Skill not found.")
        cognitions = [
            cognition.model_dump()
            for cognition_id in skill.evidence_refs
            if (cognition := cognition_repository.get(cognition_id)) is not None
        ]
        return AuditResponse(
            object_type=object_type,
            object_id=object_id,
            evidence_refs=skill.evidence_refs,
            sources={"cognitions": cognitions},
        )

    if object_type == "cognition":
        cognition = cognition_repository.get(object_id)
        if cognition is None:
            raise HTTPException(status_code=404, detail="Cognition not found.")
        return AuditResponse(
            object_type=object_type,
            object_id=object_id,
            evidence_refs=cognition.evidence_refs,
            sources={"experiences": [{"id": ref} for ref in cognition.evidence_refs]},
        )

    raise HTTPException(status_code=404, detail="Unsupported audit object type.")
