from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud import finding
from app.schemas import (
    FindingCreate,
    FindingUpdate,
    FindingResponse,
)

router = APIRouter(
    prefix="/findings",
    tags=["Findings"],
)


@router.get(
    "/",
    response_model=list[FindingResponse],
)
def get_all(
    db: Session = Depends(get_db),
):
    return finding.get_all(db)


@router.get(
    "/{finding_id}",
    response_model=FindingResponse,
)
def get_by_id(
    finding_id: UUID,
    db: Session = Depends(get_db),
):
    db_finding = finding.get_by_id(
        db,
        finding_id,
    )

    if not db_finding:
        raise HTTPException(
            status_code=404,
            detail="Finding not found",
        )

    return db_finding


@router.post(
    "/",
    response_model=FindingResponse,
    status_code=201,
)
def create(
    finding_data: FindingCreate,
    db: Session = Depends(get_db),
):
    return finding.create(
        db,
        finding_data,
    )


@router.put(
    "/{finding_id}",
    response_model=FindingResponse,
)
def update(
    finding_id: UUID,
    finding_data: FindingUpdate,
    db: Session = Depends(get_db),
):
    updated = finding.update(
        db,
        finding_id,
        finding_data,
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Finding not found",
        )

    return updated


@router.delete(
    "/{finding_id}",
    response_model=FindingResponse,
)
def delete(
    finding_id: UUID,
    db: Session = Depends(get_db),
):
    deleted = finding.delete(
        db,
        finding_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Finding not found",
        )

    return deleted