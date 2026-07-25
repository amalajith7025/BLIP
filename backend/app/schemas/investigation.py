from uuid import UUID

from pydantic import BaseModel, ConfigDict


class InvestigationCreate(BaseModel):
    organization_id: UUID
    organization_unit_id: UUID | None = None
    title: str
    description: str | None = None
    status: str


class InvestigationUpdate(BaseModel):
    organization_id: UUID | None = None
    organization_unit_id: UUID | None = None
    title: str | None = None
    description: str | None = None
    status: str | None = None


class InvestigationResponse(BaseModel):
    investigation_id: UUID
    organization_id: UUID
    organization_unit_id: UUID | None
    title: str
    description: str | None
    status: str

    model_config = ConfigDict(from_attributes=True)