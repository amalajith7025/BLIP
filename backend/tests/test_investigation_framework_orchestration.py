import pytest

from app.investigation_framework.interfaces import InvestigationStageExecutor
from app.investigation_framework.registry import StageExecutorRegistry
from app.investigation_framework.schemas import (
    Investigation,
    InvestigationExecutionContext,
    InvestigationStage,
    InvestigationStageName,
    InvestigationStatus,
    StageExecutionResult,
    StageStatus,
)
from app.investigation_framework.services import (
    InvestigationOrchestrationService,
    StageExecutionError,
    build_universal_stages,
)


class RecordingExecutor(InvestigationStageExecutor):
    def __init__(self, stage_name: InvestigationStageName, recorder: list[str]):
        self.stage_name = stage_name
        self._recorder = recorder

    def execute(
        self,
        investigation: Investigation,
        stage: InvestigationStage,
        context: InvestigationExecutionContext,
    ) -> StageExecutionResult:
        self._recorder.append(stage.name.value)
        return StageExecutionResult(
            outputs={"executed": stage.name.value},
            metadata={"order": stage.execution_order},
        )


class FailingExecutor(InvestigationStageExecutor):
    stage_name = InvestigationStageName.EXPLAIN

    def execute(
        self,
        investigation: Investigation,
        stage: InvestigationStage,
        context: InvestigationExecutionContext,
    ) -> StageExecutionResult:
        raise RuntimeError("deterministic failure")


def test_orchestrator_executes_stages_in_order():
    recorder: list[str] = []
    registry = StageExecutorRegistry()

    for stage in build_universal_stages():
        registry.register(RecordingExecutor(stage.name, recorder))

    service = InvestigationOrchestrationService(registry)
    investigation = Investigation(name="Lifecycle", stages=build_universal_stages())

    result = service.execute(investigation)

    assert result.status == InvestigationStatus.COMPLETED
    assert recorder == [
        "understand",
        "observe",
        "explain",
        "validate",
        "recommend",
        "learn",
    ]
    assert [stage.status for stage in result.stages] == [
        StageStatus.COMPLETED,
        StageStatus.COMPLETED,
        StageStatus.COMPLETED,
        StageStatus.COMPLETED,
        StageStatus.COMPLETED,
        StageStatus.COMPLETED,
    ]


def test_orchestrator_uses_noop_for_unregistered_stages():
    registry = StageExecutorRegistry()
    recorder: list[str] = []
    registry.register(RecordingExecutor(InvestigationStageName.UNDERSTAND, recorder))

    service = InvestigationOrchestrationService(registry)
    investigation = Investigation(name="Partial", stages=build_universal_stages())

    result = service.execute(investigation)

    assert result.stages[0].outputs == {"executed": "understand"}
    assert result.stages[1].outputs["status"] == "no_executor_registered"
    assert result.status == InvestigationStatus.COMPLETED


def test_orchestrator_marks_stage_and_investigation_failed_on_exception():
    registry = StageExecutorRegistry()
    recorder: list[str] = []
    registry.register(RecordingExecutor(InvestigationStageName.UNDERSTAND, recorder))
    registry.register(RecordingExecutor(InvestigationStageName.OBSERVE, recorder))
    registry.register(FailingExecutor())

    service = InvestigationOrchestrationService(registry)
    investigation = Investigation(name="Failure Path", stages=build_universal_stages())

    with pytest.raises(StageExecutionError):
        service.execute(investigation)

    assert investigation.status == InvestigationStatus.FAILED
    assert investigation.stages[0].status == StageStatus.COMPLETED
    assert investigation.stages[1].status == StageStatus.COMPLETED
    assert investigation.stages[2].status == StageStatus.FAILED


def test_orchestrator_rejects_duplicate_execution_order():
    duplicate_stages = [
        InvestigationStage(
            name=InvestigationStageName.UNDERSTAND,
            description="A",
            execution_order=1,
        ),
        InvestigationStage(
            name=InvestigationStageName.OBSERVE,
            description="B",
            execution_order=1,
        ),
    ]

    service = InvestigationOrchestrationService()

    with pytest.raises(ValueError, match="execution_order"):
        service.execute(Investigation(name="Invalid", stages=duplicate_stages))