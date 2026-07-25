from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud import investigation
from app.schemas import (
    InvestigationCreate,
    InvestigationUpdate,
    InvestigationResponse,
)

router = APIRouter(
    prefix="/investigations",
    tags=["Investigations"],
)


@router.get(
    "/",
    response_model=list[InvestigationResponse],
)
def get_all(
    db: Session = Depends(get_db),
):
    return investigation.get_all(db)


@router.get(
    "/{investigation_id}",
    response_model=InvestigationResponse,
)
def get_by_id(
    investigation_id: UUID,
    db: Session = Depends(get_db),
):
    investigation_obj = investigation.get_by_id(
        db,
        investigation_id,
    )

    if not investigation_obj:
        raise HTTPException(
            status_code=404,
            detail="Investigation not found",
        )

    return investigation_obj


@router.post(
    "/",
    response_model=InvestigationResponse,
    status_code=201,
)
def create(
    investigation_data: InvestigationCreate,
    db: Session = Depends(get_db),
):
    return investigation.create(
        db,
        investigation_data,
    )


@router.put(
    "/{investigation_id}",
    response_model=InvestigationResponse,
)
def update(
    investigation_id: UUID,
    investigation_data: InvestigationUpdate,
    db: Session = Depends(get_db),
):
    updated = investigation.update(
        db,
        investigation_id,
        investigation_data,
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Investigation not found",
        )

    return updated


@router.delete(
    "/{investigation_id}",
    response_model=InvestigationResponse,
)
def delete(
    investigation_id: UUID,
    db: Session = Depends(get_db),
):
    deleted = investigation.delete(
        db,
        investigation_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Investigation not found",
        )

    return deleted