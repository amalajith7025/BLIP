from uuid import UUID

from sqlalchemy.orm import Session

from app.models import OrganizationUnit
from app.schemas import (
    OrganizationUnitCreate,
    OrganizationUnitUpdate,
)


def get_all(db: Session):
    return db.query(OrganizationUnit).all()


def get_by_id(db: Session, organization_unit_id: UUID):
    return (
        db.query(OrganizationUnit)
        .filter(
            OrganizationUnit.organization_unit_id
            == organization_unit_id
        )
        .first()
    )


def create(
    db: Session,
    organization_unit: OrganizationUnitCreate,
):
    db_organization_unit = OrganizationUnit(
        **organization_unit.model_dump()
    )

    db.add(db_organization_unit)
    db.commit()
    db.refresh(db_organization_unit)

    return db_organization_unit


def update(
    db: Session,
    organization_unit_id: UUID,
    organization_unit: OrganizationUnitUpdate,
):
    db_organization_unit = get_by_id(
        db,
        organization_unit_id,
    )

    if not db_organization_unit:
        return None

    update_data = organization_unit.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(
            db_organization_unit,
            key,
            value,
        )

    db.commit()
    db.refresh(db_organization_unit)

    return db_organization_unit


def delete(
    db: Session,
    organization_unit_id: UUID,
):
    db_organization_unit = get_by_id(
        db,
        organization_unit_id,
    )

    if not db_organization_unit:
        return None

    db.delete(db_organization_unit)
    db.commit()

    return db_organization_unit