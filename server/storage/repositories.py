from typing import Any
from uuid import uuid4

from server.models.cognition import CognitionCandidate, CognitionRead
from server.models.experience import ExperienceCreate, ExperienceRead
from server.models.feedback import FeedbackCreate
from server.models.imported_skill import ImportedSkill
from server.models.review import ReviewCreate
from server.models.skill import LatestExam, SkillBuildRequest, SkillRead, SkillUpdateRequest
from server.storage.sqlite import connect, decode_json, encode_json, initialize_database


class ExperienceRepository:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url
        initialize_database(database_url)

    def create(self, request: ExperienceCreate) -> str:
        experience_id = f"exp_{uuid4().hex[:12]}"
        with connect(self.database_url) as connection:
            connection.execute(
                """
                INSERT INTO experiences (
                  id, agent_id, domain, intent, user_input, agent_output,
                  tools_used, retrieved_context, feedback, result_status,
                  risk_level, extraction_status, metadata
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    experience_id,
                    request.agent_id,
                    request.domain,
                    request.intent,
                    request.user_input,
                    request.agent_output,
                    encode_json(request.tools_used),
                    encode_json(request.retrieved_context),
                    request.feedback,
                    request.result_status,
                    request.risk_level,
                    "queued",
                    encode_json(request.metadata),
                ),
            )
        return experience_id

    def get(self, experience_id: str) -> ExperienceRead | None:
        with connect(self.database_url) as connection:
            row = connection.execute(
                "SELECT * FROM experiences WHERE id = ?",
                (experience_id,),
            ).fetchone()
            if row is None:
                return None

            cognition_rows = connection.execute(
                "SELECT id FROM cognitions WHERE experience_id = ? ORDER BY created_at ASC",
                (experience_id,),
            ).fetchall()

        return _experience_from_row(
            row,
            cognition_ids=[cognition_row["id"] for cognition_row in cognition_rows],
        )

    def set_extraction_status(self, experience_id: str, status: str) -> None:
        with connect(self.database_url) as connection:
            connection.execute(
                """
                UPDATE experiences
                SET extraction_status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (status, experience_id),
            )


class CognitionRepository:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url
        initialize_database(database_url)

    def create_from_experience(
        self,
        *,
        experience: ExperienceRead,
        candidate: CognitionCandidate,
    ) -> str:
        cognition_id = f"cog_{uuid4().hex[:12]}"
        evidence_refs = [experience.id]
        with connect(self.database_url) as connection:
            connection.execute(
                """
                INSERT INTO cognitions (
                  id, experience_id, type, content, agent_id, domain, intent,
                  confidence, risk_level, weight, status, evidence_refs
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    cognition_id,
                    experience.id,
                    candidate.type,
                    candidate.content,
                    experience.agent_id,
                    experience.domain,
                    experience.intent,
                    candidate.confidence,
                    experience.risk_level,
                    candidate.weight,
                    "candidate",
                    encode_json(evidence_refs),
                ),
            )
        return cognition_id

    def delete_for_experience(self, experience_id: str) -> None:
        with connect(self.database_url) as connection:
            connection.execute(
                "DELETE FROM cognitions WHERE experience_id = ?",
                (experience_id,),
            )

    def list(
        self,
        *,
        agent_id: str | None = None,
        domain: str | None = None,
        intent: str | None = None,
        status: str | None = None,
        limit: int = 50,
    ) -> list[CognitionRead]:
        clauses: list[str] = []
        values: list[Any] = []
        for field, value in {
            "agent_id": agent_id,
            "domain": domain,
            "intent": intent,
            "status": status,
        }.items():
            if value is not None:
                clauses.append(f"{field} = ?")
                values.append(value)

        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        values.append(limit)
        with connect(self.database_url) as connection:
            rows = connection.execute(
                f"SELECT * FROM cognitions {where} ORDER BY created_at DESC LIMIT ?",
                values,
            ).fetchall()
        return [_cognition_from_row(row) for row in rows]

    def get(self, cognition_id: str) -> CognitionRead | None:
        with connect(self.database_url) as connection:
            row = connection.execute(
                "SELECT * FROM cognitions WHERE id = ?",
                (cognition_id,),
            ).fetchone()
        return _cognition_from_row(row) if row else None

    def update_status(self, cognition_id: str, status: str) -> CognitionRead | None:
        with connect(self.database_url) as connection:
            connection.execute(
                """
                UPDATE cognitions
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (status, cognition_id),
            )
        return self.get(cognition_id)


