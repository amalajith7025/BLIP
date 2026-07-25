from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ArtifactCreate(BaseModel):
    investigation_id: UUID
    artifact_name: str
    artifact_type: str
    file_path: str | None = None
    description: str | None = None


class ArtifactUpdate(BaseModel):
    investigation_id: UUID | None = None
    artifact_name: str | None = None
    artifact_type: str | None = None
    file_path: str | None = None
    description: str | None = None


class ArtifactResponse(BaseModel):
    artifact_id: UUID
    investigation_id: UUID
    artifact_name: str
    artifact_type: str
    file_path: str | None
    description: str | None

    model_config = ConfigDict(from_attributes=True)