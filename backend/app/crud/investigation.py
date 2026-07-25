from uuid import UUID

from sqlalchemy.orm import Session

from app.models import Investigation
from app.schemas import (
    InvestigationCreate,
    InvestigationUpdate,
)


def get_all(db: Session):
    return db.query(Investigation).all()


def get_by_id(db: Session, investigation_id: UUID):
    return (
        db.query(Investigation)
        .filter(
            Investigation.investigation_id == investigation_id
        )
        .first()
    )


def create(
    db: Session,
    investigation: InvestigationCreate,
):
    db_investigation = Investigation(
        **investigation.model_dump()
    )

    db.add(db_investigation)
    db.commit()
    db.refresh(db_investigation)

    return db_investigation


def update(
    db: Session,
    investigation_id: UUID,
    investigation: InvestigationUpdate,
):
    db_investigation = get_by_id(
        db,
        investigation_id,
    )

    if not db_investigation:
        return None

    update_data = investigation.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(
            db_investigation,
            key,
            value,
        )

    db.commit()
    db.refresh(db_investigation)

    return db_investigation


def delete(
    db: Session,
    investigation_id: UUID,
):
    db_investigation = get_by_id(
        db,
        investigation_id,
    )

    if not db_investigation:
        return None

    db.delete(db_investigation)
    db.commit()

    return db_investigation