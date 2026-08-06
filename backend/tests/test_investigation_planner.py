from app.analysis.capabilities.registry import AnalysisCapabilityRegistry
from app.analysis.capabilities.schemas import (
    AnalysisCapability,
    BusinessPurpose,
    CapabilityStage,
    ExecutionConstraints,
    MaturityLevel,
    SemanticPrimitive,
)
from app.analysis.capabilities.services import build_default_capability_registry
from app.analysis.schemas import ColumnProfile, DatasetProfile
from app.business_goals.registry import BusinessGoalRegistry
from app.business_goals.schemas import BusinessGoal
from app.business_goals.services import build_default_goal_registry
from app.investigation_framework.schemas import InvestigationStageName
from app.planning.services import InvestigationPlannerService


def _dataset_profile(
    name: str,
    rows: int,
    columns: int,
    column_profiles: list[ColumnProfile],
) -> DatasetProfile:
    return DatasetProfile(
        name=name,
        rows=rows,
        columns=columns,
        column_profiles=column_profiles,
    )


def test_successful_planning_produces_execution_blueprint():
    planner = InvestigationPlannerService(
        goal_registry=build_default_goal_registry(),
        capability_registry=build_default_capability_registry(),
    )
    goal = planner.goal_registry.get_by_id("goal_compare_performance")
    assert goal is not None

    dataset = _dataset_profile(
        name="sales_dataset",
        rows=30,
        columns=3,
        column_profiles=[
            ColumnProfile(name="sales", data_type="float64", continuous=True, can_average=True, can_correlate=True),
            ColumnProfile(name="region", data_type="object", categorical=True, can_group=True, can_count=True),
            ColumnProfile(name="segment", data_type="object", categorical=True, can_group=True, can_count=True),
        ],
    )

    result = planner.plan(goal, dataset)

    assert result.blueprint is not None
    assert result.blueprint.goal_id == "goal_compare_performance"
    assert "cap_descriptive_statistics" in result.execution_order
    assert "cap_ttest_analysis" in result.execution_order
    assert result.planner_confidence > 0.7


def test_unsupported_dataset_skips_incompatible_capabilities():
    planner = InvestigationPlannerService(
        goal_registry=build_default_goal_registry(),
        capability_registry=build_default_capability_registry(),
    )
    goal = planner.goal_registry.get_by_id("goal_explain_decline")
    assert goal is not None

    dataset = _dataset_profile(
        name="text_only_dataset",
        rows=12,
        columns=1,
        column_profiles=[
            ColumnProfile(name="notes", data_type="object", text=True),
        ],
    )

    result = planner.plan(goal, dataset)

    assert result.execution_order == []
    assert result.skipped_capabilities
    assert any("unsupported semantic primitives" in skipped.reason for skipped in result.skipped_capabilities)
    assert any("No required capabilities are executable" in warning for warning in result.planning_warnings)


def test_missing_capability_metadata_is_reported():
    goal_registry = BusinessGoalRegistry()
    capability_registry = AnalysisCapabilityRegistry()

    goal_registry.register(
        BusinessGoal(
            goal_id="goal_missing_cap",
            name="Missing Capability Goal",
            description="Goal referencing unknown capability.",
            business_purpose=BusinessPurpose.DESCRIBE,
            common_business_questions=["What is available?"],
            applicable_investigation_stages=[InvestigationStageName.OBSERVE],
            required_analytical_capabilities=["cap_unknown"],
            optional_analytical_capabilities=[],
            supported_semantic_primitives=[SemanticPrimitive.NUMERIC],
            tags=["missing"],
            version="1.0.0",
        )
    )

    planner = InvestigationPlannerService(goal_registry=goal_registry, capability_registry=capability_registry)
    goal = goal_registry.get_by_id("goal_missing_cap")
    assert goal is not None

    dataset = _dataset_profile(
        name="numeric",
        rows=10,
        columns=1,
        column_profiles=[
            ColumnProfile(name="value", data_type="int64", continuous=True, can_average=True),
        ],
    )

    result = planner.plan(goal, dataset)

    assert len(result.skipped_capabilities) == 1
    assert result.skipped_capabilities[0].capability_id == "cap_unknown"
    assert "metadata not found" in result.skipped_capabilities[0].reason


