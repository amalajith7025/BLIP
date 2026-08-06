from __future__ import annotations

from dataclasses import replace

from .interfaces import InvestigationStageExecutor
from .registry import StageExecutorRegistry
from .schemas import (
    Investigation,
    InvestigationExecutionContext,
    InvestigationStage,
    InvestigationStageName,
    InvestigationStatus,
    StageExecutionResult,
    StageStatus,
)


class StageExecutionError(Exception):
    """
    Raised when one stage fails during deterministic orchestration.
    """


class NoOpStageExecutor(InvestigationStageExecutor):
    """
    Deterministic default executor for stages without registered capabilities.
    """

    def __init__(self, stage_name: InvestigationStageName):
        self.stage_name = stage_name

    def execute(
        self,
        investigation: Investigation,
        stage: InvestigationStage,
        context: InvestigationExecutionContext,
    ) -> StageExecutionResult:
        return StageExecutionResult(
            outputs={
                "status": "no_executor_registered",
                "stage": stage.name.value,
            },
            metadata={
                "deterministic": True,
            },
        )


class InvestigationOrchestrationService:
    """
    Executes investigation stages sequentially using pluggable executors.
    """

    def __init__(
        self,
        registry: StageExecutorRegistry | None = None,
    ):
        self.registry = registry or StageExecutorRegistry()

    def execute(self, investigation: Investigation) -> Investigation:
        self._validate_stages(investigation.stages)

        context = InvestigationExecutionContext()
        investigation.status = InvestigationStatus.IN_PROGRESS

        ordered_stages = sorted(
            investigation.stages,
            key=lambda stage: stage.execution_order,
        )

        for stage in ordered_stages:
            stage.status = StageStatus.RUNNING

            executor = self.registry.get(stage.name)
            if executor is None:
                executor = NoOpStageExecutor(stage.name)

            try:
                result = executor.execute(
                    investigation,
                    stage,
                    context,
                )
            except Exception as error:
                stage.status = StageStatus.FAILED
                investigation.status = InvestigationStatus.FAILED
                raise StageExecutionError(
                    f"Stage '{stage.name.value}' failed"
                ) from error

            stage.outputs = dict(result.outputs)
            stage.metadata.update(result.metadata)
            stage.status = StageStatus.COMPLETED
            context.stage_outputs[stage.name] = dict(result.outputs)

        investigation.metadata["stage_outputs"] = {
            stage_name.value: output
            for stage_name, output in context.stage_outputs.items()
        }
        investigation.status = InvestigationStatus.COMPLETED
        return investigation

    @staticmethod
    def _validate_stages(stages: list[InvestigationStage]) -> None:
        if not stages:
            raise ValueError("Investigation must define at least one stage")

        execution_orders = [stage.execution_order for stage in stages]
        if len(execution_orders) != len(set(execution_orders)):
            raise ValueError("Stage execution_order values must be unique")


def build_universal_stages() -> list[InvestigationStage]:
    """
    Build the canonical six-stage deterministic investigation lifecycle.
    """

    stage_templates = [
        (
            InvestigationStageName.UNDERSTAND,
            "Profile the dataset and establish structural understanding.",
            1,
        ),
        (
            InvestigationStageName.OBSERVE,
            "Capture objective patterns and measurable observations.",
            2,
        ),
        (
            InvestigationStageName.EXPLAIN,
            "Form deterministic explanatory statements from observations.",
            3,
        ),
        (
            InvestigationStageName.VALIDATE,
            "Test explanatory statements against deterministic checks.",
            4,
        ),
        (
            InvestigationStageName.RECOMMEND,
            "Package validated outcomes into recommendation-ready structures.",
            5,
        ),
        (
            InvestigationStageName.LEARN,
            "Capture reusable lifecycle insights for future investigations.",
            6,
        ),
    ]

    stages: list[InvestigationStage] = []
    for stage_name, description, order in stage_templates:
        stages.append(
            InvestigationStage(
                name=stage_name,
                description=description,
                execution_order=order,
            )
        )

    return stages


def create_universal_investigation(
    name: str,
    stage_inputs: dict[InvestigationStageName, dict] | None = None,
) -> Investigation:
    """
    Factory for creating a standard investigation with six lifecycle stages.
    """

    stage_inputs = stage_inputs or {}
    stages = build_universal_stages()

    hydrated_stages = [
        replace(
            stage,
            inputs=dict(stage_inputs.get(stage.name, {})),
        )
        for stage in stages
    ]

    return Investigation(
        name=name,
        stages=hydrated_stages,
    )