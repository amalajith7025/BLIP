from uuid import UUID

from pydantic import BaseModel, ConfigDict


class FactCreate(BaseModel):
    investigation_id: UUID
    artifact_id: UUID | None = None
    fact_statement: str


class FactUpdate(BaseModel):
    investigation_id: UUID | None = None
    artifact_id: UUID | None = None
    fact_statement: str | None = None


class FactResponse(BaseModel):
    fact_id: UUID
    investigation_id: UUID
    artifact_id: UUID | None
    fact_statement: str

    model_config = ConfigDict(from_attributes=True)