from uuid import UUID

from sqlalchemy.orm import Session

from app.models import HypothesisEvidence
from app.schemas import (
    HypothesisEvidenceCreate,
    HypothesisEvidenceUpdate,
)


def get_all(db: Session):
    return db.query(HypothesisEvidence).all()


def get_by_id(
    db: Session,
    hypothesis_evidence_id: UUID,
):
    return (
        db.query(HypothesisEvidence)
        .filter(
            HypothesisEvidence.hypothesis_evidence_id
            == hypothesis_evidence_id
        )
        .first()
    )


def create(
    db: Session,
    hypothesis_evidence: HypothesisEvidenceCreate,
):
    db_hypothesis_evidence = HypothesisEvidence(
        **hypothesis_evidence.model_dump()
    )

    db.add(db_hypothesis_evidence)
    db.commit()
    db.refresh(db_hypothesis_evidence)

    return db_hypothesis_evidence


def update(
    db: Session,
    hypothesis_evidence_id: UUID,
    hypothesis_evidence: HypothesisEvidenceUpdate,
):
    db_hypothesis_evidence = get_by_id(
        db,
        hypothesis_evidence_id,
    )

    if not db_hypothesis_evidence:
        return None

    update_data = hypothesis_evidence.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(
            db_hypothesis_evidence,
            key,
            value,
        )

    db.commit()
    db.refresh(db_hypothesis_evidence)

    return db_hypothesis_evidence


def delete(
    db: Session,
    hypothesis_evidence_id: UUID,
):
    db_hypothesis_evidence = get_by_id(
        db,
        hypothesis_evidence_id,
    )

    if not db_hypothesis_evidence:
        return None

    db.delete(db_hypothesis_evidence)
    db.commit()

    return db_hypothesis_evidence