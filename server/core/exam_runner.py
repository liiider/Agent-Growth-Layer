from server.models.exam import ExamRequest, ExamResponse
from server.models.skill import SkillRead
from server.storage.repositories import ExamRepository, SkillRepository

PASSING_SCORE = 0.75


class ExamRunner:
    def __init__(
        self,
        skill_repository: SkillRepository,
        exam_repository: ExamRepository,
    ) -> None:
        self.skill_repository = skill_repository
        self.exam_repository = exam_repository

    def run(self, skill: SkillRead, request: ExamRequest) -> ExamResponse:
        previous_status = skill.status
        self.skill_repository.update_status(skill.id, "testing")
        score = request.score if request.score is not None else _score_from_cases(request)
        failures = _failures_from_score(score)
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
