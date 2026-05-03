from uuid import uuid4

from server.core.seed_skills import SeedSkillRepository
from server.models.guidance import GuidancePayload, GuidanceRequest, GuidanceResponse
from server.storage.repositories import (
    CognitionRepository,
    ImportedSkillRepository,
    SkillRepository,
)


class GuidanceBuilder:
    def __init__(
        self,
        seed_skill_repository: SeedSkillRepository,
        cognition_repository: CognitionRepository | None = None,
        imported_skill_repository: ImportedSkillRepository | None = None,
        skill_repository: SkillRepository | None = None,
    ) -> None:
        self.seed_skill_repository = seed_skill_repository
        self.cognition_repository = cognition_repository
        self.imported_skill_repository = imported_skill_repository
        self.skill_repository = skill_repository

    def build(self, request: GuidanceRequest) -> GuidanceResponse:
        seed_skills = self._select_seed_skills(request)
        verified_skills = self._select_verified_skills(request)
        candidate_skills = self._select_candidate_guidance(request)
        output_guidance = self._merge_output_guidance(seed_skills)
        tool_policy = self._merge_tool_policy(seed_skills)

        return GuidanceResponse(
            id=f"guide_{uuid4().hex[:12]}",
            agent_id=request.agent_id,
            domain=request.domain,
            intent=request.intent,
            guidance=GuidancePayload(
                verified_skills=verified_skills,
                candidate_skills=candidate_skills,
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

    def _select_candidate_guidance(self, request: GuidanceRequest) -> list[dict]:
        if self.cognition_repository is None:
            return []

        cognitions = self.cognition_repository.list(
            agent_id=request.agent_id,
            domain=request.domain,
            intent=request.intent,
            status="candidate",
            limit=10,
        )
        candidates = [
            {
                "id": cognition.id,
                "name": _candidate_name(cognition.content),
                "status": cognition.status,
                "weight": cognition.weight,
                "confidence": cognition.confidence,
                "instructions": [cognition.content],
                "constraints": [cognition.content]
                if cognition.type in {"constraint", "error_pattern"}
                else [],
                "evidence_refs": cognition.evidence_refs,
            }
            for cognition in cognitions
        ]
        candidates.extend(self._select_imported_skill_guidance(request))
        return candidates

    def _select_imported_skill_guidance(self, request: GuidanceRequest) -> list[dict]:
        if self.imported_skill_repository is None:
            return []

        imported_skills = self.imported_skill_repository.list_candidates(
            agent_id=request.agent_id,
            domain=request.domain,
            intent=request.intent,
            limit=10,
        )
        return [
            {
                "id": skill.id,
                "name": skill.name,
                "status": skill.status,
                "weight": skill.weight,
                "confidence": skill.confidence,
                "instructions": skill.procedure,
                "constraints": skill.constraints,
                "evidence_refs": skill.evidence_refs,
            }
            for skill in imported_skills
        ]

    def _select_verified_skills(self, request: GuidanceRequest) -> list[dict]:
        if self.skill_repository is None:
            return []

        skills = self.skill_repository.list(
            agent_id=request.agent_id,
            domain=request.domain,
            intent=request.intent,
            status="verified",
            limit=10,
        )
        return [
            {
                "id": skill.id,
                "name": skill.name,
                "status": skill.status,
                "exam_score": skill.exam_score,
                "instructions": skill.procedure,
                "constraints": skill.constraints,
                "evidence_refs": skill.evidence_refs,
                "latest_exam": skill.latest_exam.model_dump() if skill.latest_exam else None,
            }
            for skill in skills
        ]


def _unique(items: object) -> list[str]:
    values: list[str] = []
    for item in items:
        if item not in values:
            values.append(item)
    return values


def _candidate_name(content: str) -> str:
    normalized = content.strip().rstrip(".")
    if len(normalized) <= 64:
        return normalized
    return f"{normalized[:61]}..."
