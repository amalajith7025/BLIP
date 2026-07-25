from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud import fact
from app.schemas import (
    FactCreate,
    FactUpdate,
    FactResponse,
)

router = APIRouter(
    prefix="/facts",
    tags=["Facts"],
)


@router.get(
    "/",
    response_model=list[FactResponse],
)
def get_all(
    db: Session = Depends(get_db),
):
    return fact.get_all(db)


@router.get(
    "/{fact_id}",
    response_model=FactResponse,
)
def get_by_id(
    fact_id: UUID,
    db: Session = Depends(get_db),
):
    fact_obj = fact.get_by_id(
        db,
        fact_id,
    )

    if not fact_obj:
        raise HTTPException(
            status_code=404,
            detail="Fact not found",
        )

    return fact_obj


@router.post(
    "/",
    response_model=FactResponse,
    status_code=201,
)
def create(
    fact_data: FactCreate,
    db: Session = Depends(get_db),
):
    return fact.create(
        db,
        fact_data,
    )


@router.put(
    "/{fact_id}",
    response_model=FactResponse,
)
def update(
    fact_id: UUID,
    fact_data: FactUpdate,
    db: Session = Depends(get_db),
):
    updated = fact.update(
        db,
        fact_id,
        fact_data,
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Fact not found",
        )

    return updated


@router.delete(
    "/{fact_id}",
    response_model=FactResponse,
)
def delete(
    fact_id: UUID,
    db: Session = Depends(get_db),
):
    deleted = fact.delete(
        db,
        fact_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Fact not found",
        )

    return deleted