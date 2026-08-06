from dataclasses import dataclass, field

from app.analysis.capabilities.schemas import AnalysisCapability
from app.investigation_framework.schemas import InvestigationStageName


@dataclass(frozen=True)
class CompatibilityCheck:
    capability_id: str
    compatible: bool
    reasons: list[str] = field(default_factory=list)
    dataset_primitives: list[str] = field(default_factory=list)
    required_primitives: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class SelectedCapability:
    capability_id: str
    requested_as: str
    capability: AnalysisCapability


@dataclass(frozen=True)
class SkippedCapability:
    capability_id: str
    requested_as: str
    reason: str


@dataclass(frozen=True)
class InvestigationBlueprint:
    goal_id: str
    goal_name: str
    dataset_name: str
    execution_order: list[str] = field(default_factory=list)
    stage_capability_order: dict[InvestigationStageName, list[str]] = field(default_factory=dict)
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class PlanningResult:
    selected_capabilities: list[SelectedCapability] = field(default_factory=list)
    skipped_capabilities: list[SkippedCapability] = field(default_factory=list)
    planning_warnings: list[str] = field(default_factory=list)
    execution_order: list[str] = field(default_factory=list)
    compatibility_report: dict[str, CompatibilityCheck] = field(default_factory=dict)
    planner_confidence: float = 0.0
    blueprint: InvestigationBlueprint | None = None
    metadata: dict[str, str] = field(default_factory=dict)