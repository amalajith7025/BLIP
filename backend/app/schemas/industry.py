from uuid import UUID

from pydantic import BaseModel, ConfigDict


class IndustryCreate(BaseModel):
    industry_name: str
    description: str | None = None


class IndustryUpdate(BaseModel):
    industry_name: str | None = None
    description: str | None = None


class IndustryResponse(BaseModel):
    industry_id: UUID
    industry_name: str
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)