from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class InvestigationStageName(str, Enum):
    UNDERSTAND = "understand"
    OBSERVE = "observe"
    EXPLAIN = "explain"
    VALIDATE = "validate"
    RECOMMEND = "recommend"
    LEARN = "learn"


class StageStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class InvestigationStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class InvestigationStage:
    """
    Represents one deterministic stage in an investigation lifecycle.
    """

    name: InvestigationStageName
    description: str
    status: StageStatus = StageStatus.PENDING
    inputs: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, Any] = field(default_factory=dict)
    execution_order: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Investigation:
    """
    Universal domain model for any investigation executed by BLIP.
    """

    name: str
    stages: list[InvestigationStage] = field(default_factory=list)
    status: InvestigationStatus = InvestigationStatus.NOT_STARTED
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class StageExecutionResult:
    """
    Deterministic output contract returned by stage executors.
    """

    outputs: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class InvestigationExecutionContext:
    """
    Shared deterministic context across sequential stage execution.
    """

    stage_outputs: dict[InvestigationStageName, dict[str, Any]] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)