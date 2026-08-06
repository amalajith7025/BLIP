import pandas as pd

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
from app.analysis.engine import AnalysisEngine
from app.analysis.schemas import ColumnProfile, DatasetProfile
from app.business_goals.registry import BusinessGoalRegistry
from app.business_goals.schemas import BusinessGoal
from app.business_goals.services import build_default_goal_registry
from app.investigation_framework.schemas import InvestigationStageName
from app.investigation_framework.services import InvestigationOrchestrationService
from app.investigation_workflow.services import InvestigationWorkflowService
from app.planning.schemas import InvestigationBlueprint, PlanningResult


def _numeric_profile(name: str, rows: int, columns: int = 1) -> DatasetProfile:
    profiles = [
        ColumnProfile(
            name="value",
            data_type="float64",
            continuous=True,
            can_average=True,
            can_correlate=True,
        )
    ]
    if columns > 1:
        profiles.append(
            ColumnProfile(
                name="group",
                data_type="object",
                categorical=True,
                can_group=True,
                can_count=True,
            )
        )

    return DatasetProfile(
        name=name,
        rows=rows,
        columns=columns,
        column_profiles=profiles,
    )


def test_successful_investigation_execution():
    service = InvestigationWorkflowService()
    goal = build_default_goal_registry().get_by_id("goal_rank_entities")
    assert goal is not None

    dataset = pd.DataFrame(
        {
            "value": [10, 11, 9, 10, 12, 9, 14, 11, 10],
            "group": ["A", "B", "A", "A", "B", "B", "A", "B", "A"],
        }
    )
    profile = _numeric_profile("rank_dataset", rows=len(dataset), columns=2)

    result = service.execute_investigation(profile, goal, dataset)

    assert result.execution_summary is not None
    assert result.execution_summary.total_executed >= 1
    assert result.findings_collection is not None
    assert result.findings_collection.investigation_id
    assert result.analysis_results
    assert result.confidence > 0
    assert result.execution_duration_ms >= 0


def test_unsupported_dataset_returns_skips_and_warnings():
    service = InvestigationWorkflowService()
    goal = build_default_goal_registry().get_by_id("goal_detect_anomalies")
    assert goal is not None

    dataset = pd.DataFrame({"notes": ["a", "b", "c", "d", "e", "f"]})
    profile = DatasetProfile(
        name="text_dataset",
        rows=6,
        columns=1,
        column_profiles=[
            ColumnProfile(name="notes", data_type="object", text=True),
        ],
    )

    result = service.execute_investigation(profile, goal, dataset)

    assert result.execution_summary is not None
    assert result.execution_summary.total_executed == 0
    assert result.findings_collection is not None
    assert result.findings_collection.findings == []
    assert result.skipped_capabilities
    assert any("No required capabilities are executable" in warning for warning in result.warnings)


def test_partial_execution_when_some_plugins_are_unavailable():
    goal_registry = BusinessGoalRegistry()
    capability_registry = build_default_capability_registry()

    capability_registry.register(
        AnalysisCapability(
            capability_id="cap_missing_plugin",
            display_name="Missing Plugin Capability",
            description="Capability metadata exists but plugin does not.",
            investigation_stage=CapabilityStage.OBSERVE,
            business_purpose=BusinessPurpose.DESCRIBE,
            required_input_types=["dataset_profile"],
            supported_semantic_primitives=[SemanticPrimitive.NUMERIC],
            expected_outputs=["missing_output"],
            execution_constraints=ExecutionConstraints(minimum_rows=1, minimum_columns=1),
            dependencies=[],
            tags=["missing-plugin"],
            maturity_level=MaturityLevel.BETA,
            version="1.0.0",
            plugin_key="Plugin Not Registered",
        )
    )

    goal_registry.register(
        BusinessGoal(
            goal_id="goal_partial",
            name="Partial Goal",
            description="One executable and one unavailable capability.",
            business_purpose=BusinessPurpose.DESCRIBE,
            common_business_questions=["What can execute?"],
            applicable_investigation_stages=[InvestigationStageName.OBSERVE],
            required_analytical_capabilities=["cap_descriptive_statistics"],
            optional_analytical_capabilities=["cap_missing_plugin"],
            supported_semantic_primitives=[SemanticPrimitive.NUMERIC],
            tags=["partial"],
            version="1.0.0",
        )
    )

    service = InvestigationWorkflowService(
        capability_registry=capability_registry,
        planner=None,
    )
    service.planner.goal_registry = goal_registry

    dataset = pd.DataFrame({"value": [1, 2, 3, 4, 5]})
    dataset["group"] = ["A", "B", "A", "B", "A"]
    profile = _numeric_profile("partial_dataset", rows=5, columns=2)
    goal = goal_registry.get_by_id("goal_partial")
    assert goal is not None

    result = service.execute_investigation(profile, goal, dataset)

    assert result.execution_summary is not None
    assert result.execution_summary.total_executed >= 1
    assert result.execution_summary.total_skipped >= 1
    assert any(item.status == "skipped" for item in result.executed_capabilities)


