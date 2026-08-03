import numpy as np
import pandas as pd
import pytest

from app.analysis.engine import AnalysisEngine
from app.analysis.profiler import DataProfiler
from app.analysis.plugins.quadratic_discriminant_analysis import QuadraticDiscriminantAnalysis


def test_plugin_metadata():
    plugin = QuadraticDiscriminantAnalysis()

    assert plugin.name == "Quadratic Discriminant Analysis"
    assert plugin.description == "Builds a Quadratic Discriminant Analysis classifier for binary classification."


def test_validate_returns_true_with_numeric_and_binary_categorical_columns():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0],
            "target": ["a", "b", "a"],
        }
    )
    profile = DataProfiler().profile(dataset)

    plugin = QuadraticDiscriminantAnalysis()

    assert plugin.validate(profile) is True


def test_validate_returns_false_for_numeric_only_dataset():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0],
            "y": [4.0, 5.0, 6.0],
        }
    )
    profile = DataProfiler().profile(dataset)

    plugin = QuadraticDiscriminantAnalysis()

    assert plugin.validate(profile) is False


def test_validate_returns_false_for_categorical_only_dataset():
    dataset = pd.DataFrame(
        {
            "group": ["a", "b", "a"],
            "label": ["x", "y", "x"],
        }
    )
    profile = DataProfiler().profile(dataset)

    plugin = QuadraticDiscriminantAnalysis()

    assert plugin.validate(profile) is False


def test_validate_returns_false_for_non_binary_target():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0, 4.0],
            "target": ["a", "b", "c", "a"],
        }
    )
    profile = DataProfiler().profile(dataset)

    plugin = QuadraticDiscriminantAnalysis()

    assert plugin.validate(profile) is False


def test_execute_returns_expected_structure():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            "y": [2.0, 1.0, 4.0, 3.0, 6.0, 5.0],
            "target": ["a", "a", "a", "b", "b", "b"],
        }
    )
    plugin = QuadraticDiscriminantAnalysis()
    results = plugin.execute(dataset)

    assert set(results.keys()) == {
        "samples_used",
        "predictors",
        "target",
        "classes",
        "accuracy",
        "priors",
        "regularization",
    }


def test_execute_returns_empty_dict_when_dataset_is_empty():
    dataset = pd.DataFrame({})
    plugin = QuadraticDiscriminantAnalysis()
    results = plugin.execute(dataset)

    assert results == {}


def test_execute_returns_empty_dict_when_fewer_than_five_complete_observations_remain():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0, 4.0, np.nan, np.nan],
            "y": [2.0, 3.0, 4.0, 5.0, np.nan, np.nan],
            "target": ["a", "a", "b", "b", "a", "b"],
        }
    )
    plugin = QuadraticDiscriminantAnalysis()
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
    plugin = QuadraticDiscriminantAnalysis()
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
    plugin = QuadraticDiscriminantAnalysis()
    results = plugin.execute(dataset)

    assert results["samples_used"] == 5
    assert results["target"] == "target"
    assert results["predictors"] == ["x", "y"]
    assert results["classes"] == ["a", "b"]


def test_execute_automatically_detects_binary_target_and_numeric_predictors():
    dataset = pd.DataFrame(
        {
            "feature_1": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            "feature_2": [2.0, 1.0, 4.0, 3.0, 6.0, 5.0],
            "target": ["a", "a", "a", "b", "b", "b"],
        }
    )
    plugin = QuadraticDiscriminantAnalysis()
    results = plugin.execute(dataset)

    assert results["samples_used"] == 6
    assert results["target"] == "target"
    assert results["predictors"] == ["feature_1", "feature_2"]
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
    plugin = QuadraticDiscriminantAnalysis()
    results = plugin.execute(dataset)

    assert results["samples_used"] == 6
    assert results["predictors"] == ["feature_1", "feature_2", "feature_3"]
    assert isinstance(results["priors"], list)
    assert isinstance(results["regularization"], float)
    assert 0.0 <= results["accuracy"] <= 1.0


def test_execute_returns_python_native_types_only():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            "y": [2.0, 1.0, 4.0, 3.0, 6.0, 5.0],
            "target": ["a", "a", "a", "b", "b", "b"],
        }
    )
    plugin = QuadraticDiscriminantAnalysis()
    results = plugin.execute(dataset)

    assert isinstance(results["samples_used"], int)
    assert isinstance(results["predictors"], list)
    assert isinstance(results["target"], str)
    assert isinstance(results["classes"], list)
    assert isinstance(results["accuracy"], float)
    assert isinstance(results["priors"], list)
    assert isinstance(results["regularization"], float)
    assert 0.0 <= results["accuracy"] <= 1.0
    assert all(
        not isinstance(value, np.integer)
        for value in [results["samples_used"]]
    )
    assert all(
        not isinstance(value, np.floating)
        for value in [results["accuracy"], results["regularization"]]
    )
    assert all(
        isinstance(value, float) and not isinstance(value, np.floating)
        for value in results["priors"]
    )


def test_explain_returns_required_keys():
    plugin = QuadraticDiscriminantAnalysis()
    explanation = plugin.explain({})

    assert set(explanation.keys()) == {
        "samples_used",
        "predictors",
        "target",
        "classes",
        "accuracy",
        "priors",
        "regularization",
    }


def test_observations_returns_expected_structure():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            "y": [2.0, 1.0, 4.0, 3.0, 6.0, 5.0],
            "target": ["a", "a", "a", "b", "b", "b"],
        }
    )
    plugin = QuadraticDiscriminantAnalysis()
    observations = plugin.observations(plugin.execute(dataset))

    assert isinstance(observations, dict)
    assert "quadratic_discriminant_analysis" in observations
    assert isinstance(observations["quadratic_discriminant_analysis"], list)
    assert len(observations["quadratic_discriminant_analysis"]) >= 1


def test_observations_handles_empty_results():
    plugin = QuadraticDiscriminantAnalysis()
    observations = plugin.observations({})

    assert isinstance(observations, dict)
    assert observations == {"": ["Very small dataset used."]}


def test_selected_by_analysis_registry_for_valid_dataset():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            "y": [2.0, 3.0, 4.0, 5.0, 6.0, 7.0],
            "target": ["a", "a", "a", "b", "b", "b"],
        }
    )
    engine = AnalysisEngine()
    profile = engine.profiler.profile(dataset)
    applicable_names = {plugin.name for plugin in engine.registry.applicable(profile)}

    assert "Quadratic Discriminant Analysis" in applicable_names
