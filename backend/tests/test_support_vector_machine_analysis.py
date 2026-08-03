import numpy as np
import pandas as pd
import pytest

from app.analysis.engine import AnalysisEngine
from app.analysis.profiler import DataProfiler
from app.analysis.plugins.support_vector_machine_analysis import SupportVectorMachineAnalysis


def test_plugin_metadata():
    plugin = SupportVectorMachineAnalysis()

    assert plugin.name == "Support Vector Machine"
    assert plugin.description == (
        "Builds a support vector machine classifier for binary classification."
    )


def test_validate_returns_true_with_numeric_and_binary_categorical_columns():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0],
            "target": ["a", "b", "a"],
        }
    )
    profile = DataProfiler().profile(dataset)

    plugin = SupportVectorMachineAnalysis()

    assert plugin.validate(profile) is True


def test_validate_returns_false_for_numeric_only_dataset():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0],
            "y": [4.0, 5.0, 6.0],
        }
    )
    profile = DataProfiler().profile(dataset)

    plugin = SupportVectorMachineAnalysis()

    assert plugin.validate(profile) is False


def test_validate_returns_false_for_categorical_only_dataset():
    dataset = pd.DataFrame(
        {
            "group": ["a", "b", "a"],
            "label": ["x", "y", "x"],
        }
    )
    profile = DataProfiler().profile(dataset)

    plugin = SupportVectorMachineAnalysis()

    assert plugin.validate(profile) is False


def test_validate_returns_false_for_more_than_two_classes_in_target():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0, 4.0],
            "target": ["a", "b", "c", "a"],
        }
    )
    profile = DataProfiler().profile(dataset)

    plugin = SupportVectorMachineAnalysis()

    assert plugin.validate(profile) is False


def test_execute_returns_expected_structure():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            "y": [2.0, 1.0, 4.0, 3.0, 6.0, 5.0],
            "target": ["a", "a", "a", "b", "b", "b"],
        }
    )
    plugin = SupportVectorMachineAnalysis()
    results = plugin.execute(dataset)

    assert set(results.keys()) == {
        "samples_used",
        "predictors",
        "target",
        "classes",
        "accuracy",
        "support_vectors",
        "kernel",
    }


def test_execute_returns_empty_dict_when_dataset_is_empty():
    dataset = pd.DataFrame({})
    plugin = SupportVectorMachineAnalysis()
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
    plugin = SupportVectorMachineAnalysis()
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
    plugin = SupportVectorMachineAnalysis()
    results = plugin.execute(dataset)

    assert results == {}


def test_execute_returns_empty_dict_when_no_numeric_predictor_columns_remain():
    dataset = pd.DataFrame(
        {
            "group": ["a", "b", "a", "b", "a"],
            "target": ["a", "b", "a", "b", "a"],
        }
    )
    plugin = SupportVectorMachineAnalysis()
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
    plugin = SupportVectorMachineAnalysis()
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
    plugin = SupportVectorMachineAnalysis()
    results = plugin.execute(dataset)

    assert results["samples_used"] == 6
    assert results["predictors"] == ["feature_1", "feature_2"]
    assert results["target"] == "target"
    assert results["classes"] == ["a", "b"]
    assert results["kernel"] == "linear"


def test_execute_returns_python_native_types_only():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            "y": [2.0, 1.0, 4.0, 3.0, 6.0, 5.0],
            "target": ["a", "a", "a", "b", "b", "b"],
        }
    )
    plugin = SupportVectorMachineAnalysis()
    results = plugin.execute(dataset)

    assert isinstance(results["samples_used"], int)
    assert isinstance(results["predictors"], list)
    assert isinstance(results["target"], str)
    assert isinstance(results["classes"], list)
    assert isinstance(results["accuracy"], float)
    assert isinstance(results["support_vectors"], int)
    assert isinstance(results["kernel"], str)
    assert 0.0 <= results["accuracy"] <= 1.0
    assert results["kernel"] == "linear"
    assert all(
        not isinstance(value, np.integer)
        for value in [results["samples_used"], results["support_vectors"]]
    )
    assert all(
        not isinstance(value, np.floating)
        for value in [results["accuracy"]]
    )


def test_explain_returns_required_keys():
    plugin = SupportVectorMachineAnalysis()
    explanation = plugin.explain({})

    assert set(explanation.keys()) == {
        "samples_used",
        "predictors",
        "target",
        "classes",
        "accuracy",
        "support_vectors",
        "kernel",
    }


def test_observations_returns_expected_structure():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            "y": [2.0, 1.0, 4.0, 3.0, 6.0, 5.0],
            "target": ["a", "a", "a", "b", "b", "b"],
        }
    )
    plugin = SupportVectorMachineAnalysis()
    results = plugin.execute(dataset)
    observations = plugin.observations(results)

    assert isinstance(observations, dict)
    assert "support_vector_machine" in observations
    assert isinstance(observations["support_vector_machine"], list)
    assert len(observations["support_vector_machine"]) >= 1


def test_observations_handles_empty_results():
    plugin = SupportVectorMachineAnalysis()
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
    plugin = SupportVectorMachineAnalysis()
    observations = plugin.observations(plugin.execute(dataset))

    assert isinstance(observations, dict)
    assert "support_vector_machine" in observations
    assert all(
        isinstance(item, str)
        for item in observations["support_vector_machine"]
    )


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

    assert "Support Vector Machine" in applicable_names
