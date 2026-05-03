from typing import Annotated

from fastapi import APIRouter, Depends

from server.config import Settings, get_settings
from server.core.prompt_importer import PromptImporter
from server.models.imported_skill import PromptImportRequest, PromptImportResponse
from server.storage.repositories import ImportedSkillRepository

router = APIRouter(prefix="/v1/skills", tags=["skills"])


def get_imported_skill_repository(
    settings: Annotated[Settings, Depends(get_settings)],
) -> ImportedSkillRepository:
    return ImportedSkillRepository(settings.database_url)


def get_prompt_importer(
    repository: Annotated[ImportedSkillRepository, Depends(get_imported_skill_repository)],
) -> PromptImporter:
    return PromptImporter(repository)


@router.post("/import_prompt", response_model=PromptImportResponse)
def import_prompt(
    request: PromptImportRequest,
    importer: Annotated[PromptImporter, Depends(get_prompt_importer)],
) -> PromptImportResponse:
    return PromptImportResponse(skill=importer.import_prompt(request))
