from uuid import UUID

from pydantic import BaseModel, ConfigDict


class OrganizationUnitCreate(BaseModel):
    organization_id: UUID
    unit_name: str
    unit_type: str | None = None
    description: str | None = None


class OrganizationUnitUpdate(BaseModel):
    organization_id: UUID | None = None
    unit_name: str | None = None
    unit_type: str | None = None
    description: str | None = None


class OrganizationUnitResponse(BaseModel):
    organization_unit_id: UUID
    organization_id: UUID
    unit_name: str
    unit_type: str | None
    description: str | None

    model_config = ConfigDict(from_attributes=True)