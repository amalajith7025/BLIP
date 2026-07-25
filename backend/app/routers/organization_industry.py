from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud import organization_industry as organization_industry_crud
from app.schemas import (
    OrganizationIndustryCreate,
    OrganizationIndustryUpdate,
    OrganizationIndustryResponse,
)

router = APIRouter(
    prefix="/organization-industries",
    tags=["Organization Industries"],
)


@router.get(
    "/",
    response_model=list[OrganizationIndustryResponse],
)
def get_organization_industries(db: Session = Depends(get_db)):
    return organization_industry_crud.get_all(db)


@router.get(
    "/{organization_industry_id}",
    response_model=OrganizationIndustryResponse,
)
def get_organization_industry(
    organization_industry_id: UUID,
    db: Session = Depends(get_db),
):
    organization_industry = organization_industry_crud.get_by_id(
        db,
        organization_industry_id,
    )

    if not organization_industry:
        raise HTTPException(
            status_code=404,
            detail="OrganizationIndustry not found",
        )

    return organization_industry


@router.post(
    "/",
    response_model=OrganizationIndustryResponse,
    status_code=201,
)
def create_organization_industry(
    organization_industry: OrganizationIndustryCreate,
    db: Session = Depends(get_db),
):
    return organization_industry_crud.create(
        db,
        organization_industry,
    )


@router.put(
    "/{organization_industry_id}",
    response_model=OrganizationIndustryResponse,
)
def update_organization_industry(
    organization_industry_id: UUID,
    organization_industry: OrganizationIndustryUpdate,
    db: Session = Depends(get_db),
):
    updated = organization_industry_crud.update(
        db,
        organization_industry_id,
        organization_industry,
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="OrganizationIndustry not found",
        )

    return updated


@router.delete(
    "/{organization_industry_id}",
    response_model=OrganizationIndustryResponse,
)
def delete_organization_industry(
    organization_industry_id: UUID,
    db: Session = Depends(get_db),
):
    deleted = organization_industry_crud.delete(
        db,
        organization_industry_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="OrganizationIndustry not found",
        )

    return deleted