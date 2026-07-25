from uuid import UUID

from pydantic import BaseModel, ConfigDict


class HypothesisCreate(BaseModel):
    investigation_id: UUID
    hypothesis_statement: str
    status: str


class HypothesisUpdate(BaseModel):
    investigation_id: UUID | None = None
    hypothesis_statement: str | None = None
    status: str | None = None


class HypothesisResponse(BaseModel):
    hypothesis_id: UUID
    investigation_id: UUID
    hypothesis_statement: str
    status: str

    model_config = ConfigDict(from_attributes=True)