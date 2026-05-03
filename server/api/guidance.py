from typing import Annotated

from fastapi import APIRouter, Depends

from server.config import Settings, get_settings
from server.core.guidance_builder import GuidanceBuilder
from server.core.seed_skills import SeedSkillRepository
from server.models.guidance import GuidanceRequest, GuidanceResponse

router = APIRouter(prefix="/v1", tags=["guidance"])


def get_guidance_builder(settings: Annotated[Settings, Depends(get_settings)]) -> GuidanceBuilder:
    repository = SeedSkillRepository(settings.seed_skills_dir)
    return GuidanceBuilder(repository)


@router.post("/guidance", response_model=GuidanceResponse)
def create_guidance(
    request: GuidanceRequest,
    builder: Annotated[GuidanceBuilder, Depends(get_guidance_builder)],
) -> GuidanceResponse:
    return builder.build(request)