class FeedbackRepository:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url
        initialize_database(database_url)

    def create(self, request: FeedbackCreate) -> str:
        feedback_id = f"fb_{uuid4().hex[:12]}"
        with connect(self.database_url) as connection:
            connection.execute(
                """
                INSERT INTO feedback (id, experience_id, feedback_type, content, score)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    feedback_id,
                    request.experience_id,
                    request.feedback_type,
                    request.content,
                    request.score,
                ),
            )
        return feedback_id


class ImportedSkillRepository:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url
        initialize_database(database_url)

    def create(self, skill: ImportedSkill, *, import_id: str) -> None:
        with connect(self.database_url) as connection:
            connection.execute(
                """
                INSERT INTO imported_skills (
                  id, import_id, agent_id, name, domain, intent, status,
                  weight, confidence, procedure, constraints, evidence_refs
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    skill.id,
                    import_id,
                    skill.agent_id,
                    skill.name,
                    skill.domain,
                    skill.intent,
                    skill.status,
                    skill.weight,
                    skill.confidence,
                    encode_json(skill.procedure),
                    encode_json(skill.constraints),
                    encode_json(skill.evidence_refs),
                ),
            )

    def list_candidates(
        self,
        *,
        agent_id: str,
        domain: str,
        intent: str,
        limit: int = 20,
    ) -> list[ImportedSkill]:
        with connect(self.database_url) as connection:
            rows = connection.execute(
                """
                SELECT * FROM imported_skills
                WHERE agent_id = ? AND domain = ? AND intent = ? AND status = 'candidate'
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (agent_id, domain, intent, limit),
            ).fetchall()
        return [_imported_skill_from_row(row) for row in rows]


class SkillRepository:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url
        initialize_database(database_url)

    def build_from_cognitions(
        self,
        request: SkillBuildRequest,
        cognitions: list[CognitionRead],
    ) -> SkillRead:
        skill_id = f"skill_{uuid4().hex[:12]}"
        procedure = [cognition.content for cognition in cognitions]
        constraints = [
            cognition.content
            for cognition in cognitions
            if cognition.type in {"constraint", "error_pattern"}
        ]
        error_patterns = [
            cognition.content for cognition in cognitions if cognition.type == "error_pattern"
        ]
        evidence_refs = [cognition.id for cognition in cognitions]
        weight = _max_weight([cognition.weight for cognition in cognitions])
        confidence = min(
            0.99,
            sum(cognition.confidence for cognition in cognitions) / len(cognitions),
        )

        with connect(self.database_url) as connection:
            connection.execute(
                """
                INSERT INTO skills (
                  id, agent_id, name, domain, intent, status, weight, confidence,
                  version, procedure, constraints, error_patterns, negative_examples,
                  tool_policy, output_guidance, evidence_refs
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    skill_id,
                    request.agent_id,
                    request.name,
                    request.domain,
                    request.intent,
                    "candidate",
                    weight,
                    confidence,
                    "0.1.0",
                    encode_json(procedure),
                    encode_json(constraints),
                    encode_json(error_patterns),
                    encode_json([]),
                    encode_json([]),
                    encode_json([]),
                    encode_json(evidence_refs),
                ),
            )
        skill = self.get(skill_id)
        if skill is None:
            msg = "Failed to create skill."
            raise RuntimeError(msg)
        return skill

    def list(
        self,
        *,
        agent_id: str | None = None,
        domain: str | None = None,
        intent: str | None = None,
        status: str | None = None,
        limit: int = 50,
    ) -> list[SkillRead]:
        clauses: list[str] = []
        values: list[Any] = []
        for field, value in {
            "agent_id": agent_id,
            "domain": domain,
            "intent": intent,
            "status": status,
        }.items():
            if value is not None:
                clauses.append(f"{field} = ?")
                values.append(value)

        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        values.append(limit)
        with connect(self.database_url) as connection:
            rows = connection.execute(
                f"SELECT * FROM skills {where} ORDER BY created_at DESC LIMIT ?",
                values,
            ).fetchall()
        return [self._skill_from_row(row) for row in rows]

    def get(self, skill_id: str) -> SkillRead | None:
        with connect(self.database_url) as connection:
            row = connection.execute(
                "SELECT * FROM skills WHERE id = ?",
                (skill_id,),
            ).fetchone()
        return self._skill_from_row(row) if row else None

    def update(self, skill_id: str, request: SkillUpdateRequest) -> SkillRead | None:
        skill = self.get(skill_id)
        if skill is None:
            return None

        with connect(self.database_url) as connection:
            procedure = (
                request.procedure
                if request.procedure is not None
                else skill.procedure
            )
            connection.execute(
                """
                UPDATE skills
                SET name = ?, procedure = ?, constraints = ?,
                    output_guidance = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    request.name or skill.name,
                    encode_json(procedure),
                    encode_json(
                        request.constraints
                        if request.constraints is not None
                        else skill.constraints
                    ),
                    encode_json(
                        request.output_guidance
                        if request.output_guidance is not None
                        else skill.output_guidance
                    ),
                    skill_id,
                ),
            )
        return self.get(skill_id)

    def update_status(
        self,
        skill_id: str,
        status: str,
        *,
        exam_score: float | None = None,
    ) -> SkillRead | None:
        with connect(self.database_url) as connection:
            connection.execute(
                """
                UPDATE skills
                SET status = ?, exam_score = COALESCE(?, exam_score),
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (status, exam_score, skill_id),
            )
        return self.get(skill_id)

    def _skill_from_row(self, row: Any) -> SkillRead:
        latest_exam = self._latest_exam(row["id"])
        return SkillRead(
            id=row["id"],
            agent_id=row["agent_id"],
            name=row["name"],
            domain=row["domain"],
            intent=row["intent"],
            status=row["status"],
            weight=row["weight"],
            confidence=row["confidence"],
            version=row["version"],
            procedure=decode_json(row["procedure"]) or [],
            constraints=decode_json(row["constraints"]) or [],
            error_patterns=decode_json(row["error_patterns"]) or [],
            negative_examples=decode_json(row["negative_examples"]) or [],
            tool_policy=decode_json(row["tool_policy"]) or [],
            output_guidance=decode_json(row["output_guidance"]) or [],
            evidence_refs=decode_json(row["evidence_refs"]) or [],
            exam_score=row["exam_score"],
            latest_exam=latest_exam,
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def _latest_exam(self, skill_id: str) -> LatestExam | None:
        with connect(self.database_url) as connection:
            row = connection.execute(
                """
                SELECT * FROM exams
                WHERE skill_id = ?
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (skill_id,),
            ).fetchone()
        if row is None:
            return None
        return LatestExam(
            exam_id=row["id"],
            evaluator=row["evaluator"],
            score=row["score"],
            passed=bool(row["passed"]),
            status_before=row["status_before"],
            status_after=row["status_after"],
            failures=decode_json(row["failures"]) or [],
            created_at=row["created_at"],
        )


class ExamRepository:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url
        initialize_database(database_url)

    def create(
        self,
        *,
        skill_id: str,
        evaluator: str,
        score: float,
        passed: bool,
        failures: list[str],
        status_before: str,
        status_after: str,
    ) -> str:
        exam_id = f"exam_{uuid4().hex[:12]}"
        with connect(self.database_url) as connection:
            connection.execute(
                """
                INSERT INTO exams (
                  id, skill_id, evaluator, score, passed, failures,
                  status_before, status_after
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    exam_id,
                    skill_id,
                    evaluator,
                    score,
                    int(passed),
                    encode_json(failures),
                    status_before,
                    status_after,
                ),
            )
        return exam_id


class ReviewRepository:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url
        initialize_database(database_url)

    def create(self, request: ReviewCreate) -> str:
        review_id = f"rev_{uuid4().hex[:12]}"
        with connect(self.database_url) as connection:
            connection.execute(
                """
                INSERT INTO reviews (
                  id, object_type, object_id, decision, reviewer, notes, metadata
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    review_id,
                    request.object_type,
                    request.object_id,
                    request.decision,
                    request.reviewer,
                    request.notes,
                    encode_json(request.metadata),
                ),
            )
        return review_id


def _experience_from_row(row: Any, *, cognition_ids: list[str]) -> ExperienceRead:
    return ExperienceRead(
        id=row["id"],
        agent_id=row["agent_id"],
        domain=row["domain"],
        intent=row["intent"],
        user_input=row["user_input"],
        agent_output=row["agent_output"],
        tools_used=decode_json(row["tools_used"]) or [],
        retrieved_context=decode_json(row["retrieved_context"]) or [],
        feedback=row["feedback"],
        result_status=row["result_status"],
        risk_level=row["risk_level"],
        extraction_status=row["extraction_status"],
        cognition_ids=cognition_ids,
        metadata=decode_json(row["metadata"]) or {},
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _cognition_from_row(row: Any) -> CognitionRead:
    return CognitionRead(
        id=row["id"],
        type=row["type"],
        content=row["content"],
        agent_id=row["agent_id"],
        domain=row["domain"],
        intent=row["intent"],
        confidence=row["confidence"],
        risk_level=row["risk_level"],
        weight=row["weight"],
        status=row["status"],
        evidence_refs=decode_json(row["evidence_refs"]) or [],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _imported_skill_from_row(row: Any) -> ImportedSkill:
    return ImportedSkill(
        id=row["id"],
        name=row["name"],
        status=row["status"],
        agent_id=row["agent_id"],
        domain=row["domain"],
        intent=row["intent"],
        procedure=decode_json(row["procedure"]) or [],
        constraints=decode_json(row["constraints"]) or [],
        evidence_refs=decode_json(row["evidence_refs"]) or [],
        weight=row["weight"],
        confidence=row["confidence"],
    )


def _max_weight(weights: list[str]) -> str:
    if "high" in weights:
        return "high"
    if "medium" in weights:
        return "medium"
    return "low"
