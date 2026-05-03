from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from server.config import Settings, get_settings
from server.core.seed_skills import SeedSkillRepository
from server.models.seed_skill import SeedSkill

router = APIRouter(prefix="/v1/seed-skills", tags=["seed-skills"])


def get_seed_skill_repository(
    settings: Annotated[Settings, Depends(get_settings)],
) -> SeedSkillRepository:
    return SeedSkillRepository(settings.seed_skills_dir)


@router.get("", response_model=list[SeedSkill])
def list_seed_skills(
    repository: Annotated[SeedSkillRepository, Depends(get_seed_skill_repository)],
) -> list[SeedSkill]:
    return repository.list()


@router.get("/{skill_id}", response_model=SeedSkill)
def get_seed_skill(
    skill_id: str,
    repository: Annotated[SeedSkillRepository, Depends(get_seed_skill_repository)],
) -> SeedSkill:
    skill = repository.get(skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail="Seed skill not found.")
    return skill
