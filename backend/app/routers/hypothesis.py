from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud import hypothesis
from app.schemas import (
    HypothesisCreate,
    HypothesisUpdate,
    HypothesisResponse,
)

router = APIRouter(
    prefix="/hypotheses",
    tags=["Hypotheses"],
)


@router.get(
    "/",
    response_model=list[HypothesisResponse],
)
def get_all(
    db: Session = Depends(get_db),
):
    return hypothesis.get_all(db)


@router.get(
    "/{hypothesis_id}",
    response_model=HypothesisResponse,
)
def get_by_id(
    hypothesis_id: UUID,
    db: Session = Depends(get_db),
):
    db_hypothesis = hypothesis.get_by_id(
        db,
        hypothesis_id,
    )

    if not db_hypothesis:
        raise HTTPException(
            status_code=404,
            detail="Hypothesis not found",
        )

    return db_hypothesis


@router.post(
    "/",
    response_model=HypothesisResponse,
    status_code=201,
)
def create(
    hypothesis_data: HypothesisCreate,
    db: Session = Depends(get_db),
):
    return hypothesis.create(
        db,
        hypothesis_data,
    )


@router.put(
    "/{hypothesis_id}",
    response_model=HypothesisResponse,
)
def update(
    hypothesis_id: UUID,
    hypothesis_data: HypothesisUpdate,
    db: Session = Depends(get_db),
):
    updated = hypothesis.update(
        db,
        hypothesis_id,
        hypothesis_data,
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Hypothesis not found",
        )

    return updated


@router.delete(
    "/{hypothesis_id}",
    response_model=HypothesisResponse,
)
def delete(
    hypothesis_id: UUID,
    db: Session = Depends(get_db),
):
    deleted = hypothesis.delete(
        db,
        hypothesis_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Hypothesis not found",
        )

    return deleted