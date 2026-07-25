from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RecommendationCreate(BaseModel):
    investigation_id: UUID
    finding_id: UUID
    recommendation_statement: str


class RecommendationUpdate(BaseModel):
    investigation_id: UUID | None = None
    finding_id: UUID | None = None
    recommendation_statement: str | None = None


class RecommendationResponse(BaseModel):
    recommendation_id: UUID
    investigation_id: UUID
    finding_id: UUID
    recommendation_statement: str

    model_config = ConfigDict(from_attributes=True)