import numpy as np
import pandas as pd
import pytest

from app.analysis.engine import AnalysisEngine
from app.analysis.profiler import DataProfiler
from app.analysis.plugins.decision_tree_analysis import DecisionTreeAnalysis


def test_plugin_metadata():
    plugin = DecisionTreeAnalysis()

    assert plugin.name == "Decision Tree"
    assert plugin.description == (
        "Builds a decision tree classifier for binary classification."
    )


def test_validate_returns_true_with_numeric_and_binary_categorical_columns():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0],
            "target": ["a", "b", "a"],
        }
    )
    profile = DataProfiler().profile(dataset)

    plugin = DecisionTreeAnalysis()

    assert plugin.validate(profile) is True


def test_validate_returns_false_for_numeric_only_dataset():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0],
            "y": [4.0, 5.0, 6.0],
        }
    )
    profile = DataProfiler().profile(dataset)

    plugin = DecisionTreeAnalysis()

    assert plugin.validate(profile) is False


def test_validate_returns_false_for_categorical_only_dataset():
    dataset = pd.DataFrame(
        {
            "group": ["a", "b", "a"],
            "label": ["x", "y", "x"],
        }
    )
    profile = DataProfiler().profile(dataset)

    plugin = DecisionTreeAnalysis()

    assert plugin.validate(profile) is False


def test_validate_returns_false_for_more_than_two_classes_in_target():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0, 4.0],
            "target": ["a", "b", "c", "a"],
        }
    )
    profile = DataProfiler().profile(dataset)

    plugin = DecisionTreeAnalysis()

    assert plugin.validate(profile) is False


def test_execute_returns_expected_structure():
    dataset = pd.DataFrame(
        {
            "feature_1": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            "feature_2": [2.0, 1.0, 4.0, 3.0, 6.0, 5.0],
            "target": ["a", "a", "a", "b", "b", "b"],
        }
    )
    plugin = DecisionTreeAnalysis()
    results = plugin.execute(dataset)

    assert set(results.keys()) == {
        "samples_used",
        "features_used",
        "target",
        "classes",
        "accuracy",
        "tree_depth",
        "leaf_count",
        "feature_importance",
    }


def test_execute_returns_empty_dict_when_fewer_than_five_complete_observations_remain():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0, 4.0, np.nan, np.nan],
            "y": [2.0, 3.0, 4.0, 5.0, np.nan, np.nan],
            "target": ["a", "a", "b", "b", "a", "b"],
        }
    )
    plugin = DecisionTreeAnalysis()
    results = plugin.execute(dataset)

    assert results == {}


def test_execute_returns_empty_dict_when_fewer_than_two_target_classes_remain():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0, 4.0, 5.0],
            "y": [2.0, 3.0, 4.0, 5.0, 6.0],
            "target": ["a", "a", "a", "a", "a"],
        }
    )
    plugin = DecisionTreeAnalysis()
    results = plugin.execute(dataset)

    assert results == {}


def test_execute_returns_empty_dict_when_no_numeric_predictor_columns_remain():
    dataset = pd.DataFrame(
        {
            "group": ["a", "b", "a", "b", "a"],
            "target": ["a", "b", "a", "b", "a"],
        }
    )
    plugin = DecisionTreeAnalysis()
    results = plugin.execute(dataset)

    assert results == {}


def test_execute_ignores_rows_containing_missing_values():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0, 4.0, 5.0, np.nan, np.nan],
            "y": [2.0, 1.0, 4.0, 3.0, 6.0, np.nan, 7.0],
            "target": ["a", "a", "a", "b", "b", "a", np.nan],
        }
    )
    plugin = DecisionTreeAnalysis()
    results = plugin.execute(dataset)

    assert results["samples_used"] == 5
    assert results["target"] == "target"
    assert results["features_used"] == ["x", "y"]
    assert results["classes"] == ["a", "b"]


def test_execute_automatically_detects_binary_target_and_numeric_predictors():
    dataset = pd.DataFrame(
        {
            "feature_1": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            "feature_2": [2.0, 1.0, 4.0, 3.0, 6.0, 5.0],
            "target": ["a", "a", "a", "b", "b", "b"],
        }
    )
    plugin = DecisionTreeAnalysis()
    results = plugin.execute(dataset)

    assert results["samples_used"] == 6
    assert results["target"] == "target"
    assert results["features_used"] == ["feature_1", "feature_2"]
    assert results["classes"] == ["a", "b"]


