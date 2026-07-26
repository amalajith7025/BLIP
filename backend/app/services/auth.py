from sqlalchemy.orm import Session

from app.auth.jwt import create_access_token
from app.auth.security import hash_password, verify_password
from app.crud.user import (
    create_user,
    get_user_by_email,
)
from app.models.user import User
from app.schemas.user import UserCreate


class AuthService:

    @staticmethod
    def register_user(
        db: Session,
        user: UserCreate,
    ) -> User:
        existing_user = get_user_by_email(
            db,
            user.email,
        )

        if existing_user:
            raise ValueError("Email already registered.")

        hashed_password = hash_password(
            user.password,
        )

        return create_user(
            db=db,
            user=user,
            hashed_password=hashed_password,
        )

    @staticmethod
    def authenticate_user(
        db: Session,
        email: str,
        password: str,
    ) -> User | None:
        user = get_user_by_email(
            db,
            email,
        )

        if user is None:
            return None

        if not verify_password(
            password,
            user.password_hash,
        ):
            return None

        return user

    @staticmethod
    def login_user(
        db: Session,
        email: str,
        password: str,
    ) -> dict:
        user = AuthService.authenticate_user(
            db,
            email,
            password,
        )

        if user is None:
            raise ValueError("Invalid email or password.")

        access_token = create_access_token(
            {
                "sub": str(user.user_id),
            }
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
        }