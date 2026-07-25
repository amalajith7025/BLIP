from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud import organization as organization_crud
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
)

router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
)


@router.get("/", response_model=list[OrganizationResponse])
def get_organizations(db: Session = Depends(get_db)):
    return organization_crud.get_all(db)


@router.get("/{organization_id}", response_model=OrganizationResponse)
def get_organization(organization_id: UUID, db: Session = Depends(get_db)):
    organization = organization_crud.get_by_id(db, organization_id)

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
    return organization_crud.create(db, organization)


@router.put("/{organization_id}", response_model=OrganizationResponse)
def update_organization(
    organization_id: UUID,
    organization: OrganizationUpdate,
    db: Session = Depends(get_db),
):
    updated = organization_crud.update(db, organization_id, organization)

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    return updated


@router.delete("/{organization_id}")
def delete_organization(
    organization_id: UUID,
    db: Session = Depends(get_db),
):
    deleted = organization_crud.delete(db, organization_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    return {"message": "Organization deleted successfully"}