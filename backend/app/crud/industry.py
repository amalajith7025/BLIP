from uuid import UUID

from sqlalchemy.orm import Session

from app.models.industry import Industry
from app.schemas.industry import (
    IndustryCreate,
    IndustryUpdate,
)


def get_all(db: Session):
    return db.query(Industry).all()


def get_by_id(db: Session, industry_id: UUID):
    return (
        db.query(Industry)
        .filter(Industry.industry_id == industry_id)
        .first()
    )


def create(db: Session, industry: IndustryCreate):
    db_industry = Industry(**industry.model_dump())

    db.add(db_industry)
    db.commit()
    db.refresh(db_industry)

    return db_industry


def update(
    db: Session,
    industry_id: UUID,
    industry: IndustryUpdate,
):
    db_industry = get_by_id(db, industry_id)

    if not db_industry:
        return None

    update_data = industry.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_industry, key, value)

    db.commit()
    db.refresh(db_industry)

    return db_industry


def delete(db: Session, industry_id: UUID):
    db_industry = get_by_id(db, industry_id)

    if not db_industry:
        return None

    db.delete(db_industry)
    db.commit()

    return db_industry