def test_execute_supports_multiple_numeric_predictor_columns():
    dataset = pd.DataFrame(
        {
            "feature_1": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            "feature_2": [2.0, 1.0, 4.0, 3.0, 6.0, 5.0],
            "feature_3": [3.0, 5.0, 1.0, 7.0, 2.0, 8.0],
            "target": ["a", "a", "b", "b", "b", "a"],
        }
    )
    plugin = DecisionTreeAnalysis()
    results = plugin.execute(dataset)

    assert results["samples_used"] == 6
    assert results["features_used"] == ["feature_1", "feature_2", "feature_3"]
    assert isinstance(results["feature_importance"], dict)
    assert set(results["feature_importance"].keys()) == set(results["features_used"])
    assert sum(results["feature_importance"].values()) == pytest.approx(1.0, rel=1e-6)
    assert 0.0 <= results["accuracy"] <= 1.0
    assert isinstance(results["tree_depth"], int)
    assert results["tree_depth"] >= 1
    assert isinstance(results["leaf_count"], int)
    assert results["leaf_count"] >= 2


def test_execute_returns_python_native_types_only():
    dataset = pd.DataFrame(
        {
            "feature_1": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            "feature_2": [2.0, 1.0, 4.0, 3.0, 6.0, 5.0],
            "target": ["a", "a", "a", "b", "b", "b"],
        }
    )
    plugin = DecisionTreeAnalysis()
    results = plugin.execute(dataset)

    assert isinstance(results["samples_used"], int)
    assert isinstance(results["features_used"], list)
    assert isinstance(results["target"], str)
    assert isinstance(results["classes"], list)
    assert isinstance(results["accuracy"], float)
    assert isinstance(results["tree_depth"], int)
    assert isinstance(results["leaf_count"], int)
    assert isinstance(results["feature_importance"], dict)
    assert 0.0 <= results["accuracy"] <= 1.0
    assert results["tree_depth"] >= 1
    assert results["leaf_count"] >= 2
    assert all(
        not isinstance(value, np.integer)
        for value in [results["samples_used"], results["tree_depth"], results["leaf_count"]]
    )
    assert all(
        not isinstance(value, np.floating)
        for value in [results["accuracy"]]
    )
    assert all(
        isinstance(value, float) and not isinstance(value, np.floating)
        for value in results["feature_importance"].values()
    )


def test_explain_returns_required_keys():
    plugin = DecisionTreeAnalysis()
    explanation = plugin.explain({})

    assert set(explanation.keys()) == {
        "samples_used",
        "features_used",
        "target",
        "classes",
        "accuracy",
        "tree_depth",
        "leaf_count",
        "feature_importance",
    }


def test_observations_returns_expected_structure():
    dataset = pd.DataFrame(
        {
            "feature_1": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            "feature_2": [2.0, 1.0, 4.0, 3.0, 6.0, 5.0],
            "target": ["a", "a", "a", "b", "b", "b"],
        }
    )
    plugin = DecisionTreeAnalysis()
    results = plugin.execute(dataset)
    observations = plugin.observations(results)

    assert isinstance(observations, dict)
    assert "decision_tree" in observations
    assert isinstance(observations["decision_tree"], list)
    assert len(observations["decision_tree"]) >= 1


def test_observations_handles_empty_results():
    plugin = DecisionTreeAnalysis()
    observations = plugin.observations({})

    assert isinstance(observations, dict)
    assert observations == {"": ["Very small dataset used."]}


def test_observations_produces_objective_observations_only():
    dataset = pd.DataFrame(
        {
            "feature_1": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            "feature_2": [2.0, 1.0, 4.0, 3.0, 6.0, 5.0],
            "target": ["a", "a", "a", "b", "b", "b"],
        }
    )
    plugin = DecisionTreeAnalysis()
    observations = plugin.observations(plugin.execute(dataset))

    allowed_observations = {
        "High classification accuracy observed.",
        "Low classification accuracy observed.",
        "Tree depth is shallow.",
        "Tree depth is relatively large.",
        "One predictor contributes most of the importance.",
        "Feature importance is relatively balanced.",
        "Very small dataset used.",
    }

    assert all(
        item in allowed_observations
        for item in observations["decision_tree"]
    )


def test_selected_by_analysis_registry_for_valid_dataset():
    dataset = pd.DataFrame(
        {
            "feature_1": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            "feature_2": [2.0, 1.0, 4.0, 3.0, 6.0, 5.0],
            "target": ["a", "a", "a", "b", "b", "b"],
        }
    )
    engine = AnalysisEngine()
    profile = engine.profiler.profile(dataset)
    applicable_names = {plugin.name for plugin in engine.registry.applicable(profile)}

    assert "Decision Tree" in applicable_names
