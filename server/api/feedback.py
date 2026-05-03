from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from server.config import Settings, get_settings
from server.models.feedback import FeedbackCreate, FeedbackCreateResponse
from server.storage.repositories import ExperienceRepository, FeedbackRepository

router = APIRouter(prefix="/v1/feedback", tags=["feedback"])


def get_feedback_repository(
    settings: Annotated[Settings, Depends(get_settings)],
) -> FeedbackRepository:
    return FeedbackRepository(settings.database_url)


def get_experience_repository(
    settings: Annotated[Settings, Depends(get_settings)],
) -> ExperienceRepository:
    return ExperienceRepository(settings.database_url)


@router.post("", response_model=FeedbackCreateResponse)
def create_feedback(
    request: FeedbackCreate,
    feedback_repository: Annotated[FeedbackRepository, Depends(get_feedback_repository)],
    experience_repository: Annotated[ExperienceRepository, Depends(get_experience_repository)],
) -> FeedbackCreateResponse:
    if experience_repository.get(request.experience_id) is None:
        raise HTTPException(status_code=404, detail="Experience not found.")

    feedback_id = feedback_repository.create(request)
    return FeedbackCreateResponse(
        feedback_id=feedback_id,
        experience_id=request.experience_id,
        feedback_type=request.feedback_type,
        status="received",
    )
