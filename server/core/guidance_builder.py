from uuid import uuid4

from server.core.seed_skills import SeedSkillRepository
from server.models.guidance import GuidancePayload, GuidanceRequest, GuidanceResponse


class GuidanceBuilder:
    def __init__(self, seed_skill_repository: SeedSkillRepository) -> None:
        self.seed_skill_repository = seed_skill_repository

    def build(self, request: GuidanceRequest) -> GuidanceResponse:
        seed_skills = self._select_seed_skills(request)
        output_guidance = self._merge_output_guidance(seed_skills)
        tool_policy = self._merge_tool_policy(seed_skills)

        return GuidanceResponse(
            id=f"guide_{uuid4().hex[:12]}",
            agent_id=request.agent_id,
            domain=request.domain,
            intent=request.intent,
            guidance=GuidancePayload(
                seed_skills=seed_skills,
                output_guidance=output_guidance,
                tool_policy=tool_policy,
            ),
        )

    @staticmethod
    def _merge_output_guidance(seed_skills: list) -> list[str]:
        return _unique(item for skill in seed_skills for item in skill.output_guidance)

    @staticmethod
    def _merge_tool_policy(seed_skills: list) -> list[str]:
        return _unique(item for skill in seed_skills for item in skill.tool_policy)

    def _select_seed_skills(self, request: GuidanceRequest) -> list:
        skills = self.seed_skill_repository.list()
        domain_matches = [
            skill for skill in skills if request.domain in skill.domain
        ]
        general_matches = [
            skill
            for skill in skills
            if "general" in skill.domain and skill not in domain_matches
        ]
        return domain_matches + general_matches


def _unique(items: object) -> list[str]:
    values: list[str] = []
    for item in items:
        if item not in values:
            values.append(item)
    return values
