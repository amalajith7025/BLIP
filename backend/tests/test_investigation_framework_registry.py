from app.investigation_framework.interfaces import InvestigationStageExecutor
from app.investigation_framework.registry import StageExecutorRegistry
from app.investigation_framework.schemas import (
    Investigation,
    InvestigationExecutionContext,
    InvestigationStage,
    InvestigationStageName,
    StageExecutionResult,
)


class StubUnderstandExecutor(InvestigationStageExecutor):
    stage_name = InvestigationStageName.UNDERSTAND

    def execute(
        self,
        investigation: Investigation,
        stage: InvestigationStage,
        context: InvestigationExecutionContext,
    ) -> StageExecutionResult:
        return StageExecutionResult(outputs={"ok": True})


def test_registry_register_and_get_executor():
    registry = StageExecutorRegistry()
    executor = StubUnderstandExecutor()

    registry.register(executor)

    assert registry.get(InvestigationStageName.UNDERSTAND) is executor
    assert registry.all() == [executor]


def test_registry_replaces_executor_for_same_stage():
    registry = StageExecutorRegistry()
    first = StubUnderstandExecutor()
    second = StubUnderstandExecutor()

    registry.register(first)
    registry.register(second)

    assert registry.get(InvestigationStageName.UNDERSTAND) is second
    assert len(registry.all()) == 1