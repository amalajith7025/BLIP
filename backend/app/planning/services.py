from __future__ import annotations

from app.analysis.capabilities.registry import AnalysisCapabilityRegistry
from app.analysis.capabilities.schemas import AnalysisCapability, CapabilityStage, SemanticPrimitive
from app.analysis.capabilities.services import build_default_capability_registry
from app.analysis.schemas import DatasetProfile
from app.business_goals.registry import BusinessGoalRegistry
from app.business_goals.schemas import BusinessGoal
from app.business_goals.services import build_default_goal_registry
from app.investigation_framework.schemas import InvestigationStageName

from .schemas import (
    CompatibilityCheck,
    InvestigationBlueprint,
    PlanningResult,
    SelectedCapability,
    SkippedCapability,
)


class InvestigationPlannerService:
    """
    Deterministic planner that maps a business goal and dataset profile
    into an executable capability blueprint.
    """

    def __init__(
        self,
        goal_registry: BusinessGoalRegistry | None = None,
        capability_registry: AnalysisCapabilityRegistry | None = None,
    ):
        self.goal_registry = goal_registry or build_default_goal_registry()
        self.capability_registry = capability_registry or build_default_capability_registry()

    def plan(
        self,
        goal: BusinessGoal,
        dataset_profile: DatasetProfile,
    ) -> PlanningResult:
        planning_warnings: list[str] = []
        skipped: list[SkippedCapability] = []
        compatibility_report: dict[str, CompatibilityCheck] = {}

        registered_goal = self.goal_registry.get_by_id(goal.goal_id)
        if registered_goal is None:
            raise KeyError(f"Business goal '{goal.goal_id}' is not registered")

        dataset_primitives = self._extract_dataset_primitives(dataset_profile)

        requested_map: dict[str, str] = {}
        for capability_id in self.goal_registry.get_required_capabilities(goal.goal_id):
            requested_map.setdefault(capability_id, "required")
        for capability_id in self.goal_registry.get_optional_capabilities(goal.goal_id):
            requested_map.setdefault(capability_id, "optional")

        selected: dict[str, SelectedCapability] = {}

        for capability_id, requested_as in requested_map.items():
            capability = self.capability_registry.get(capability_id)
            if capability is None:
                skipped.append(
                    SkippedCapability(
                        capability_id=capability_id,
                        requested_as=requested_as,
                        reason="capability metadata not found in registry",
                    )
                )
                planning_warnings.append(f"Capability '{capability_id}' is missing from capability registry")
                continue

            check = self._evaluate_compatibility(capability, dataset_profile, dataset_primitives)
            compatibility_report[capability.capability_id] = check

            if not check.compatible:
                skipped.append(
                    SkippedCapability(
                        capability_id=capability.capability_id,
                        requested_as=requested_as,
                        reason="; ".join(check.reasons),
                    )
                )
                continue

            selected[capability.capability_id] = SelectedCapability(
                capability_id=capability.capability_id,
                requested_as=requested_as,
                capability=capability,
            )

        self._resolve_dependencies(
            selected=selected,
            skipped=skipped,
            compatibility_report=compatibility_report,
            dataset_profile=dataset_profile,
            dataset_primitives=dataset_primitives,
            planning_warnings=planning_warnings,
        )

        execution_order = self._build_execution_order(
            [selection.capability for selection in selected.values()],
            planning_warnings,
        )

        ordered_selected = [selected[capability_id] for capability_id in execution_order if capability_id in selected]
        stage_plan = self._build_stage_plan(execution_order, selected)

        required_ids = self.goal_registry.get_required_capabilities(goal.goal_id)
        optional_ids = self.goal_registry.get_optional_capabilities(goal.goal_id)
        confidence = self._calculate_confidence(
            required_ids=required_ids,
            optional_ids=optional_ids,
            selected=ordered_selected,
            warnings=planning_warnings,
        )

        if not any(item.requested_as == "required" for item in ordered_selected):
            planning_warnings.append("No required capabilities are executable for the supplied dataset profile")

        blueprint = InvestigationBlueprint(
            goal_id=registered_goal.goal_id,
            goal_name=registered_goal.name,
            dataset_name=dataset_profile.name,
            execution_order=execution_order,
            stage_capability_order=stage_plan,
            metadata={
                "business_purpose": registered_goal.business_purpose.value,
                "planner_version": "1.0.0",
            },
        )

        return PlanningResult(
            selected_capabilities=ordered_selected,
            skipped_capabilities=skipped,
            planning_warnings=planning_warnings,
            execution_order=execution_order,
            compatibility_report=compatibility_report,
            planner_confidence=confidence,
            blueprint=blueprint,
            metadata={
                "dataset_primitives": ",".join(sorted(primitive.value for primitive in dataset_primitives)),
                "goal_id": registered_goal.goal_id,
            },
        )

    def _resolve_dependencies(
        self,
        selected: dict[str, SelectedCapability],
        skipped: list[SkippedCapability],
        compatibility_report: dict[str, CompatibilityCheck],
        dataset_profile: DatasetProfile,
        dataset_primitives: set[SemanticPrimitive],
        planning_warnings: list[str],
    ) -> None:
        changed = True
        while changed:
            changed = False

            for capability_id in list(selected.keys()):
                capability = selected[capability_id].capability

                missing_dependency = False
                for dependency_id in capability.dependencies:
                    dependency = self.capability_registry.get(dependency_id)
                    if dependency is None:
                        reason = f"missing dependency '{dependency_id}'"
                        skipped.append(
                            SkippedCapability(
                                capability_id=capability_id,
                                requested_as=selected[capability_id].requested_as,
                                reason=reason,
                            )
                        )
                        compatibility_report[capability_id] = CompatibilityCheck(
                            capability_id=capability_id,
                            compatible=False,
                            reasons=[reason],
                            dataset_primitives=[],
                            required_primitives=[
                                primitive.value
                                for primitive in sorted(
                                    set(capability.supported_semantic_primitives),
                                    key=lambda item: item.value,
                                )
                            ],
                        )
                        planning_warnings.append(
                            f"Capability '{capability_id}' skipped due to missing dependency '{dependency_id}'"
                        )
                        del selected[capability_id]
                        missing_dependency = True
                        changed = True
                        break

                    if dependency.capability_id not in compatibility_report:
                        compatibility_report[dependency.capability_id] = self._evaluate_compatibility(
                            dependency,
                            dataset_profile,
                            dataset_primitives,
                        )

                    check = compatibility_report[dependency.capability_id]
                    if not check.compatible:
                        reason = f"incompatible dependency '{dependency_id}': {'; '.join(check.reasons)}"
                        skipped.append(
                            SkippedCapability(
                                capability_id=capability_id,
                                requested_as=selected[capability_id].requested_as,
                                reason=reason,
                            )
                        )
                        compatibility_report[capability_id] = CompatibilityCheck(
                            capability_id=capability_id,
                            compatible=False,
                            reasons=[reason],
                            dataset_primitives=[],
                            required_primitives=[
                                primitive.value
                                for primitive in sorted(
                                    set(capability.supported_semantic_primitives),
                                    key=lambda item: item.value,
                                )
                            ],
                        )
                        planning_warnings.append(
                            f"Capability '{capability_id}' skipped because dependency '{dependency_id}' is incompatible"
                        )
                        del selected[capability_id]
                        missing_dependency = True
                        changed = True
                        break

                    if dependency_id not in selected:
                        selected[dependency_id] = SelectedCapability(
                            capability_id=dependency_id,
                            requested_as="dependency",
                            capability=dependency,
                        )
                        changed = True

                if missing_dependency:
                    continue

    def _build_execution_order(
        self,
        capabilities: list[AnalysisCapability],
        planning_warnings: list[str],
    ) -> list[str]:
        if not capabilities:
            return []

        capability_ids = {capability.capability_id for capability in capabilities}
        in_degree: dict[str, int] = {capability.capability_id: 0 for capability in capabilities}
        adjacency: dict[str, list[str]] = {capability.capability_id: [] for capability in capabilities}
        capability_map = {capability.capability_id: capability for capability in capabilities}

        for capability in capabilities:
            for dependency_id in capability.dependencies:
                if dependency_id not in capability_ids:
                    continue
                adjacency[dependency_id].append(capability.capability_id)
                in_degree[capability.capability_id] += 1

        ready = [capability_id for capability_id, degree in in_degree.items() if degree == 0]
        ready = self._sort_capability_ids(ready, capability_map)
        ordered: list[str] = []

        while ready:
            current = ready.pop(0)
            ordered.append(current)

            for child in self._sort_capability_ids(adjacency[current], capability_map):
                in_degree[child] -= 1
                if in_degree[child] == 0:
                    ready.append(child)
            ready = self._sort_capability_ids(ready, capability_map)

        if len(ordered) != len(capability_ids):
            planning_warnings.append("Capability dependency cycle detected; fallback deterministic ordering applied")
            remaining = [capability_id for capability_id in capability_ids if capability_id not in ordered]
            ordered.extend(self._sort_capability_ids(remaining, capability_map))

        return ordered

    def _build_stage_plan(
        self,
        execution_order: list[str],
        selected: dict[str, SelectedCapability],
    ) -> dict[InvestigationStageName, list[str]]:
        stage_map: dict[InvestigationStageName, list[str]] = {
            InvestigationStageName.UNDERSTAND: [],
            InvestigationStageName.OBSERVE: [],
            InvestigationStageName.EXPLAIN: [],
            InvestigationStageName.VALIDATE: [],
            InvestigationStageName.RECOMMEND: [],
            InvestigationStageName.LEARN: [],
        }

        for capability_id in execution_order:
            selection = selected.get(capability_id)
            if selection is None:
                continue

            stage_name = self._capability_stage_to_investigation_stage(selection.capability.investigation_stage)
            stage_map[stage_name].append(capability_id)

        return stage_map

    @staticmethod
    def _capability_stage_to_investigation_stage(stage: CapabilityStage) -> InvestigationStageName:
        mapping = {
            CapabilityStage.OBSERVE: InvestigationStageName.OBSERVE,
            CapabilityStage.EXPLAIN: InvestigationStageName.EXPLAIN,
            CapabilityStage.VALIDATE: InvestigationStageName.VALIDATE,
            CapabilityStage.RECOMMEND: InvestigationStageName.RECOMMEND,
        }
        return mapping[stage]

    def _evaluate_compatibility(
        self,
        capability: AnalysisCapability,
        dataset_profile: DatasetProfile,
        dataset_primitives: set[SemanticPrimitive],
    ) -> CompatibilityCheck:
        reasons: list[str] = []

        required_primitives = set(capability.supported_semantic_primitives)
        if required_primitives and not (required_primitives & dataset_primitives):
            reasons.append("unsupported semantic primitives")

        constraints = capability.execution_constraints
        if constraints.minimum_rows is not None and dataset_profile.rows < constraints.minimum_rows:
            reasons.append(f"requires at least {constraints.minimum_rows} rows")

        if constraints.minimum_columns is not None and dataset_profile.columns < constraints.minimum_columns:
            reasons.append(f"requires at least {constraints.minimum_columns} columns")

        if constraints.requires_non_null_ratio_at_least is not None:
            non_null_ratio = self._dataset_non_null_ratio(dataset_profile)
            if non_null_ratio < constraints.requires_non_null_ratio_at_least:
                reasons.append(
                    "requires higher non-null ratio"
                )

        return CompatibilityCheck(
            capability_id=capability.capability_id,
            compatible=len(reasons) == 0,
            reasons=reasons,
            dataset_primitives=[primitive.value for primitive in sorted(dataset_primitives, key=lambda item: item.value)],
            required_primitives=[primitive.value for primitive in sorted(required_primitives, key=lambda item: item.value)],
        )

    @staticmethod
    def _dataset_non_null_ratio(dataset_profile: DatasetProfile) -> float:
        total_cells = dataset_profile.rows * dataset_profile.columns
        if total_cells == 0:
            return 0.0

        missing = sum(column.missing_values for column in dataset_profile.column_profiles)
        non_null = max(0, total_cells - missing)
        return non_null / total_cells

    @staticmethod
    def _extract_dataset_primitives(dataset_profile: DatasetProfile) -> set[SemanticPrimitive]:
        primitives: set[SemanticPrimitive] = set()

        for column in dataset_profile.column_profiles:
            if column.continuous or column.discrete or column.can_average or column.can_correlate:
                primitives.add(SemanticPrimitive.NUMERIC)
            if column.categorical or column.can_group:
                primitives.add(SemanticPrimitive.CATEGORICAL)
            if column.boolean:
                primitives.add(SemanticPrimitive.BOOLEAN)
            if column.datetime or column.can_forecast:
                primitives.add(SemanticPrimitive.DATETIME)
            if column.text:
                primitives.add(SemanticPrimitive.TEXT)
            if column.role == "identifier":
                primitives.add(SemanticPrimitive.IDENTIFIER)

        return primitives

    @staticmethod
    def _sort_capability_ids(
        capability_ids: list[str],
        capability_map: dict[str, AnalysisCapability],
    ) -> list[str]:
        stage_rank = {
            CapabilityStage.OBSERVE: 1,
            CapabilityStage.EXPLAIN: 2,
            CapabilityStage.VALIDATE: 3,
            CapabilityStage.RECOMMEND: 4,
        }

        return sorted(
            capability_ids,
            key=lambda capability_id: (
                stage_rank[capability_map[capability_id].investigation_stage],
                capability_id,
            ),
        )

    @staticmethod
    def _calculate_confidence(
        required_ids: list[str],
        optional_ids: list[str],
        selected: list[SelectedCapability],
        warnings: list[str],
    ) -> float:
        required_selected = sum(
            1
            for selection in selected
            if selection.requested_as == "required"
        )
        optional_selected = sum(
            1
            for selection in selected
            if selection.requested_as == "optional"
        )

        required_score = (required_selected / len(required_ids)) if required_ids else 1.0
        optional_score = (optional_selected / len(optional_ids)) if optional_ids else 1.0
        warning_penalty = min(0.30, 0.05 * len(warnings))

        confidence = (0.75 * required_score) + (0.25 * optional_score) - warning_penalty
        return round(max(0.0, min(1.0, confidence)), 3)