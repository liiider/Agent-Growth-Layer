from pathlib import Path

import pytest

from server.core.seed_skills import SeedSkillRepository


def test_all_seed_skill_templates_match_schema() -> None:
    repository = SeedSkillRepository(Path("templates/seed_skills"))

    skills = repository.list()

    assert len(skills) == 8
    assert {skill.status for skill in skills} == {"seed"}
    assert all(skill.id.startswith("seed_") for skill in skills)
    assert all(skill.instructions for skill in skills)
    assert all(skill.domain for skill in skills)
    assert all(skill.intent for skill in skills)


def test_seed_skill_repository_rejects_invalid_yaml(tmp_path: Path) -> None:
    skill_file = tmp_path / "invalid.yaml"
    skill_file.write_text(
        """
id: seed_invalid
name: Invalid
version: 0.1.0
status: candidate
description: Invalid status should fail.
""",
        encoding="utf-8",
    )

    repository = SeedSkillRepository(tmp_path)

    with pytest.raises(ValueError):
        repository.list()
