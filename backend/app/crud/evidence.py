from uuid import UUID

from sqlalchemy.orm import Session

from app.models import Evidence
from app.schemas import EvidenceCreate, EvidenceUpdate


def get_all(db: Session):
    return db.query(Evidence).all()


def get_by_id(
    db: Session,
    evidence_id: UUID,
):
    return (
        db.query(Evidence)
        .filter(Evidence.evidence_id == evidence_id)
        .first()
    )


def create(
    db: Session,
    evidence: EvidenceCreate,
):
    db_evidence = Evidence(**evidence.model_dump())

    db.add(db_evidence)
    db.commit()
    db.refresh(db_evidence)

    return db_evidence


def update(
    db: Session,
    evidence_id: UUID,
    evidence: EvidenceUpdate,
):
    db_evidence = get_by_id(
        db,
        evidence_id,
    )

    if not db_evidence:
        return None

    update_data = evidence.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(
            db_evidence,
            key,
            value,
        )

    db.commit()
    db.refresh(db_evidence)

    return db_evidence


def delete(
    db: Session,
    evidence_id: UUID,
):
    db_evidence = get_by_id(
        db,
        evidence_id,
    )

    if not db_evidence:
        return None

    db.delete(db_evidence)
    db.commit()

    return db_evidence