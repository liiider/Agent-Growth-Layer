from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from server.config import Settings, get_settings
from server.core.exam_runner import ExamRunner
from server.core.prompt_importer import PromptImporter
from server.models.exam import ExamRequest, ExamResponse
from server.models.imported_skill import PromptImportRequest, PromptImportResponse
from server.models.skill import (
    SkillBuildRequest,
    SkillBuildResponse,
    SkillRead,
    SkillStatusUpdate,
    SkillUpdateRequest,
)
from server.storage.repositories import (
    CognitionRepository,
    ExamRepository,
    ImportedSkillRepository,
    SkillRepository,
)

router = APIRouter(prefix="/v1/skills", tags=["skills"])


def get_imported_skill_repository(
    settings: Annotated[Settings, Depends(get_settings)],
) -> ImportedSkillRepository:
    return ImportedSkillRepository(settings.database_url)


def get_cognition_repository(
    settings: Annotated[Settings, Depends(get_settings)],
) -> CognitionRepository:
    return CognitionRepository(settings.database_url)


def get_skill_repository(
    settings: Annotated[Settings, Depends(get_settings)],
) -> SkillRepository:
    return SkillRepository(settings.database_url)


def get_exam_repository(
    settings: Annotated[Settings, Depends(get_settings)],
) -> ExamRepository:
    return ExamRepository(settings.database_url)


def get_prompt_importer(
    repository: Annotated[ImportedSkillRepository, Depends(get_imported_skill_repository)],
) -> PromptImporter:
    return PromptImporter(repository)


def get_exam_runner(
    skill_repository: Annotated[SkillRepository, Depends(get_skill_repository)],
    exam_repository: Annotated[ExamRepository, Depends(get_exam_repository)],
) -> ExamRunner:
    return ExamRunner(skill_repository, exam_repository)


@router.post("/import_prompt", response_model=PromptImportResponse)
def import_prompt(
    request: PromptImportRequest,
    importer: Annotated[PromptImporter, Depends(get_prompt_importer)],
) -> PromptImportResponse:
    return PromptImportResponse(skill=importer.import_prompt(request))


@router.post("/build", response_model=SkillBuildResponse)
def build_skill(
    request: SkillBuildRequest,
    cognition_repository: Annotated[CognitionRepository, Depends(get_cognition_repository)],
    skill_repository: Annotated[SkillRepository, Depends(get_skill_repository)],
) -> SkillBuildResponse:
    cognitions = []
    for cognition_id in request.cognition_ids:
        cognition = cognition_repository.get(cognition_id)
        if cognition is None:
            raise HTTPException(status_code=404, detail=f"Cognition not found: {cognition_id}")
        cognitions.append(cognition)
    return SkillBuildResponse(skill=skill_repository.build_from_cognitions(request, cognitions))


@router.get("", response_model=list[SkillRead])
def list_skills(
    repository: Annotated[SkillRepository, Depends(get_skill_repository)],
    agent_id: str | None = None,
    domain: str | None = None,
    intent: str | None = None,
    status: str | None = None,
    limit: int = Query(default=50, ge=1, le=100),
) -> list[SkillRead]:
    return repository.list(
        agent_id=agent_id,
        domain=domain,
        intent=intent,
        status=status,
        limit=limit,
    )


@router.get("/{skill_id}", response_model=SkillRead)
def get_skill(
    skill_id: str,
    repository: Annotated[SkillRepository, Depends(get_skill_repository)],
) -> SkillRead:
    skill = repository.get(skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill not found.")
    return skill


@router.patch("/{skill_id}", response_model=SkillRead)
def update_skill(
    skill_id: str,
    request: SkillUpdateRequest,
    repository: Annotated[SkillRepository, Depends(get_skill_repository)],
) -> SkillRead:
    skill = repository.update(skill_id, request)
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill not found.")
    return skill


@router.patch("/{skill_id}/status", response_model=SkillRead)
def update_skill_status(
    skill_id: str,
    request: SkillStatusUpdate,
    repository: Annotated[SkillRepository, Depends(get_skill_repository)],
) -> SkillRead:
    skill = repository.update_status(skill_id, request.status)
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill not found.")
    return skill


@router.post("/{skill_id}/exam", response_model=ExamResponse)
def run_exam(
    skill_id: str,
    request: ExamRequest,
    skill_repository: Annotated[SkillRepository, Depends(get_skill_repository)],
    exam_runner: Annotated[ExamRunner, Depends(get_exam_runner)],
) -> ExamResponse:
    skill = skill_repository.get(skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill not found.")
    return exam_runner.run(skill, request)
