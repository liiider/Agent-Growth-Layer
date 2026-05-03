from typing import Any
from uuid import uuid4

from server.models.cognition import CognitionCandidate, CognitionRead
from server.models.experience import ExperienceCreate, ExperienceRead
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
