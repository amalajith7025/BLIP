from pydantic import BaseModel


class DatasetUploadResponse(BaseModel):
    dataset_id: str
    filename: str
    rows: int
    columns: int


class SemanticColumnResponse(BaseModel):
    name: str
    data_type: str
    primitive: str
    missing_values: int
    unique_values: int


class SemanticProfileResponse(BaseModel):
    dataset_id: str
    dataset_name: str
    rows: int
    columns: int
    measures: int
    dimensions: int
    health_score: float
    warnings: list[str]
    columns_profile: list[SemanticColumnResponse]


class BusinessGoalResponse(BaseModel):
    goal_id: str
    name: str
    description: str
    business_purpose: str
    tags: list[str]


class StartInvestigationRequest(BaseModel):
    dataset_id: str
    goal_id: str


class StartInvestigationResponse(BaseModel):
    investigation_id: str
    status: str
    progress: int
    current_step: str


class InvestigationStatusResponse(BaseModel):
    investigation_id: str
    status: str
    progress: int
    current_step: str
    warnings: list[str]


class FindingEvidenceResponse(BaseModel):
    capability_name: str
    evidence_type: str
    confidence: float
    trace_reference: str
    evidence_value: str


class FindingResponse(BaseModel):
    id: str
    title: str
    description: str
    category: str
    severity: str
    confidence: float
    business_impact: str
    supporting_analyses: list[str]
    supporting_evidence: list[FindingEvidenceResponse]


class FindingCollectionResponse(BaseModel):
    investigation_id: str
    findings: list[FindingResponse]
    summary: dict
    statistics: dict
    warnings: list[str]
    execution_metadata: dict


class InvestigationFindingsResponse(BaseModel):
    investigation_id: str
    status: str
    confidence: float
    findings_collection: FindingCollectionResponse