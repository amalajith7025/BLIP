from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud import business_question
from app.schemas import (
    BusinessQuestionCreate,
    BusinessQuestionUpdate,
    BusinessQuestionResponse,
)

router = APIRouter(
    prefix="/business-questions",
    tags=["Business Questions"],
)


@router.get(
    "/",
    response_model=list[BusinessQuestionResponse],
)
def get_all(
    db: Session = Depends(get_db),
):
    return business_question.get_all(db)


@router.get(
    "/{business_question_id}",
    response_model=BusinessQuestionResponse,
)
def get_by_id(
    business_question_id: UUID,
    db: Session = Depends(get_db),
):
    business_question_obj = business_question.get_by_id(
        db,
        business_question_id,
    )

    if not business_question_obj:
        raise HTTPException(
            status_code=404,
            detail="Business Question not found",
        )

    return business_question_obj


@router.post(
    "/",
    response_model=BusinessQuestionResponse,
    status_code=201,
)
def create(
    business_question_data: BusinessQuestionCreate,
    db: Session = Depends(get_db),
):
    return business_question.create(
        db,
        business_question_data,
    )


@router.put(
    "/{business_question_id}",
    response_model=BusinessQuestionResponse,
)
def update(
    business_question_id: UUID,
    business_question_data: BusinessQuestionUpdate,
    db: Session = Depends(get_db),
):
    updated = business_question.update(
        db,
        business_question_id,
        business_question_data,
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Business Question not found",
        )

    return updated


@router.delete(
    "/{business_question_id}",
    response_model=BusinessQuestionResponse,
)
def delete(
    business_question_id: UUID,
    db: Session = Depends(get_db),
):
    deleted = business_question.delete(
        db,
        business_question_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Business Question not found",
        )

    return deleted