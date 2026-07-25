from uuid import UUID

from sqlalchemy.orm import Session

from app.models import Fact
from app.schemas import FactCreate, FactUpdate


def get_all(db: Session):
    return db.query(Fact).all()


def get_by_id(
    db: Session,
    fact_id: UUID,
):
    return (
        db.query(Fact)
        .filter(Fact.fact_id == fact_id)
        .first()
    )


def create(
    db: Session,
    fact: FactCreate,
):
    db_fact = Fact(**fact.model_dump())

    db.add(db_fact)
    db.commit()
    db.refresh(db_fact)

    return db_fact


def update(
    db: Session,
    fact_id: UUID,
    fact: FactUpdate,
):
    db_fact = get_by_id(
        db,
        fact_id,
    )

    if not db_fact:
        return None

    update_data = fact.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(
            db_fact,
            key,
            value,
        )

    db.commit()
    db.refresh(db_fact)

    return db_fact


def delete(
    db: Session,
    fact_id: UUID,
):
    db_fact = get_by_id(
        db,
        fact_id,
    )

    if not db_fact:
        return None

    db.delete(db_fact)
    db.commit()

    return db_fact