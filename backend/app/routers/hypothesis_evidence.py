from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud import hypothesis_evidence
from app.schemas import (
    HypothesisEvidenceCreate,
    HypothesisEvidenceUpdate,
    HypothesisEvidenceResponse,
)

router = APIRouter(
    prefix="/hypothesis-evidence",
    tags=["Hypothesis Evidence"],
)


@router.get(
    "/",
    response_model=list[HypothesisEvidenceResponse],
)
def get_all(
    db: Session = Depends(get_db),
):
    return hypothesis_evidence.get_all(db)


@router.get(
    "/{hypothesis_evidence_id}",
    response_model=HypothesisEvidenceResponse,
)
def get_by_id(
    hypothesis_evidence_id: UUID,
    db: Session = Depends(get_db),
):
    db_hypothesis_evidence = hypothesis_evidence.get_by_id(
        db,
        hypothesis_evidence_id,
    )

    if not db_hypothesis_evidence:
        raise HTTPException(
            status_code=404,
            detail="Hypothesis Evidence not found",
        )

    return db_hypothesis_evidence


@router.post(
    "/",
    response_model=HypothesisEvidenceResponse,
    status_code=201,
)
def create(
    hypothesis_evidence_data: HypothesisEvidenceCreate,
    db: Session = Depends(get_db),
):
    return hypothesis_evidence.create(
        db,
        hypothesis_evidence_data,
    )


@router.put(
    "/{hypothesis_evidence_id}",
    response_model=HypothesisEvidenceResponse,
)
def update(
    hypothesis_evidence_id: UUID,
    hypothesis_evidence_data: HypothesisEvidenceUpdate,
    db: Session = Depends(get_db),
):
    updated = hypothesis_evidence.update(
        db,
        hypothesis_evidence_id,
        hypothesis_evidence_data,
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Hypothesis Evidence not found",
        )

    return updated


@router.delete(
    "/{hypothesis_evidence_id}",
    response_model=HypothesisEvidenceResponse,
)
def delete(
    hypothesis_evidence_id: UUID,
    db: Session = Depends(get_db),
):
    deleted = hypothesis_evidence.delete(
        db,
        hypothesis_evidence_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Hypothesis Evidence not found",
        )

    return deleted