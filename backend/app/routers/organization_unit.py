from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.permissions import (
    authorize_organization_access,
    require_authenticated_user_dependency,
)
from app.core.database import get_db
from app.crud import organization_unit
from app.models.user import User
from app.schemas import (
    OrganizationUnitCreate,
    OrganizationUnitUpdate,
    OrganizationUnitResponse,
)

router = APIRouter(
    prefix="/organization-units",
    tags=["Organization Units"],
)


@router.get(
    "/",
    response_model=list[OrganizationUnitResponse],
)
def get_all(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user_dependency),
):
    organization_units = organization_unit.get_all(db)
    return [
        item
        for item in organization_units
        if item.organization_id == current_user.organization_id
    ]


@router.get(
    "/{organization_unit_id}",
    response_model=OrganizationUnitResponse,
)
def get_by_id(
    organization_unit_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user_dependency),
):
    organization_unit_obj = organization_unit.get_by_id(
        db,
        organization_unit_id,
    )

    if not organization_unit_obj:
        raise HTTPException(
            status_code=404,
            detail="Organization Unit not found",
        )

    authorize_organization_access(
        db,
        current_user,
        organization_unit_obj.organization_id,
    )

    return organization_unit_obj


@router.post(
    "/",
    response_model=OrganizationUnitResponse,
    status_code=201,
)
def create(
    organization_unit_data: OrganizationUnitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user_dependency),
):
    authorize_organization_access(
        db,
        current_user,
        organization_unit_data.organization_id,
    )

    return organization_unit.create(
        db,
        organization_unit_data,
    )


@router.put(
    "/{organization_unit_id}",
    response_model=OrganizationUnitResponse,
)
def update(
    organization_unit_id: UUID,
    organization_unit_data: OrganizationUnitUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user_dependency),
):
    existing = organization_unit.get_by_id(db, organization_unit_id)

    if not existing:
        raise HTTPException(
            status_code=404,
            detail="Organization Unit not found",
        )

    authorize_organization_access(
        db,
        current_user,
        existing.organization_id,
    )

    updated = organization_unit.update(
        db,
        organization_unit_id,
        organization_unit_data,
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Organization Unit not found",
        )

    return updated


@router.delete(
    "/{organization_unit_id}",
    response_model=OrganizationUnitResponse,
)
def delete(
    organization_unit_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user_dependency),
):
    existing = organization_unit.get_by_id(db, organization_unit_id)

    if not existing:
        raise HTTPException(
            status_code=404,
            detail="Organization Unit not found",
        )

    authorize_organization_access(
        db,
        current_user,
        existing.organization_id,
    )

    deleted = organization_unit.delete(
        db,
        organization_unit_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Organization Unit not found",
        )

    return deleted