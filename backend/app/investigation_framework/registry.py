from .interfaces import InvestigationStageExecutor
from .schemas import InvestigationStageName


class StageExecutorRegistry:
    """
    Registry for stage executors keyed by lifecycle stage name.
    """

    def __init__(self):
        self._executors: dict[InvestigationStageName, InvestigationStageExecutor] = {}

    def register(self, executor: InvestigationStageExecutor) -> None:
        self._executors[executor.stage_name] = executor

    def get(self, stage_name: InvestigationStageName) -> InvestigationStageExecutor | None:
        return self._executors.get(stage_name)

    def all(self) -> list[InvestigationStageExecutor]:
        return list(self._executors.values())