def test_dependency_resolution_adds_and_orders_dependencies():
    goal_registry = BusinessGoalRegistry()
    capability_registry = AnalysisCapabilityRegistry()

    capability_registry.register(
        AnalysisCapability(
            capability_id="cap_child",
            display_name="Child",
            description="Dependency capability",
            investigation_stage=CapabilityStage.OBSERVE,
            business_purpose=BusinessPurpose.DESCRIBE,
            required_input_types=["dataset_profile"],
            supported_semantic_primitives=[SemanticPrimitive.NUMERIC],
            expected_outputs=["child_output"],
            execution_constraints=ExecutionConstraints(minimum_rows=1),
            dependencies=[],
            tags=["dependency"],
            maturity_level=MaturityLevel.STABLE,
            version="1.0.0",
            plugin_key="Child Plugin",
        )
    )
    capability_registry.register(
        AnalysisCapability(
            capability_id="cap_parent",
            display_name="Parent",
            description="Parent capability",
            investigation_stage=CapabilityStage.EXPLAIN,
            business_purpose=BusinessPurpose.DIAGNOSE,
            required_input_types=["dataset_profile"],
            supported_semantic_primitives=[SemanticPrimitive.NUMERIC],
            expected_outputs=["parent_output"],
            execution_constraints=ExecutionConstraints(minimum_rows=1),
            dependencies=["cap_child"],
            tags=["parent"],
            maturity_level=MaturityLevel.STABLE,
            version="1.0.0",
            plugin_key="Parent Plugin",
        )
    )

    goal_registry.register(
        BusinessGoal(
            goal_id="goal_dependency",
            name="Dependency Goal",
            description="Ensures dependency resolution",
            business_purpose=BusinessPurpose.DIAGNOSE,
            common_business_questions=["What depends on what?"],
            applicable_investigation_stages=[InvestigationStageName.OBSERVE, InvestigationStageName.EXPLAIN],
            required_analytical_capabilities=["cap_parent"],
            optional_analytical_capabilities=[],
            supported_semantic_primitives=[SemanticPrimitive.NUMERIC],
            tags=["dependency"],
            version="1.0.0",
        )
    )

    planner = InvestigationPlannerService(goal_registry=goal_registry, capability_registry=capability_registry)
    goal = goal_registry.get_by_id("goal_dependency")
    assert goal is not None

    dataset = _dataset_profile(
        name="dependency_dataset",
        rows=20,
        columns=1,
        column_profiles=[
            ColumnProfile(name="value", data_type="float64", continuous=True, can_average=True),
        ],
    )

    result = planner.plan(goal, dataset)

    assert result.execution_order == ["cap_child", "cap_parent"]
    selected_by_id = {item.capability_id: item for item in result.selected_capabilities}
    assert selected_by_id["cap_parent"].requested_as == "required"
    assert selected_by_id["cap_child"].requested_as == "dependency"


def test_planner_confidence_decreases_when_required_capabilities_fail():
    planner = InvestigationPlannerService(
        goal_registry=build_default_goal_registry(),
        capability_registry=build_default_capability_registry(),
    )

    goal = planner.goal_registry.get_by_id("goal_compare_performance")
    assert goal is not None

    supported_dataset = _dataset_profile(
        name="supported",
        rows=40,
        columns=2,
        column_profiles=[
            ColumnProfile(name="value", data_type="float64", continuous=True, can_average=True),
            ColumnProfile(name="group", data_type="object", categorical=True, can_group=True),
        ],
    )
    unsupported_dataset = _dataset_profile(
        name="unsupported",
        rows=4,
        columns=1,
        column_profiles=[
            ColumnProfile(name="comment", data_type="object", text=True),
        ],
    )

    supported_result = planner.plan(goal, supported_dataset)
    unsupported_result = planner.plan(goal, unsupported_dataset)

    assert supported_result.planner_confidence > unsupported_result.planner_confidence


def test_skipped_capability_reporting_contains_reason_and_type():
    planner = InvestigationPlannerService(
        goal_registry=build_default_goal_registry(),
        capability_registry=build_default_capability_registry(),
    )
    goal = planner.goal_registry.get_by_id("goal_validate_hypothesis")
    assert goal is not None

    dataset = _dataset_profile(
        name="tiny_dataset",
        rows=2,
        columns=1,
        column_profiles=[
            ColumnProfile(name="only_text", data_type="object", text=True),
        ],
    )

    result = planner.plan(goal, dataset)

    assert result.skipped_capabilities
    assert all(item.reason for item in result.skipped_capabilities)
    assert all(item.requested_as in {"required", "optional", "dependency"} for item in result.skipped_capabilities)