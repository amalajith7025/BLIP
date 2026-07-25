from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud import industry as industry_crud
from app.schemas import (
    IndustryCreate,
    IndustryUpdate,
    IndustryResponse,
)

router = APIRouter(
    prefix="/industries",
    tags=["Industries"],
)


@router.get("/", response_model=list[IndustryResponse])
def get_industries(db: Session = Depends(get_db)):
    return industry_crud.get_all(db)


@router.get("/{industry_id}", response_model=IndustryResponse)
def get_industry(
    industry_id: UUID,
    db: Session = Depends(get_db),
):
    industry = industry_crud.get_by_id(db, industry_id)

    if not industry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Industry not found",
        )

    return industry


@router.post(
    "/",
    response_model=IndustryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_industry(
    industry: IndustryCreate,
    db: Session = Depends(get_db),
):
    return industry_crud.create(db, industry)


@router.put("/{industry_id}", response_model=IndustryResponse)
def update_industry(
    industry_id: UUID,
    industry: IndustryUpdate,
    db: Session = Depends(get_db),
):
    updated = industry_crud.update(
        db,
        industry_id,
        industry,
    )

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Industry not found",
        )

    return updated


@router.delete("/{industry_id}", response_model=IndustryResponse)
def delete_industry(
    industry_id: UUID,
    db: Session = Depends(get_db),
):
    deleted = industry_crud.delete(db, industry_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Industry not found",
        )

    return deleted