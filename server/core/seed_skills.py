from pathlib import Path

import yaml

from server.models.seed_skill import SeedSkill


class SeedSkillRepository:
    def __init__(self, seed_skills_dir: Path) -> None:
        self.seed_skills_dir = seed_skills_dir

    def list(self) -> list[SeedSkill]:
        if not self.seed_skills_dir.exists():
            return []

        skills = [
            self._load_file(path)
            for path in sorted(self.seed_skills_dir.glob("*.yaml"))
            if path.is_file()
        ]
        return skills

    def get(self, skill_id: str) -> SeedSkill | None:
        return next((skill for skill in self.list() if skill.id == skill_id), None)

    def _load_file(self, path: Path) -> SeedSkill:
        with path.open("r", encoding="utf-8") as file:
            data = yaml.safe_load(file) or {}
        return SeedSkill.model_validate(data)
