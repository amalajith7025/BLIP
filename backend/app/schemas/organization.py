from uuid import UUID
from pydantic import BaseModel, ConfigDict


class OrganizationCreate(BaseModel):
    tenant_id: UUID
    organization_name: str
    legal_name: str | None = None
    website: str | None = None
    description: str | None = None


class OrganizationUpdate(BaseModel):
    organization_name: str | None = None
    legal_name: str | None = None
    website: str | None = None
    description: str | None = None


class OrganizationResponse(BaseModel):
    organization_id: UUID
    tenant_id: UUID
    organization_name: str
    legal_name: str | None
    website: str | None
    description: str | None

    model_config = ConfigDict(from_attributes=True)