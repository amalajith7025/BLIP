from __future__ import annotations

import time

import pandas as pd

from app.analysis.capabilities.registry import AnalysisCapabilityRegistry
from app.analysis.capabilities.services import build_default_capability_registry
from app.analysis.engine import AnalysisEngine
from app.analysis.schemas import DatasetProfile
from app.business_goals.schemas import BusinessGoal
from app.findings.services import FindingsBuilderService
from app.investigation_framework.interfaces import InvestigationStageExecutor
from app.investigation_framework.registry import StageExecutorRegistry
from app.investigation_framework.schemas import (
    Investigation,
    InvestigationExecutionContext,
    InvestigationStage,
    InvestigationStageName,
    StageExecutionResult,
)
from app.investigation_framework.services import (
    InvestigationOrchestrationService,
    create_universal_investigation,
)
from app.planning.schemas import PlanningResult
from app.planning.services import InvestigationPlannerService

from .schemas import (
    ExecutedCapabilityResult,
    InvestigationExecutionSummary,
    InvestigationResult,
)


class CapabilityExecutionStageExecutor(InvestigationStageExecutor):
    """
    Executes planned capabilities for a single investigation stage.
    """

    def __init__(
        self,
        stage_name: InvestigationStageName,
        analysis_engine: AnalysisEngine,
        capability_registry: AnalysisCapabilityRegistry,
    ):
        self.stage_name = stage_name
        self.analysis_engine = analysis_engine
        self.capability_registry = capability_registry

    def execute(
        self,
        investigation: Investigation,
        stage: InvestigationStage,
        context: InvestigationExecutionContext,
    ) -> StageExecutionResult:
        capability_ids = stage.inputs.get("capability_ids", [])
        dataset = stage.inputs.get("dataset")
        executed_capabilities: list[ExecutedCapabilityResult] = []
        stage_warnings: list[str] = []

        if not capability_ids:
            return StageExecutionResult(
                outputs={
                    "executed_capabilities": [],
                    "analysis_results": {},
                    "warnings": [],
                },
                metadata={
                    "capability_count": 0,
                },
            )

        if dataset is None:
            return StageExecutionResult(
                outputs={
                    "executed_capabilities": [],
                    "analysis_results": {},
                    "warnings": ["dataset is missing for stage execution"],
                },
                metadata={
                    "capability_count": len(capability_ids),
                },
            )

        analysis_results: dict[str, dict] = {}

        for capability_id in capability_ids:
            capability = self.capability_registry.get(capability_id)
            if capability is None:
                executed_capabilities.append(
                    ExecutedCapabilityResult(
                        capability_id=capability_id,
                        plugin_name="",
                        stage=self.stage_name.value,
                        status="skipped",
                        reason="capability metadata not found",
                    )
                )
                stage_warnings.append(f"Capability '{capability_id}' metadata not found")
                continue

            plugin = self.analysis_engine.registry.get(capability.plugin_key)
            if plugin is None:
                executed_capabilities.append(
                    ExecutedCapabilityResult(
                        capability_id=capability_id,
                        plugin_name=capability.plugin_key,
                        stage=self.stage_name.value,
                        status="skipped",
                        reason="analysis plugin is not registered",
                    )
                )
                stage_warnings.append(
                    f"Capability '{capability_id}' plugin '{capability.plugin_key}' not registered"
                )
                continue

            try:
                result_payload = plugin.execute(dataset)
                explanation = plugin.explain(result_payload)
                observations = plugin.observations(result_payload)
            except Exception as error:
                executed_capabilities.append(
                    ExecutedCapabilityResult(
                        capability_id=capability_id,
                        plugin_name=capability.plugin_key,
                        stage=self.stage_name.value,
                        status="failed",
                        reason=str(error),
                    )
                )
                stage_warnings.append(
                    f"Capability '{capability_id}' failed during execution"
                )
                continue

            executed = ExecutedCapabilityResult(
                capability_id=capability_id,
                plugin_name=capability.plugin_key,
                stage=self.stage_name.value,
                status="executed",
                results=result_payload,
                explanation=explanation,
                observations=observations,
            )
            executed_capabilities.append(executed)
            analysis_results[capability_id] = {
                "plugin_name": capability.plugin_key,
                "stage": self.stage_name.value,
                "results": result_payload,
                "explanation": explanation,
                "observations": observations,
            }

        return StageExecutionResult(
            outputs={
                "executed_capabilities": [item.__dict__ for item in executed_capabilities],
                "analysis_results": analysis_results,
                "warnings": stage_warnings,
            },
            metadata={
                "capability_count": len(capability_ids),
            },
        )


