from server.core.llm import ChatClient
from server.models.exam import ExamRequest, ExamResponse
from server.models.skill import SkillRead
from server.storage.repositories import ExamRepository, SkillRepository

PASSING_SCORE = 0.75


class ExamRunner:
    def __init__(
        self,
        skill_repository: SkillRepository,
        exam_repository: ExamRepository,
        chat_client: ChatClient | None = None,
    ) -> None:
        self.skill_repository = skill_repository
        self.exam_repository = exam_repository
        self.chat_client = chat_client

    def run(self, skill: SkillRead, request: ExamRequest) -> ExamResponse:
        previous_status = skill.status
        self.skill_repository.update_status(skill.id, "testing")
        score, failures = self._score(skill, request)
        passed = score >= PASSING_SCORE
        new_status = "verified" if passed else "failed"
        exam_id = self.exam_repository.create(
            skill_id=skill.id,
            evaluator=request.evaluator,
            score=score,
            passed=passed,
            failures=failures,
            status_before="testing",
            status_after=new_status,
        )
        self.skill_repository.update_status(skill.id, new_status, exam_score=score)
        return ExamResponse(
            exam_id=exam_id,
            skill_id=skill.id,
            previous_status=previous_status,
            score=score,
            passed=passed,
            failures=failures,
            new_status=new_status,
        )

    def _score(self, skill: SkillRead, request: ExamRequest) -> tuple[float, list[str]]:
        if request.score is not None:
            score = request.score
            return score, _failures_from_score(score)
        if request.evaluator == "llm_judge" and self.chat_client is not None:
            return self._score_with_llm(skill, request)
        score = _score_from_cases(request)
        return score, _failures_from_score(score)

    def _score_with_llm(self, skill: SkillRead, request: ExamRequest) -> tuple[float, list[str]]:
        payload = self.chat_client.complete_json(
            [
                {
                    "role": "system",
                    "content": (
                        "Judge whether an Agent Growth Layer skill satisfies the exam cases. "
                        "Return json with keys: score and failures. score must be a number "
                        "between 0 and 1. failures must be a string array. Example json: "
                        "{\"score\":0.8,\"failures\":[]}"
                    ),
                },
                {
                    "role": "user",
                    "content": skill.model_dump_json() + "\n" + request.model_dump_json(),
                },
            ]
        )
        score = float(payload.get("score", 0))
        failures = payload.get("failures", [])
        if not isinstance(failures, list):
            failures = []
        return max(0.0, min(1.0, score)), [
            failure for failure in failures if isinstance(failure, str) and failure.strip()
        ]


def _score_from_cases(request: ExamRequest) -> float:
    if not request.cases:
        return 0.0

    scored_cases = [
        1.0 if case.expected_behavior and case.forbidden_behavior else 0.5
        for case in request.cases
    ]
    return sum(scored_cases) / len(scored_cases)


def _failures_from_score(score: float) -> list[str]:
    if score >= PASSING_SCORE:
        return []
    return [f"Score {score:.2f} is below passing threshold {PASSING_SCORE:.2f}."]