def test_execution_failures_are_captured_without_crashing_pipeline():
    class FailingPlugin:
        name = "Failing Plugin"
        description = "Always fails"

        def validate(self, profile):
            return True

        def execute(self, dataset):
            raise RuntimeError("forced plugin failure")

        def explain(self, results):
            return {}

        def observations(self, results):
            return {}

    capability_registry = AnalysisCapabilityRegistry()
    capability_registry.register(
        AnalysisCapability(
            capability_id="cap_failing",
            display_name="Failing Capability",
            description="Used to test failure handling.",
            investigation_stage=CapabilityStage.OBSERVE,
            business_purpose=BusinessPurpose.DESCRIBE,
            required_input_types=["dataset_profile"],
            supported_semantic_primitives=[SemanticPrimitive.NUMERIC],
            expected_outputs=["none"],
            execution_constraints=ExecutionConstraints(minimum_rows=1, minimum_columns=1),
            dependencies=[],
            tags=["failing"],
            maturity_level=MaturityLevel.EXPERIMENTAL,
            version="1.0.0",
            plugin_key="Failing Plugin",
        )
    )

    goal_registry = BusinessGoalRegistry()
    goal_registry.register(
        BusinessGoal(
            goal_id="goal_failing",
            name="Failing Goal",
            description="For failure handling test.",
            business_purpose=BusinessPurpose.DESCRIBE,
            common_business_questions=["Can pipeline handle failures?"],
            applicable_investigation_stages=[InvestigationStageName.OBSERVE],
            required_analytical_capabilities=["cap_failing"],
            optional_analytical_capabilities=[],
            supported_semantic_primitives=[SemanticPrimitive.NUMERIC],
            tags=["failure"],
            version="1.0.0",
        )
    )

    analysis_engine = AnalysisEngine()
    analysis_engine.registry.register(FailingPlugin())

    service = InvestigationWorkflowService(
        capability_registry=capability_registry,
        analysis_engine=analysis_engine,
    )
    service.planner.goal_registry = goal_registry

    dataset = pd.DataFrame({"value": [1, 2, 3]})
    profile = _numeric_profile("failing_dataset", rows=3, columns=1)
    goal = goal_registry.get_by_id("goal_failing")
    assert goal is not None

    result = service.execute_investigation(profile, goal, dataset)

    assert result.execution_summary is not None
    assert result.execution_summary.total_failed == 1
    assert any(item.status == "failed" for item in result.executed_capabilities)
    assert any("failed during execution" in warning for warning in result.warnings)


def test_planner_integration_uses_planner_output_blueprint():
    class StubPlanner:
        def __init__(self):
            self.called = False

        def plan(self, goal, dataset_profile):
            self.called = True
            blueprint = InvestigationBlueprint(
                goal_id=goal.goal_id,
                goal_name=goal.name,
                dataset_name=dataset_profile.name,
                execution_order=["cap_descriptive_statistics"],
                stage_capability_order={
                    InvestigationStageName.OBSERVE: ["cap_descriptive_statistics"],
                    InvestigationStageName.UNDERSTAND: [],
                    InvestigationStageName.EXPLAIN: [],
                    InvestigationStageName.VALIDATE: [],
                    InvestigationStageName.RECOMMEND: [],
                    InvestigationStageName.LEARN: [],
                },
                metadata={"planner": "stub"},
            )
            return PlanningResult(
                selected_capabilities=[],
                skipped_capabilities=[],
                planning_warnings=[],
                execution_order=["cap_descriptive_statistics"],
                compatibility_report={},
                planner_confidence=0.9,
                blueprint=blueprint,
                metadata={"source": "stub"},
            )

    planner = StubPlanner()
    service = InvestigationWorkflowService(planner=planner)
    goal = build_default_goal_registry().get_by_id("goal_rank_entities")
    assert goal is not None

    dataset = pd.DataFrame({"value": [2, 4, 6]})
    profile = _numeric_profile("planner_dataset", rows=3, columns=1)

    result = service.execute_investigation(profile, goal, dataset)

    assert planner.called is True
    assert result.execution_summary is not None
    assert result.execution_summary.total_executed >= 1


def test_framework_integration_executes_through_framework_service():
    class SpyFramework:
        def __init__(self):
            self.called = False
            self.delegate = InvestigationOrchestrationService()

        def execute(self, investigation):
            self.called = True
            return self.delegate.execute(investigation)

    framework = SpyFramework()
    service = InvestigationWorkflowService(framework=framework)

    goal = build_default_goal_registry().get_by_id("goal_rank_entities")
    assert goal is not None

    dataset = pd.DataFrame({"value": [1, 3, 5, 7]})
    profile = _numeric_profile("framework_dataset", rows=4, columns=1)

    result = service.execute_investigation(profile, goal, dataset)

    assert framework.called is True
    assert result.execution_summary is not None
    assert result.execution_summary.framework_status.value == "completed"