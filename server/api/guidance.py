from typing import Annotated

from fastapi import APIRouter, Depends

from server.config import Settings, get_settings
from server.core.guidance_builder import GuidanceBuilder
from server.core.seed_skills import SeedSkillRepository
from server.models.guidance import GuidanceRequest, GuidanceResponse
from server.storage.repositories import CognitionRepository

router = APIRouter(prefix="/v1", tags=["guidance"])


def get_guidance_builder(settings: Annotated[Settings, Depends(get_settings)]) -> GuidanceBuilder:
    seed_skill_repository = SeedSkillRepository(settings.seed_skills_dir)
    cognition_repository = CognitionRepository(settings.database_url)
    return GuidanceBuilder(seed_skill_repository, cognition_repository)


@router.post("/guidance", response_model=GuidanceResponse)
def create_guidance(
    request: GuidanceRequest,
    builder: Annotated[GuidanceBuilder, Depends(get_guidance_builder)],
) -> GuidanceResponse:
    return builder.build(request)
