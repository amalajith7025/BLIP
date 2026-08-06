from dataclasses import dataclass, field

from app.findings.schemas import FindingCollection
from app.investigation_framework.schemas import InvestigationStatus, StageStatus
from app.planning.schemas import PlanningResult, SkippedCapability


@dataclass(frozen=True)
class ExecutedCapabilityResult:
    capability_id: str
    plugin_name: str
    stage: str
    status: str
    results: dict = field(default_factory=dict)
    explanation: dict = field(default_factory=dict)
    observations: dict = field(default_factory=dict)
    reason: str | None = None


@dataclass(frozen=True)
class InvestigationExecutionSummary:
    framework_status: InvestigationStatus
    stage_statuses: dict[str, StageStatus] = field(default_factory=dict)
    total_selected: int = 0
    total_executed: int = 0
    total_failed: int = 0
    total_skipped: int = 0


@dataclass(frozen=True)
class InvestigationResult:
    investigation_metadata: dict[str, str] = field(default_factory=dict)
    execution_summary: InvestigationExecutionSummary | None = None
    executed_capabilities: list[ExecutedCapabilityResult] = field(default_factory=list)
    skipped_capabilities: list[SkippedCapability] = field(default_factory=list)
    findings_collection: FindingCollection | None = None
    analysis_results: dict[str, dict] = field(default_factory=dict)
    execution_duration_ms: float = 0.0
    warnings: list[str] = field(default_factory=list)
    planner_decisions: PlanningResult | None = None
    confidence: float = 0.0