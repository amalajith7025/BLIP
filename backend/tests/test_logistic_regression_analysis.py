import numpy as np
import pandas as pd

from app.analysis.engine import AnalysisEngine
from app.analysis.profiler import DataProfiler
from app.analysis.plugins.logistic_regression_analysis import LogisticRegressionAnalysis


def test_plugin_metadata():
    plugin = LogisticRegressionAnalysis()

    assert plugin.name == "Logistic Regression"
    assert plugin.description == (
        "Builds a logistic regression model for binary classification."
    )


def test_validate_returns_true_with_numeric_and_binary_categorical_columns():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0],
            "target": ["a", "b", "a"],
        }
    )
    profile = DataProfiler().profile(dataset)

    plugin = LogisticRegressionAnalysis()

    assert plugin.validate(profile) is True


def test_validate_returns_false_for_numeric_only_dataset():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0],
            "y": [4.0, 5.0, 6.0],
        }
    )
    profile = DataProfiler().profile(dataset)

    plugin = LogisticRegressionAnalysis()

    assert plugin.validate(profile) is False


def test_validate_returns_false_for_categorical_only_dataset():
    dataset = pd.DataFrame(
        {
            "group": ["a", "b", "a"],
            "label": ["x", "y", "x"],
        }
    )
    profile = DataProfiler().profile(dataset)

    plugin = LogisticRegressionAnalysis()

    assert plugin.validate(profile) is False


def test_validate_returns_false_for_more_than_two_classes_in_target():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0, 4.0],
            "target": ["a", "b", "c", "a"],
        }
    )
    profile = DataProfiler().profile(dataset)

    plugin = LogisticRegressionAnalysis()

    assert plugin.validate(profile) is False


def test_execute_returns_expected_structure():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            "y": [2.0, 3.0, 4.0, 5.0, 6.0, 7.0],
            "target": ["a", "a", "a", "b", "b", "b"],
        }
    )
    plugin = LogisticRegressionAnalysis()
    results = plugin.execute(dataset)

    assert set(results.keys()) == {
        "samples_used",
        "features_used",
        "target",
        "classes",
        "coefficients",
        "intercept",
        "accuracy",
        "iterations",
        "converged",
    }


def test_execute_returns_empty_dict_when_fewer_than_two_complete_observations_remain():
    dataset = pd.DataFrame(
        {
            "x": [1.0, np.nan, np.nan],
            "target": ["a", np.nan, np.nan],
        }
    )
    plugin = LogisticRegressionAnalysis()
    results = plugin.execute(dataset)

    assert results == {}


def test_execute_ignores_rows_containing_missing_values():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0, np.nan, 5.0, 6.0],
            "y": [2.0, 3.0, np.nan, 5.0, 6.0, 7.0],
            "target": ["a", "a", "b", "b", "b", np.nan],
        }
    )
    plugin = LogisticRegressionAnalysis()
    results = plugin.execute(dataset)

    assert results["samples_used"] == 3
    assert results["target"] == "target"
    assert results["features_used"] == ["x", "y"]
    assert results["classes"] == ["a", "b"]


def test_execute_selects_binary_target_and_numeric_features():
    dataset = pd.DataFrame(
        {
            "feature_1": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            "feature_2": [2.0, 1.0, 4.0, 3.0, 6.0, 5.0],
            "target": ["a", "a", "a", "b", "b", "b"],
        }
    )
    plugin = LogisticRegressionAnalysis()
    results = plugin.execute(dataset)

    assert results["samples_used"] == 6
    assert results["features_used"] == ["feature_1", "feature_2"]
    assert results["target"] == "target"
    assert results["classes"] == ["a", "b"]
    assert isinstance(results["coefficients"], dict)
    assert isinstance(results["classes"], list)
    assert all(isinstance(item, str) for item in results["classes"])
    assert isinstance(results["features_used"], list)
    assert isinstance(results["intercept"], float)
    assert isinstance(results["accuracy"], float)
    assert 0.0 <= results["accuracy"] <= 1.0
    assert isinstance(results["iterations"], int)
    assert isinstance(results["converged"], bool)


def test_execute_returns_python_native_types_only():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            "y": [2.0, 1.0, 4.0, 3.0, 6.0, 5.0],
            "target": ["a", "a", "a", "b", "b", "b"],
        }
    )
    plugin = LogisticRegressionAnalysis()
    results = plugin.execute(dataset)

    assert isinstance(results["samples_used"], int)
    assert isinstance(results["features_used"], list)
    assert isinstance(results["target"], str)
    assert isinstance(results["classes"], list)
    assert isinstance(results["coefficients"], dict)
    assert isinstance(results["intercept"], float)
    assert isinstance(results["accuracy"], float)
    assert isinstance(results["iterations"], int)
    assert isinstance(results["converged"], bool)
    assert 0.0 <= results["accuracy"] <= 1.0


def test_explain_returns_required_keys():
    plugin = LogisticRegressionAnalysis()
    explanation = plugin.explain({})

    assert set(explanation.keys()) == {
        "samples_used",
        "features_used",
        "target",
        "classes",
        "coefficients",
        "intercept",
        "accuracy",
        "iterations",
        "converged",
    }


def test_observations_returns_expected_structure():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            "y": [2.0, 1.0, 4.0, 3.0, 6.0, 5.0],
            "target": ["a", "a", "a", "b", "b", "b"],
        }
    )
    plugin = LogisticRegressionAnalysis()
    results = plugin.execute(dataset)
    observations = plugin.observations(results)

    assert isinstance(observations, dict)
    assert "logistic_regression" in observations
    assert isinstance(observations["logistic_regression"], list)
    assert len(observations["logistic_regression"]) >= 1


def test_observations_handles_empty_results():
    plugin = LogisticRegressionAnalysis()
    observations = plugin.observations({})

    assert isinstance(observations, dict)
    assert observations == {"": ["Very small dataset used."]}


def test_observations_produces_objective_observations_only():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            "y": [2.0, 1.0, 4.0, 3.0, 6.0, 5.0],
            "target": ["a", "a", "a", "b", "b", "b"],
        }
    )
    plugin = LogisticRegressionAnalysis()
    observations = plugin.observations(plugin.execute(dataset))

    allowed_observations = {
        "Model converged successfully.",
        "High classification accuracy observed.",
        "Low classification accuracy observed.",
        "Very small dataset used.",
        "Multiple predictor variables were included.",
    }

    assert all(
        item in allowed_observations
        for item in observations["logistic_regression"]
    )


def test_selected_by_analysis_registry_for_valid_dataset():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            "y": [2.0, 1.0, 4.0, 3.0, 6.0, 5.0],
            "target": ["a", "a", "a", "b", "b", "b"],
        }
    )
    engine = AnalysisEngine()
    profile = engine.profiler.profile(dataset)
    applicable_names = {plugin.name for plugin in engine.registry.applicable(profile)}

    assert "Logistic Regression" in applicable_names
