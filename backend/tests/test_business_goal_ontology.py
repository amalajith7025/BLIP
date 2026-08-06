import pytest

from app.analysis.capabilities import build_default_capability_registry
from app.analysis.capabilities.schemas import BusinessPurpose
from app.business_goals import (
    BusinessGoal,
    BusinessGoalRegistry,
    build_default_goal_registry,
    build_goal_capability_blueprint,
)


def test_default_goal_registry_seeds_universal_goals():
    registry = build_default_goal_registry()
    goals = registry.list_available()

    expected_names = {
        "Explain Decline",
        "Explain Growth",
        "Compare Performance",
        "Rank Entities",
        "Segment Population",
        "Detect Anomalies",
        "Discover Relationships",
        "Forecast Trends",
        "Validate Hypothesis",
        "Measure Change",
        "Optimize Performance",
    }

    assert len(goals) == 11
    assert {goal.name for goal in goals} == expected_names


def test_register_and_get_goal_by_id():
    registry = BusinessGoalRegistry()
    goal = BusinessGoal(
        goal_id="goal_custom",
        name="Custom Goal",
        description="Custom description",
        business_purpose=BusinessPurpose.DESCRIBE,
        common_business_questions=["What is happening?"],
        applicable_investigation_stages=[],
        required_analytical_capabilities=["cap_descriptive_statistics"],
        optional_analytical_capabilities=[],
        supported_semantic_primitives=[],
        tags=["custom"],
        version="1.0.0",
    )

    registry.register(goal)

    found = registry.get_by_id("goal_custom")
    assert found is not None
    assert found.name == "Custom Goal"


def test_search_by_business_purpose():
    registry = build_default_goal_registry()

    compare_goals = registry.search_by_business_purpose(BusinessPurpose.COMPARE)

    assert compare_goals
    assert all(goal.business_purpose == BusinessPurpose.COMPARE for goal in compare_goals)


def test_retrieve_required_and_optional_capabilities():
    registry = build_default_goal_registry()

    required = registry.get_required_capabilities("goal_explain_decline")
    optional = registry.get_optional_capabilities("goal_explain_decline")

    assert required == ["cap_descriptive_statistics", "cap_correlation_analysis"]
    assert "cap_regression_analysis" in optional


def test_registry_validates_required_fields():
    registry = BusinessGoalRegistry()

    with pytest.raises(ValueError, match="goal_id"):
        registry.register(
            BusinessGoal(
                goal_id="",
                name="Invalid",
                description="Invalid",
                business_purpose=BusinessPurpose.DESCRIBE,
                common_business_questions=[],
                applicable_investigation_stages=[],
                required_analytical_capabilities=["cap_descriptive_statistics"],
                optional_analytical_capabilities=[],
                supported_semantic_primitives=[],
                tags=[],
                version="1.0.0",
            )
        )

    with pytest.raises(ValueError, match="required_analytical_capabilities"):
        registry.register(
            BusinessGoal(
                goal_id="goal_invalid",
                name="Invalid",
                description="Invalid",
                business_purpose=BusinessPurpose.DESCRIBE,
                common_business_questions=[],
                applicable_investigation_stages=[],
                required_analytical_capabilities=[],
                optional_analytical_capabilities=[],
                supported_semantic_primitives=[],
                tags=[],
                version="1.0.0",
            )
        )


def test_build_goal_capability_blueprint_returns_metadata_only():
    goal_registry = build_default_goal_registry()
    capability_registry = build_default_capability_registry()

    blueprint = build_goal_capability_blueprint(
        goal_id="goal_compare_performance",
        goal_registry=goal_registry,
        capability_registry=capability_registry,
    )

    assert set(blueprint.keys()) == {"required", "optional"}
    assert all(hasattr(capability, "capability_id") for capability in blueprint["required"])
    assert all(hasattr(capability, "plugin_key") for capability in blueprint["required"])
    assert all(not hasattr(capability, "execute") for capability in blueprint["required"])


def test_missing_goal_capability_lookup_raises_key_error():
    registry = build_default_goal_registry()

    with pytest.raises(KeyError):
        registry.get_required_capabilities("goal_missing")