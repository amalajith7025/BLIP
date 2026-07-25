from uuid import UUID

from sqlalchemy.orm import Session

from app.models import BusinessQuestion
from app.schemas import (
    BusinessQuestionCreate,
    BusinessQuestionUpdate,
)


def get_all(db: Session):
    return db.query(BusinessQuestion).all()


def get_by_id(
    db: Session,
    business_question_id: UUID,
):
    return (
        db.query(BusinessQuestion)
        .filter(
            BusinessQuestion.business_question_id == business_question_id
        )
        .first()
    )


def create(
    db: Session,
    business_question: BusinessQuestionCreate,
):
    db_business_question = BusinessQuestion(
        **business_question.model_dump()
    )

    db.add(db_business_question)
    db.commit()
    db.refresh(db_business_question)

    return db_business_question


def update(
    db: Session,
    business_question_id: UUID,
    business_question: BusinessQuestionUpdate,
):
    db_business_question = get_by_id(
        db,
        business_question_id,
    )

    if not db_business_question:
        return None

    update_data = business_question.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(
            db_business_question,
            key,
            value,
        )

    db.commit()
    db.refresh(db_business_question)

    return db_business_question


def delete(
    db: Session,
    business_question_id: UUID,
):
    db_business_question = get_by_id(
        db,
        business_question_id,
    )

    if not db_business_question:
        return None

    db.delete(db_business_question)
    db.commit()

    return db_business_question