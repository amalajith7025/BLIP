from uuid import UUID

from sqlalchemy.orm import Session

from app.models.membership import Membership
from app.models.workspace import Workspace
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate


def get_by_id(db: Session, workspace_id: UUID) -> Workspace | None:
    return (
        db.query(Workspace)
        .filter(Workspace.workspace_id == workspace_id)
        .first()
    )


def get_by_slug(db: Session, slug: str) -> Workspace | None:
    return db.query(Workspace).filter(Workspace.slug == slug).first()


def list_for_user(db: Session, user_id: UUID) -> list[Workspace]:
    return (
        db.query(Workspace)
        .join(Membership)
        .filter(
            Membership.user_id == user_id,
            Membership.status == "ACTIVE",
        )
        .all()
    )


def create(
    db: Session,
    workspace: WorkspaceCreate,
    owner_id: UUID,
) -> Workspace:
    db_workspace = Workspace(
        **workspace.model_dump(),
        owner_id=owner_id,
    )
    db.add(db_workspace)
    db.flush()
    return db_workspace


def update(
    db: Session,
    workspace: Workspace,
    workspace_data: WorkspaceUpdate,
) -> Workspace:
    for key, value in workspace_data.model_dump(exclude_unset=True).items():
        setattr(workspace, key, value)
    db.flush()
    return workspace


def delete(db: Session, workspace: Workspace) -> None:
    db.delete(workspace)
    db.flush()
