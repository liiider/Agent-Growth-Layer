from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from server.config import Settings, get_settings
from server.models.cognition import CognitionRead, CognitionStatusUpdate
from server.storage.repositories import CognitionRepository

router = APIRouter(prefix="/v1/cognitions", tags=["cognitions"])


def get_cognition_repository(
    settings: Annotated[Settings, Depends(get_settings)],
) -> CognitionRepository:
    return CognitionRepository(settings.database_url)


@router.get("", response_model=list[CognitionRead])
def list_cognitions(
    repository: Annotated[CognitionRepository, Depends(get_cognition_repository)],
    agent_id: str | None = None,
    domain: str | None = None,
    intent: str | None = None,
    status: str | None = None,
    limit: int = Query(default=50, ge=1, le=100),
) -> list[CognitionRead]:
    return repository.list(
        agent_id=agent_id,
        domain=domain,
        intent=intent,
        status=status,
        limit=limit,
    )


@router.get("/{cognition_id}", response_model=CognitionRead)
def get_cognition(
    cognition_id: str,
    repository: Annotated[CognitionRepository, Depends(get_cognition_repository)],
) -> CognitionRead:
    cognition = repository.get(cognition_id)
    if cognition is None:
        raise HTTPException(status_code=404, detail="Cognition not found.")
    return cognition


@router.patch("/{cognition_id}/status", response_model=CognitionRead)
def update_cognition_status(
    cognition_id: str,
    request: CognitionStatusUpdate,
    repository: Annotated[CognitionRepository, Depends(get_cognition_repository)],
) -> CognitionRead:
    cognition = repository.update_status(cognition_id, request.status)
    if cognition is None:
        raise HTTPException(status_code=404, detail="Cognition not found.")
    return cognition
