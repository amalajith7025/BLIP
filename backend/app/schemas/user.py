from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    organization_id: UUID
    role_id: UUID
    email: EmailStr
    first_name: str
    last_name: str


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    role_id: UUID | None = None
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool | None = None


class UserResponse(UserBase):
    user_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)