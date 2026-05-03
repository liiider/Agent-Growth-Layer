import json

from pydantic import ValidationError

from server.core.llm import ChatClient
from server.models.cognition import CognitionCandidate
from server.models.experience import ExperienceRead
from server.storage.repositories import CognitionRepository, ExperienceRepository


class CognitionExtractor:
    def __init__(
        self,
        experience_repository: ExperienceRepository,
        cognition_repository: CognitionRepository,
        chat_client: ChatClient | None = None,
    ) -> None:
        self.experience_repository = experience_repository
        self.cognition_repository = cognition_repository
        self.chat_client = chat_client

    def extract(self, experience_id: str) -> None:
        experience = self.experience_repository.get(experience_id)
        if experience is None:
            return

        self.experience_repository.set_extraction_status(experience_id, "processing")
        try:
            candidate = self._build_candidate(experience)
            self.cognition_repository.delete_for_experience(experience.id)
            self.cognition_repository.create_from_experience(
                experience=experience,
                candidate=candidate,
            )
            self.experience_repository.set_extraction_status(experience_id, "succeeded")
        except Exception:
            self.experience_repository.set_extraction_status(experience_id, "failed")
            raise

    def _build_candidate(self, experience: ExperienceRead) -> CognitionCandidate:
        if self.chat_client is not None:
            return self._build_candidate_with_llm(experience)
        return _build_deterministic_candidate(experience)

    def _build_candidate_with_llm(self, experience: ExperienceRead) -> CognitionCandidate:
        payload = self.chat_client.complete_json(
            [
                {
                    "role": "system",
                    "content": (
                        "Extract one reusable Agent Growth Layer cognition from an agent "
                        "experience. Return only JSON with keys: type, content, confidence, weight."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(experience.model_dump(), ensure_ascii=False),
                },
            ]
        )
        try:
            return CognitionCandidate.model_validate(payload)
        except ValidationError as exc:
            raise RuntimeError(
                "LLM cognition extraction response failed schema validation."
            ) from exc


def _build_deterministic_candidate(experience: ExperienceRead) -> CognitionCandidate:
    source = experience.feedback or experience.agent_output
    content = source.strip()
    if not content.endswith("."):
        content = f"{content}."

    if experience.result_status in {"corrected", "failed"}:
        cognition_type = "error_pattern"
        confidence = 0.78
    else:
        cognition_type = "rule"
        confidence = 0.66

    return CognitionCandidate(
        type=cognition_type,
        content=content,
        confidence=confidence,
        weight=_weight_from_risk(experience.risk_level),
    )


def _weight_from_risk(risk_level: str) -> str:
    if risk_level == "high":
        return "high"
    if risk_level == "medium":
        return "medium"
    return "low"
