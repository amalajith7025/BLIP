from uuid import UUID

from pydantic import BaseModel, ConfigDict


class OrganizationIndustryCreate(BaseModel):
    organization_id: UUID
    industry_id: UUID


class OrganizationIndustryUpdate(BaseModel):
    organization_id: UUID | None = None
    industry_id: UUID | None = None


class OrganizationIndustryResponse(BaseModel):
    organization_industry_id: UUID
    organization_id: UUID
    industry_id: UUID

    model_config = ConfigDict(from_attributes=True)