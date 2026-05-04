from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from server.config import Settings, get_settings
from server.models.review import ReviewCreate, ReviewResponse
from server.storage.repositories import (
    CognitionRepository,
    ExperienceRepository,
    ReviewRepository,
    SkillRepository,
)

router = APIRouter(prefix="/v1/reviews", tags=["reviews"])


def get_experience_repository(
    settings: Annotated[Settings, Depends(get_settings)],
) -> ExperienceRepository:
    return ExperienceRepository(settings.database_url)


def get_cognition_repository(
    settings: Annotated[Settings, Depends(get_settings)],
) -> CognitionRepository:
    return CognitionRepository(settings.database_url)


def get_skill_repository(
    settings: Annotated[Settings, Depends(get_settings)],
) -> SkillRepository:
    return SkillRepository(settings.database_url)


def get_review_repository(
    settings: Annotated[Settings, Depends(get_settings)],
) -> ReviewRepository:
    return ReviewRepository(settings.database_url)


@router.post("", response_model=ReviewResponse)
def create_review(
    request: ReviewCreate,
    experience_repository: Annotated[ExperienceRepository, Depends(get_experience_repository)],
    cognition_repository: Annotated[CognitionRepository, Depends(get_cognition_repository)],
    skill_repository: Annotated[SkillRepository, Depends(get_skill_repository)],
    review_repository: Annotated[ReviewRepository, Depends(get_review_repository)],
) -> ReviewResponse:
    new_status = _apply_review_decision(
        request,
        experience_repository=experience_repository,
        cognition_repository=cognition_repository,
        skill_repository=skill_repository,
    )
    review_id = review_repository.create(request)
    return ReviewResponse(
        review_id=review_id,
        object_type=request.object_type,
        object_id=request.object_id,
        decision=request.decision,
        reviewer=request.reviewer,
        notes=request.notes,
        new_status=new_status,
    )


def _apply_review_decision(
    request: ReviewCreate,
    *,
    experience_repository: ExperienceRepository,
    cognition_repository: CognitionRepository,
    skill_repository: SkillRepository,
) -> str | None:
    if request.object_type == "experience":
        if experience_repository.get(request.object_id) is None:
            raise HTTPException(status_code=404, detail="Experience not found.")
        return None

    if request.object_type == "cognition":
        cognition = cognition_repository.get(request.object_id)
        if cognition is None:
            raise HTTPException(status_code=404, detail="Cognition not found.")
        status = _status_for_cognition_review(request.decision, cognition.status)
        if status == cognition.status:
            return status
        updated = cognition_repository.update_status(request.object_id, status)
        return updated.status if updated else None

    skill = skill_repository.get(request.object_id)
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill not found.")
    status = _status_for_skill_review(request, skill)
    if status == skill.status:
        return status
    updated = skill_repository.update_status(request.object_id, status)
    return updated.status if updated else None


def _status_for_cognition_review(decision: str, current_status: str) -> str:
    if decision == "approve":
        return "verified"
    if decision == "reject":
        return "deprecated"
    if decision == "quarantine":
        return "quarantined"
    return current_status


def _status_for_skill_review(request: ReviewCreate, skill) -> str:
    if request.decision == "quarantine":
        return "quarantined"
    if request.decision == "reject":
        return "failed"
    if request.decision == "revise":
        return skill.status
    if not skill.latest_exam or not skill.latest_exam.passed:
        raise HTTPException(
            status_code=409,
            detail="Skill approval requires a passing exam.",
        )
    return "verified"
