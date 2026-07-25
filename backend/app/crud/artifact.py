from uuid import UUID

from sqlalchemy.orm import Session

from app.models import Artifact
from app.schemas import ArtifactCreate, ArtifactUpdate


def get_all(db: Session):
    return db.query(Artifact).all()


def get_by_id(
    db: Session,
    artifact_id: UUID,
):
    return (
        db.query(Artifact)
        .filter(Artifact.artifact_id == artifact_id)
        .first()
    )


def create(
    db: Session,
    artifact: ArtifactCreate,
):
    db_artifact = Artifact(**artifact.model_dump())

    db.add(db_artifact)
    db.commit()
    db.refresh(db_artifact)

    return db_artifact


def update(
    db: Session,
    artifact_id: UUID,
    artifact: ArtifactUpdate,
):
    db_artifact = get_by_id(
        db,
        artifact_id,
    )

    if not db_artifact:
        return None

    update_data = artifact.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(
            db_artifact,
            key,
            value,
        )

    db.commit()
    db.refresh(db_artifact)

    return db_artifact


def delete(
    db: Session,
    artifact_id: UUID,
):
    db_artifact = get_by_id(
        db,
        artifact_id,
    )

    if not db_artifact:
        return None

    db.delete(db_artifact)
    db.commit()

    return db_artifact