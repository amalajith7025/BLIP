from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class OrganizationStatus(str, Enum):
    ACTIVE = "Active"
    SUSPENDED = "Suspended"
    ARCHIVED = "Archived"


class OrganizationCreate(BaseModel):
    tenant_id: UUID
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    industry: str | None = Field(default=None, max_length=100)
    timezone: str | None = Field(default=None, max_length=100)


class OrganizationUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    industry: str | None = Field(default=None, max_length=100)
    timezone: str | None = Field(default=None, max_length=100)


class OrganizationStatusUpdate(BaseModel):
    status: OrganizationStatus


class OrganizationResponse(BaseModel):
    organization_id: UUID
    tenant_id: UUID
    name: str
    description: str | None
    industry: str | None
    timezone: str | None
    status: OrganizationStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
