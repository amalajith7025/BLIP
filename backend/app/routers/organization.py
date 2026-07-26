from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.permissions import (
    authorize_organization_access,
    require_authenticated_user_dependency,
    require_organization_member_dependency,
)
from app.core.database import get_db
from app.models.user import User
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationResponse,
    OrganizationStatusUpdate,
    OrganizationUpdate,
)
from app.services.organization import OrganizationService

router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
)


@router.get("/", response_model=list[OrganizationResponse])
def get_organizations(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user_dependency),
):
    return OrganizationService.list_organizations(db, current_user)


@router.get("/{organization_id}", response_model=OrganizationResponse)
def get_organization(
    organization_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_organization_member_dependency),
):
    organization = authorize_organization_access(db, current_user, organization_id)

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    return organization


@router.post(
    "/",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_organization(
    organization: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user_dependency),
):
    try:
        return OrganizationService.create_organization(db, organization)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )


@router.put("/{organization_id}", response_model=OrganizationResponse)
def update_organization(
    organization_id: UUID,
    organization: OrganizationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user_dependency),
):
    authorize_organization_access(db, current_user, organization_id)

    try:
        updated = OrganizationService.update_organization(
            db,
            organization_id,
            organization,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    return updated


@router.patch("/{organization_id}/status", response_model=OrganizationResponse)
def update_organization_status(
    organization_id: UUID,
    organization_status: OrganizationStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user_dependency),
):
    authorize_organization_access(db, current_user, organization_id)

    updated = OrganizationService.update_organization_status(
        db,
        organization_id,
        organization_status.status,
    )

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    return updated
