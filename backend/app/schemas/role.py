from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RoleBase(BaseModel):
    role_name: str
    description: str | None = None


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    role_name: str | None = None
    description: str | None = None


class RoleResponse(RoleBase):
    role_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)