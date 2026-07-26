from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
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
def get_organizations(db: Session = Depends(get_db)):
    return OrganizationService.list_organizations(db)


@router.get("/{organization_id}", response_model=OrganizationResponse)
def get_organization(organization_id: UUID, db: Session = Depends(get_db)):
    organization = OrganizationService.get_organization(db, organization_id)

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
):
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
):
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
