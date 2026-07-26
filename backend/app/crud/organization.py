from uuid import UUID

from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.schemas.organization import OrganizationCreate, OrganizationUpdate


def get_all(db: Session):
    return db.query(Organization).all()


def get_by_id(db: Session, organization_id: UUID):
    return (
        db.query(Organization)
        .filter(Organization.organization_id == organization_id)
        .first()
    )


def get_by_name(db: Session, name: str):
    return (
        db.query(Organization)
        .filter(Organization.name == name)
        .first()
    )


def create(db: Session, organization: OrganizationCreate):
    db_organization = Organization(**organization.model_dump())

    db.add(db_organization)
    db.commit()
    db.refresh(db_organization)

    return db_organization


def update(db: Session, organization_id: UUID, organization: OrganizationUpdate):
    db_organization = get_by_id(db, organization_id)

    if not db_organization:
        return None

    update_data = organization.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_organization, key, value)

    db.commit()
    db.refresh(db_organization)

    return db_organization


def update_status(db: Session, organization_id: UUID, status: str):
    db_organization = get_by_id(db, organization_id)

    if not db_organization:
        return None

    db_organization.status = status
    db.commit()
    db.refresh(db_organization)

    return db_organization
