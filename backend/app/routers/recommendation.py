from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud import recommendation
from app.schemas import (
    RecommendationCreate,
    RecommendationUpdate,
    RecommendationResponse,
)

router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"],
)


@router.get(
    "/",
    response_model=list[RecommendationResponse],
)
def get_all(
    db: Session = Depends(get_db),
):
    return recommendation.get_all(db)


@router.get(
    "/{recommendation_id}",
    response_model=RecommendationResponse,
)
def get_by_id(
    recommendation_id: UUID,
    db: Session = Depends(get_db),
):
    db_recommendation = recommendation.get_by_id(
        db,
        recommendation_id,
    )

    if not db_recommendation:
        raise HTTPException(
            status_code=404,
            detail="Recommendation not found",
        )

    return db_recommendation


@router.post(
    "/",
    response_model=RecommendationResponse,
    status_code=201,
)
def create(
    recommendation_data: RecommendationCreate,
    db: Session = Depends(get_db),
):
    return recommendation.create(
        db,
        recommendation_data,
    )


@router.put(
    "/{recommendation_id}",
    response_model=RecommendationResponse,
)
def update(
    recommendation_id: UUID,
    recommendation_data: RecommendationUpdate,
    db: Session = Depends(get_db),
):
    updated = recommendation.update(
        db,
        recommendation_id,
        recommendation_data,
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Recommendation not found",
        )

    return updated


@router.delete(
    "/{recommendation_id}",
    response_model=RecommendationResponse,
)
def delete(
    recommendation_id: UUID,
    db: Session = Depends(get_db),
):
    deleted = recommendation.delete(
        db,
        recommendation_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Recommendation not found",
        )

    return deleted