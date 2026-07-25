from uuid import UUID

from sqlalchemy.orm import Session

from app.models import Hypothesis
from app.schemas import (
    HypothesisCreate,
    HypothesisUpdate,
)


def get_all(db: Session):
    return db.query(Hypothesis).all()


def get_by_id(
    db: Session,
    hypothesis_id: UUID,
):
    return (
        db.query(Hypothesis)
        .filter(
            Hypothesis.hypothesis_id == hypothesis_id
        )
        .first()
    )


def create(
    db: Session,
    hypothesis: HypothesisCreate,
):
    db_hypothesis = Hypothesis(
        **hypothesis.model_dump()
    )

    db.add(db_hypothesis)
    db.commit()
    db.refresh(db_hypothesis)

    return db_hypothesis


def update(
    db: Session,
    hypothesis_id: UUID,
    hypothesis: HypothesisUpdate,
):
    db_hypothesis = get_by_id(
        db,
        hypothesis_id,
    )

    if not db_hypothesis:
        return None

    update_data = hypothesis.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(
            db_hypothesis,
            key,
            value,
        )

    db.commit()
    db.refresh(db_hypothesis)

    return db_hypothesis


def delete(
    db: Session,
    hypothesis_id: UUID,
):
    db_hypothesis = get_by_id(
        db,
        hypothesis_id,
    )

    if not db_hypothesis:
        return None

    db.delete(db_hypothesis)
    db.commit()

    return db_hypothesis