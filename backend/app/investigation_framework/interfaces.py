from abc import ABC, abstractmethod

from .schemas import (
    Investigation,
    InvestigationExecutionContext,
    InvestigationStage,
    InvestigationStageName,
    StageExecutionResult,
)


class InvestigationStageExecutor(ABC):
    """
    Pluggable executor contract for a single investigation stage.
    """

    stage_name: InvestigationStageName

    @abstractmethod
    def execute(
        self,
        investigation: Investigation,
        stage: InvestigationStage,
        context: InvestigationExecutionContext,
    ) -> StageExecutionResult:
        """
        Execute deterministic logic for the stage and return stage outputs.
        """
        pass