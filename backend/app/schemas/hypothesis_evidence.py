from uuid import UUID

from pydantic import BaseModel, ConfigDict


class HypothesisEvidenceCreate(BaseModel):
    hypothesis_id: UUID
    evidence_id: UUID


class HypothesisEvidenceUpdate(BaseModel):
    hypothesis_id: UUID | None = None
    evidence_id: UUID | None = None


class HypothesisEvidenceResponse(BaseModel):
    hypothesis_evidence_id: UUID
    hypothesis_id: UUID
    evidence_id: UUID

    model_config = ConfigDict(from_attributes=True)