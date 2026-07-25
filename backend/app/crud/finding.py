from uuid import UUID

from sqlalchemy.orm import Session

from app.models import Finding
from app.schemas import (
    FindingCreate,
    FindingUpdate,
)


def get_all(db: Session):
    return db.query(Finding).all()


def get_by_id(
    db: Session,
    finding_id: UUID,
):
    return (
        db.query(Finding)
        .filter(
            Finding.finding_id == finding_id
        )
        .first()
    )


def create(
    db: Session,
    finding: FindingCreate,
):
    db_finding = Finding(
        **finding.model_dump()
    )

    db.add(db_finding)
    db.commit()
    db.refresh(db_finding)

    return db_finding


def update(
    db: Session,
    finding_id: UUID,
    finding: FindingUpdate,
):
    db_finding = get_by_id(
        db,
        finding_id,
    )

    if not db_finding:
        return None

    update_data = finding.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(
            db_finding,
            key,
            value,
        )

    db.commit()
    db.refresh(db_finding)

    return db_finding


def delete(
    db: Session,
    finding_id: UUID,
):
    db_finding = get_by_id(
        db,
        finding_id,
    )

    if not db_finding:
        return None

    db.delete(db_finding)
    db.commit()

    return db_finding