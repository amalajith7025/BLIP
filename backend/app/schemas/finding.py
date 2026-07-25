from uuid import UUID

from pydantic import BaseModel, ConfigDict


class FindingCreate(BaseModel):
    investigation_id: UUID
    finding_statement: str


class FindingUpdate(BaseModel):
    investigation_id: UUID | None = None
    finding_statement: str | None = None


class FindingResponse(BaseModel):
    finding_id: UUID
    investigation_id: UUID
    finding_statement: str

    model_config = ConfigDict(from_attributes=True)