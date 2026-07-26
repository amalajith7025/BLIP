from uuid import UUID

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate


def create_user(
    db: Session,
    user: UserCreate,
    hashed_password: str,
) -> User:
    db_user = User(
        organization_id=user.organization_id,
        role_id=user.role_id,
        email=user.email,
        password_hash=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=True,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def get_user_by_id(
    db: Session,
    user_id: UUID,
) -> User | None:
    return (
        db.query(User)
        .filter(User.user_id == user_id)
        .first()
    )


def get_user_by_email(
    db: Session,
    email: str,
) -> User | None:
    return (
        db.query(User)
        .filter(User.email == email)
        .first()
    )


def update_user(
    db: Session,
    db_user: User,
) -> User:
    db.commit()
    db.refresh(db_user)

    return db_user


def delete_user(
    db: Session,
    db_user: User,
) -> None:
    db.delete(db_user)
    db.commit()