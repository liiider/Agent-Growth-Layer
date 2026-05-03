from uuid import uuid4

from server.models.imported_skill import ImportedSkill, PromptImportRequest
from server.storage.repositories import ImportedSkillRepository


class PromptImporter:
    def __init__(self, imported_skill_repository: ImportedSkillRepository) -> None:
        self.imported_skill_repository = imported_skill_repository

    def import_prompt(self, request: PromptImportRequest) -> ImportedSkill:
        import_id = f"prompt_import_{uuid4().hex[:12]}"
        skill = ImportedSkill(
            id=f"skill_imported_{uuid4().hex[:12]}",
            name=_skill_name(request.intent),
            status="candidate",
            agent_id=request.agent_id,
            domain=request.domain,
            intent=request.intent,
            procedure=_extract_procedure(request.prompt),
            constraints=_extract_constraints(request.prompt),
            evidence_refs=[import_id],
            weight="medium",
            confidence=0.7,
        )
        self.imported_skill_repository.create(skill, import_id=import_id)
        return skill


def _skill_name(intent: str) -> str:
    words = intent.replace("_", " ").strip().title()
    return f"Imported {words} Skill" if words else "Imported Prompt Skill"


def _extract_procedure(prompt: str) -> list[str]:
    sentences = _sentences(prompt)
    procedures = [
        _normalize_instruction(sentence)
        for sentence in sentences
        if sentence.lower().startswith(("always ", "check ", "retrieve ", "first "))
    ]
    return procedures or [_normalize_instruction(sentences[0] if sentences else prompt)]


def _extract_constraints(prompt: str) -> list[str]:
    sentences = _sentences(prompt)
    constraints = [
        _normalize_instruction(sentence)
        for sentence in sentences
        if sentence.lower().startswith(("never ", "do not ", "don't "))
    ]
    return constraints


def _sentences(prompt: str) -> list[str]:
    normalized = prompt.replace("\n", " ").strip()
    return [
        sentence.strip()
        for sentence in normalized.split(".")
        if sentence.strip()
    ]


def _normalize_instruction(sentence: str) -> str:
    sentence = sentence.strip()
    if sentence.lower().startswith("always "):
        sentence = sentence[7:]
    if not sentence:
        return sentence
    return f"{sentence[0].upper()}{sentence[1:]}"
