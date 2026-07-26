from uuid import UUID

from sqlalchemy.orm import Session

from app.models.membership import Membership


def get_active_for_user(
    db: Session,
    workspace_id: UUID,
    user_id: UUID,
) -> Membership | None:
    return (
        db.query(Membership)
        .filter(
            Membership.workspace_id == workspace_id,
            Membership.user_id == user_id,
            Membership.status == "ACTIVE",
        )
        .first()
    )


def create_owner_membership(
    db: Session,
    workspace_id: UUID,
    user_id: UUID,
) -> Membership:
    membership = Membership(
        workspace_id=workspace_id,
        user_id=user_id,
        role="OWNER",
        status="ACTIVE",
    )
    db.add(membership)
    db.flush()
    return membership
