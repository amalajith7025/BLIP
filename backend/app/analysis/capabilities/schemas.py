from dataclasses import dataclass, field
from enum import Enum


class CapabilityStage(str, Enum):
    OBSERVE = "observe"
    EXPLAIN = "explain"
    VALIDATE = "validate"
    RECOMMEND = "recommend"


class BusinessPurpose(str, Enum):
    DESCRIBE = "describe"
    DIAGNOSE = "diagnose"
    COMPARE = "compare"
    CLASSIFY = "classify"
    CLUSTER = "cluster"
    FORECAST = "forecast"
    DETECT_ANOMALY = "detect_anomaly"
    REDUCE_DIMENSION = "reduce_dimension"
    DISCOVER_ASSOCIATION = "discover_association"
    VALIDATE_ASSUMPTION = "validate_assumption"


class SemanticPrimitive(str, Enum):
    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    TEXT = "text"
    IDENTIFIER = "identifier"


class MaturityLevel(str, Enum):
    EXPERIMENTAL = "experimental"
    BETA = "beta"
    STABLE = "stable"


@dataclass(frozen=True)
class ExecutionConstraints:
    minimum_rows: int | None = None
    minimum_columns: int | None = None
    requires_non_null_ratio_at_least: float | None = None
    notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class AnalysisCapability:
    capability_id: str
    display_name: str
    description: str
    investigation_stage: CapabilityStage
    business_purpose: BusinessPurpose
    required_input_types: list[str] = field(default_factory=list)
    supported_semantic_primitives: list[SemanticPrimitive] = field(default_factory=list)
    expected_outputs: list[str] = field(default_factory=list)
    execution_constraints: ExecutionConstraints = field(default_factory=ExecutionConstraints)
    dependencies: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    maturity_level: MaturityLevel = MaturityLevel.BETA
    version: str = "1.0.0"
    plugin_key: str = ""