from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from server.config import Settings, get_settings
from server.core.extractor import CognitionExtractor
from server.core.llm import build_chat_client
from server.models.experience import (
    ExperienceCreate,
    ExperienceCreateResponse,
    ExperienceRead,
    ExperienceRetryResponse,
)
from server.storage.repositories import CognitionRepository, ExperienceRepository

router = APIRouter(prefix="/v1/experiences", tags=["experiences"])


def get_experience_repository(
    settings: Annotated[Settings, Depends(get_settings)],
) -> ExperienceRepository:
    return ExperienceRepository(settings.database_url)


def get_cognition_repository(
    settings: Annotated[Settings, Depends(get_settings)],
) -> CognitionRepository:
    return CognitionRepository(settings.database_url)


def get_extractor(
    settings: Annotated[Settings, Depends(get_settings)],
    experience_repository: Annotated[ExperienceRepository, Depends(get_experience_repository)],
    cognition_repository: Annotated[CognitionRepository, Depends(get_cognition_repository)],
) -> CognitionExtractor:
    return CognitionExtractor(
        experience_repository,
        cognition_repository,
        chat_client=build_chat_client(settings),
    )


@router.post("", response_model=ExperienceCreateResponse)
def create_experience(
    request: ExperienceCreate,
    background_tasks: BackgroundTasks,
    experience_repository: Annotated[ExperienceRepository, Depends(get_experience_repository)],
    extractor: Annotated[CognitionExtractor, Depends(get_extractor)],
) -> ExperienceCreateResponse:
    experience_id = experience_repository.create(request)
    background_tasks.add_task(extractor.extract, experience_id)
    return ExperienceCreateResponse(
        experience_id=experience_id,
        status="received",
        extraction_status="queued",
    )


@router.get("/{experience_id}", response_model=ExperienceRead)
def get_experience(
    experience_id: str,
    experience_repository: Annotated[ExperienceRepository, Depends(get_experience_repository)],
) -> ExperienceRead:
    experience = experience_repository.get(experience_id)
    if experience is None:
        raise HTTPException(status_code=404, detail="Experience not found.")
    return experience


@router.post("/{experience_id}/extract", response_model=ExperienceRetryResponse)
def retry_extraction(
    experience_id: str,
    background_tasks: BackgroundTasks,
    experience_repository: Annotated[ExperienceRepository, Depends(get_experience_repository)],
    extractor: Annotated[CognitionExtractor, Depends(get_extractor)],
) -> ExperienceRetryResponse:
    experience = experience_repository.get(experience_id)
    if experience is None:
        raise HTTPException(status_code=404, detail="Experience not found.")

    experience_repository.set_extraction_status(experience_id, "retrying")
    background_tasks.add_task(extractor.extract, experience_id)
    return ExperienceRetryResponse(
        experience_id=experience_id,
        extraction_status="retrying",
    )
