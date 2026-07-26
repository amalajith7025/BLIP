from uuid import UUID

from sqlalchemy.orm import Session

from app.models.role import Role


def get_role_by_id(
    db: Session,
    role_id: UUID,
) -> Role | None:
    return (
        db.query(Role)
        .filter(Role.role_id == role_id)
        .first()
    )


def get_role_by_name(
    db: Session,
    role_name: str,
) -> Role | None:
    return (
        db.query(Role)
        .filter(Role.role_name == role_name)
        .first()
    )


def get_all_roles(
    db: Session,
) -> list[Role]:
    return db.query(Role).all()


def create_role(
    db: Session,
    role: Role,
) -> Role:
    db.add(role)
    db.commit()
    db.refresh(role)

    return role


def update_role(
    db: Session,
    role: Role,
) -> Role:
    db.commit()
    db.refresh(role)

    return role


def delete_role(
    db: Session,
    role: Role,
) -> None:
    db.delete(role)
    db.commit()