from uuid import uuid4

from server.core.llm import ChatClient
from server.models.imported_skill import ImportedSkill, PromptImportRequest
from server.storage.repositories import ImportedSkillRepository


class PromptImporter:
    def __init__(
        self,
        imported_skill_repository: ImportedSkillRepository,
        chat_client: ChatClient | None = None,
    ) -> None:
        self.imported_skill_repository = imported_skill_repository
        self.chat_client = chat_client

    def import_prompt(self, request: PromptImportRequest) -> ImportedSkill:
        import_id = f"prompt_import_{uuid4().hex[:12]}"
        if self.chat_client is not None:
            skill = self._import_prompt_with_llm(request, import_id)
            self.imported_skill_repository.create(skill, import_id=import_id)
            return skill

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

    def _import_prompt_with_llm(
        self,
        request: PromptImportRequest,
        import_id: str,
    ) -> ImportedSkill:
        payload = self.chat_client.complete_json(
            [
                {
                    "role": "system",
                    "content": (
                        "Convert a developer prompt into one reusable Agent Growth Layer skill. "
                        "Return JSON with keys: name, procedure, constraints, confidence, weight."
                    ),
                },
                {"role": "user", "content": request.model_dump_json()},
            ]
        )
        return ImportedSkill(
            id=f"skill_imported_{uuid4().hex[:12]}",
            name=str(payload.get("name") or _skill_name(request.intent)),
            status="candidate",
            agent_id=request.agent_id,
            domain=request.domain,
            intent=request.intent,
            procedure=_string_list(payload.get("procedure")) or _extract_procedure(request.prompt),
            constraints=_string_list(payload.get("constraints")),
            evidence_refs=[import_id],
            weight=str(payload.get("weight") or "medium"),
            confidence=float(payload.get("confidence") or 0.7),
        )


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


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item.strip()]
