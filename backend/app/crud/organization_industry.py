from uuid import UUID

from sqlalchemy.orm import Session

from app.models import OrganizationIndustry
from app.schemas import (
    OrganizationIndustryCreate,
    OrganizationIndustryUpdate,
)


def get_all(db: Session):
    return db.query(OrganizationIndustry).all()


def get_by_id(db: Session, organization_industry_id: UUID):
    return (
        db.query(OrganizationIndustry)
        .filter(
            OrganizationIndustry.organization_industry_id
            == organization_industry_id
        )
        .first()
    )


def create(
    db: Session,
    organization_industry: OrganizationIndustryCreate,
):
    db_organization_industry = OrganizationIndustry(
        **organization_industry.model_dump()
    )

    db.add(db_organization_industry)
    db.commit()
    db.refresh(db_organization_industry)

    return db_organization_industry


def update(
    db: Session,
    organization_industry_id: UUID,
    organization_industry: OrganizationIndustryUpdate,
):
    db_organization_industry = get_by_id(
        db,
        organization_industry_id,
    )

    if not db_organization_industry:
        return None

    update_data = organization_industry.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(db_organization_industry, key, value)

    db.commit()
    db.refresh(db_organization_industry)

    return db_organization_industry


def delete(
    db: Session,
    organization_industry_id: UUID,
):
    db_organization_industry = get_by_id(
        db,
        organization_industry_id,
    )

    if not db_organization_industry:
        return None

    db.delete(db_organization_industry)
    db.commit()

    return db_organization_industry