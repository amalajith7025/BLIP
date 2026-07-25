from uuid import UUID

from sqlalchemy.orm import Session

from app.models import Recommendation
from app.schemas import (
    RecommendationCreate,
    RecommendationUpdate,
)


def get_all(db: Session):
    return db.query(Recommendation).all()


def get_by_id(
    db: Session,
    recommendation_id: UUID,
):
    return (
        db.query(Recommendation)
        .filter(
            Recommendation.recommendation_id == recommendation_id
        )
        .first()
    )


def create(
    db: Session,
    recommendation: RecommendationCreate,
):
    db_recommendation = Recommendation(
        **recommendation.model_dump()
    )

    db.add(db_recommendation)
    db.commit()
    db.refresh(db_recommendation)

    return db_recommendation


def update(
    db: Session,
    recommendation_id: UUID,
    recommendation: RecommendationUpdate,
):
    db_recommendation = get_by_id(
        db,
        recommendation_id,
    )

    if not db_recommendation:
        return None

    update_data = recommendation.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(
            db_recommendation,
            key,
            value,
        )

    db.commit()
    db.refresh(db_recommendation)

    return db_recommendation


def delete(
    db: Session,
    recommendation_id: UUID,
):
    db_recommendation = get_by_id(
        db,
        recommendation_id,
    )

    if not db_recommendation:
        return None

    db.delete(db_recommendation)
    db.commit()

    return db_recommendation