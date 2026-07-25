from uuid import UUID

from pydantic import BaseModel, ConfigDict


class EvidenceCreate(BaseModel):
    investigation_id: UUID
    fact_id: UUID
    evidence_type: str
    evidence_statement: str
    confidence_score: int | None = None


class EvidenceUpdate(BaseModel):
    investigation_id: UUID | None = None
    fact_id: UUID | None = None
    evidence_type: str | None = None
    evidence_statement: str | None = None
    confidence_score: int | None = None


class EvidenceResponse(BaseModel):
    evidence_id: UUID
    investigation_id: UUID
    fact_id: UUID
    evidence_type: str
    evidence_statement: str
    confidence_score: int | None

    model_config = ConfigDict(from_attributes=True)