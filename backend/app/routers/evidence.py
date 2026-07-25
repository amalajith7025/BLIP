from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud import evidence
from app.schemas import (
    EvidenceCreate,
    EvidenceUpdate,
    EvidenceResponse,
)

router = APIRouter(
    prefix="/evidence",
    tags=["Evidence"],
)


@router.get(
    "/",
    response_model=list[EvidenceResponse],
)
def get_all(
    db: Session = Depends(get_db),
):
    return evidence.get_all(db)


@router.get(
    "/{evidence_id}",
    response_model=EvidenceResponse,
)
def get_by_id(
    evidence_id: UUID,
    db: Session = Depends(get_db),
):
    evidence_obj = evidence.get_by_id(
        db,
        evidence_id,
    )

    if not evidence_obj:
        raise HTTPException(
            status_code=404,
            detail="Evidence not found",
        )

    return evidence_obj


@router.post(
    "/",
    response_model=EvidenceResponse,
    status_code=201,
)
def create(
    evidence_data: EvidenceCreate,
    db: Session = Depends(get_db),
):
    return evidence.create(
        db,
        evidence_data,
    )


@router.put(
    "/{evidence_id}",
    response_model=EvidenceResponse,
)
def update(
    evidence_id: UUID,
    evidence_data: EvidenceUpdate,
    db: Session = Depends(get_db),
):
    updated = evidence.update(
        db,
        evidence_id,
        evidence_data,
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Evidence not found",
        )

    return updated


@router.delete(
    "/{evidence_id}",
    response_model=EvidenceResponse,
)
def delete(
    evidence_id: UUID,
    db: Session = Depends(get_db),
):
    deleted = evidence.delete(
        db,
        evidence_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Evidence not found",
        )

    return deleted