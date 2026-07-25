from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud import artifact
from app.schemas import (
    ArtifactCreate,
    ArtifactUpdate,
    ArtifactResponse,
)

router = APIRouter(
    prefix="/artifacts",
    tags=["Artifacts"],
)


@router.get(
    "/",
    response_model=list[ArtifactResponse],
)
def get_all(
    db: Session = Depends(get_db),
):
    return artifact.get_all(db)


@router.get(
    "/{artifact_id}",
    response_model=ArtifactResponse,
)
def get_by_id(
    artifact_id: UUID,
    db: Session = Depends(get_db),
):
    artifact_obj = artifact.get_by_id(
        db,
        artifact_id,
    )

    if not artifact_obj:
        raise HTTPException(
            status_code=404,
            detail="Artifact not found",
        )

    return artifact_obj


@router.post(
    "/",
    response_model=ArtifactResponse,
    status_code=201,
)
def create(
    artifact_data: ArtifactCreate,
    db: Session = Depends(get_db),
):
    return artifact.create(
        db,
        artifact_data,
    )


@router.put(
    "/{artifact_id}",
    response_model=ArtifactResponse,
)
def update(
    artifact_id: UUID,
    artifact_data: ArtifactUpdate,
    db: Session = Depends(get_db),
):
    updated = artifact.update(
        db,
        artifact_id,
        artifact_data,
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Artifact not found",
        )

    return updated


@router.delete(
    "/{artifact_id}",
    response_model=ArtifactResponse,
)
def delete(
    artifact_id: UUID,
    db: Session = Depends(get_db),
):
    deleted = artifact.delete(
        db,
        artifact_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Artifact not found",
        )

    return deleted