class InvestigationWorkflowService:
    """
    End-to-end investigation pipeline orchestration built from existing BLIP systems.
    """

    def __init__(
        self,
        planner: InvestigationPlannerService | None = None,
        framework: InvestigationOrchestrationService | None = None,
        analysis_engine: AnalysisEngine | None = None,
        capability_registry: AnalysisCapabilityRegistry | None = None,
        findings_builder: FindingsBuilderService | None = None,
    ):
        self.capability_registry = capability_registry or build_default_capability_registry()
        self.analysis_engine = analysis_engine or AnalysisEngine()
        self.planner = planner or InvestigationPlannerService(
            capability_registry=self.capability_registry,
        )
        self.framework = framework or self._build_framework()
        self.findings_builder = findings_builder or FindingsBuilderService()

    def execute_investigation(
        self,
        dataset_profile: DatasetProfile,
        business_goal: BusinessGoal,
        dataset: pd.DataFrame,
    ) -> InvestigationResult:
        started = time.perf_counter()

        planning_result = self.planner.plan(business_goal, dataset_profile)

        stage_inputs = {
            stage_name: {
                "capability_ids": capability_ids,
                "dataset": dataset,
                "dataset_profile": dataset_profile,
            }
            for stage_name, capability_ids in planning_result.blueprint.stage_capability_order.items()
        }

        investigation = create_universal_investigation(
            name=f"Investigation - {business_goal.name}",
            stage_inputs=stage_inputs,
        )

        executed_investigation = self.framework.execute(investigation)

        executed_capabilities: list[ExecutedCapabilityResult] = []
        analysis_results: dict[str, dict] = {}
        warnings = list(planning_result.planning_warnings)

        for stage in executed_investigation.stages:
            stage_output = stage.outputs
            stage_warnings = stage_output.get("warnings", [])
            warnings.extend(stage_warnings)

            for capability_data in stage_output.get("executed_capabilities", []):
                executed = ExecutedCapabilityResult(**capability_data)
                executed_capabilities.append(executed)

            for capability_id, result_data in stage_output.get("analysis_results", {}).items():
                analysis_results[capability_id] = result_data

        total_executed = sum(1 for item in executed_capabilities if item.status == "executed")
        total_failed = sum(1 for item in executed_capabilities if item.status == "failed")
        total_skipped = len(planning_result.skipped_capabilities) + sum(
            1 for item in executed_capabilities if item.status == "skipped"
        )

        duration_ms = round((time.perf_counter() - started) * 1000, 3)

        summary = InvestigationExecutionSummary(
            framework_status=executed_investigation.status,
            stage_statuses={stage.name.value: stage.status for stage in executed_investigation.stages},
            total_selected=len(planning_result.selected_capabilities),
            total_executed=total_executed,
            total_failed=total_failed,
            total_skipped=total_skipped,
        )

        missing_values = sum(column.missing_values for column in dataset_profile.column_profiles)
        total_cells = dataset_profile.rows * max(1, dataset_profile.columns)
        missing_ratio = (missing_values / total_cells) if total_cells > 0 else 1.0

        base_result = InvestigationResult(
            investigation_metadata={
                "goal_id": business_goal.goal_id,
                "goal_name": business_goal.name,
                "dataset_name": dataset_profile.name,
                "dataset_rows": str(dataset_profile.rows),
                "dataset_columns": str(dataset_profile.columns),
                "dataset_missing_ratio": str(round(missing_ratio, 6)),
                "workflow_version": "1.0.0",
            },
            execution_summary=summary,
            executed_capabilities=executed_capabilities,
            skipped_capabilities=planning_result.skipped_capabilities,
            analysis_results=analysis_results,
            execution_duration_ms=duration_ms,
            warnings=warnings,
            planner_decisions=planning_result,
            confidence=planning_result.planner_confidence,
        )

        findings_collection = self.findings_builder.build(base_result)

        return InvestigationResult(
            investigation_metadata=base_result.investigation_metadata,
            execution_summary=base_result.execution_summary,
            executed_capabilities=base_result.executed_capabilities,
            skipped_capabilities=base_result.skipped_capabilities,
            findings_collection=findings_collection,
            analysis_results=base_result.analysis_results,
            execution_duration_ms=base_result.execution_duration_ms,
            warnings=base_result.warnings,
            planner_decisions=base_result.planner_decisions,
            confidence=base_result.confidence,
        )

    def _build_framework(self) -> InvestigationOrchestrationService:
        registry = StageExecutorRegistry()

        for stage_name in (
            InvestigationStageName.OBSERVE,
            InvestigationStageName.EXPLAIN,
            InvestigationStageName.VALIDATE,
            InvestigationStageName.RECOMMEND,
        ):
            registry.register(
                CapabilityExecutionStageExecutor(
                    stage_name=stage_name,
                    analysis_engine=self.analysis_engine,
                    capability_registry=self.capability_registry,
                )
            )

        return InvestigationOrchestrationService(registry=registry)