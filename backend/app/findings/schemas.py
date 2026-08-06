from dataclasses import dataclass, field


@dataclass(frozen=True)
class Evidence:
    capability_id: str
    capability_name: str
    source_analysis: str
    evidence_type: str
    evidence_value: dict | str | float | int | bool | None
    confidence: float
    trace_reference: str


@dataclass(frozen=True)
class Finding:
    id: str
    title: str
    description: str
    category: str
    severity: str
    confidence: float
    business_impact: str
    supporting_capabilities: list[str] = field(default_factory=list)
    supporting_evidence: list[Evidence] = field(default_factory=list)
    related_metrics: list[str] = field(default_factory=list)
    related_dimensions: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    created_at: str = "1970-01-01T00:00:00Z"


@dataclass(frozen=True)
class FindingCollection:
    investigation_id: str
    findings: list[Finding] = field(default_factory=list)
    summary: dict = field(default_factory=dict)
    statistics: dict = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    execution_metadata: dict = field(default_factory=dict)