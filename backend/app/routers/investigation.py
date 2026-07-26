from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.permissions import (
    authorize_investigation_access,
    require_authenticated_user_dependency,
)
from app.core.database import get_db
from app.crud import investigation
from app.models.user import User
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
    current_user: User = Depends(require_authenticated_user_dependency),
):
    investigations = investigation.get_all(db)
    return [
        item
        for item in investigations
        if item.organization_id == current_user.organization_id
    ]


@router.get(
    "/{investigation_id}",
    response_model=InvestigationResponse,
)
def get_by_id(
    investigation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user_dependency),
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

    authorize_investigation_access(db, current_user, investigation_id)

    return investigation_obj


@router.post(
    "/",
    response_model=InvestigationResponse,
    status_code=201,
)
def create(
    investigation_data: InvestigationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user_dependency),
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
    current_user: User = Depends(require_authenticated_user_dependency),
):
    existing = investigation.get_by_id(db, investigation_id)

    if not existing:
        raise HTTPException(
            status_code=404,
            detail="Investigation not found",
        )

    authorize_investigation_access(db, current_user, investigation_id)

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
    current_user: User = Depends(require_authenticated_user_dependency),
):
    existing = investigation.get_by_id(db, investigation_id)

    if not existing:
        raise HTTPException(
            status_code=404,
            detail="Investigation not found",
        )

    authorize_investigation_access(db, current_user, investigation_id)

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