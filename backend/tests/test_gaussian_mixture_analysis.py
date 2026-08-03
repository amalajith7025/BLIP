import numpy as np
import pandas as pd

from app.analysis.engine import AnalysisEngine
from app.analysis.profiler import DataProfiler
from app.analysis.plugins.gaussian_mixture_analysis import GaussianMixtureAnalysis


def test_plugin_metadata():
    plugin = GaussianMixtureAnalysis()

    assert plugin.name == "Gaussian Mixture Model"
    assert plugin.description == (
        "Groups observations into probabilistic clusters using Gaussian Mixture Models."
    )


def test_validate_returns_true_with_two_numeric_columns():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0],
            "y": [4.0, 5.0, 6.0],
        }
    )
    profile = DataProfiler().profile(dataset)

    plugin = GaussianMixtureAnalysis()

    assert plugin.validate(profile) is True


def test_validate_returns_false_with_one_numeric_column():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0],
            "group": ["a", "b", "a"],
        }
    )
    profile = DataProfiler().profile(dataset)

    plugin = GaussianMixtureAnalysis()

    assert plugin.validate(profile) is False


def test_validate_returns_false_for_categorical_only_dataset():
    dataset = pd.DataFrame(
        {
            "a": ["x", "y", "x"],
            "b": ["u", "v", "u"],
        }
    )
    profile = DataProfiler().profile(dataset)

    plugin = GaussianMixtureAnalysis()

    assert plugin.validate(profile) is False


def test_execute_returns_expected_structure():
    dataset = pd.DataFrame(
        {
            "x": [0.0, 0.0, 10.0, 10.0, 20.0, 20.0],
            "y": [0.0, 0.5, 10.0, 10.5, 20.0, 20.5],
            "z": [0.0, 1.0, 10.0, 11.0, 20.0, 21.0],
        }
    )
    plugin = GaussianMixtureAnalysis()
    results = plugin.execute(dataset)

    assert set(results.keys()) == {
        "samples_used",
        "features_used",
        "component_count",
        "component_sizes",
        "weights",
        "means",
        "converged",
        "iterations",
    }


def test_execute_returns_empty_dict_when_fewer_than_two_complete_rows_remain():
    dataset = pd.DataFrame(
        {
            "x": [1.0, np.nan],
            "y": [2.0, np.nan],
            "z": [3.0, np.nan],
        }
    )
    plugin = GaussianMixtureAnalysis()
    results = plugin.execute(dataset)

    assert results == {}


def test_execute_ignores_rows_containing_missing_values():
    dataset = pd.DataFrame(
        {
            "x": [0.0, 0.0, 10.0, 10.0, np.nan, 20.0],
            "y": [0.0, 0.5, 10.0, 10.5, 20.0, np.nan],
            "z": [0.0, 1.0, 10.0, 11.0, 20.0, np.nan],
        }
    )
    plugin = GaussianMixtureAnalysis()
    results = plugin.execute(dataset)

    assert results["samples_used"] == 4
    assert results["features_used"] == ["x", "y", "z"]
    assert results["component_count"] == 3
    assert isinstance(results["component_sizes"], dict)
    assert isinstance(results["weights"], list)
    assert isinstance(results["means"], list)


def test_execute_supports_multiple_numeric_columns():
    dataset = pd.DataFrame(
        {
            "x": [0.0, 0.0, 0.0, 10.0, 10.0, 10.0, 20.0, 20.0, 20.0],
            "y": [0.0, 0.5, 1.0, 10.0, 10.5, 11.0, 20.0, 20.5, 21.0],
            "z": [0.0, 1.0, 2.0, 10.0, 11.0, 12.0, 20.0, 21.0, 22.0],
        }
    )
    plugin = GaussianMixtureAnalysis()
    results = plugin.execute(dataset)

    assert results["samples_used"] == 9
    assert results["features_used"] == ["x", "y", "z"]
    assert results["component_count"] == 3
    assert isinstance(results["component_sizes"], dict)
    assert isinstance(results["weights"], list)
    assert isinstance(results["means"], list)
    assert len(results["weights"]) == 3
    assert len(results["means"]) == 3
    assert all(isinstance(mean, list) for mean in results["means"])
    assert sum(results["component_sizes"].values()) == results["samples_used"]


def test_execute_returns_python_native_types_only():
    dataset = pd.DataFrame(
        {
            "x": [0.0, 0.0, 10.0, 10.0, 20.0, 20.0],
            "y": [0.0, 0.5, 10.0, 10.5, 20.0, 20.5],
            "z": [0.0, 1.0, 10.0, 11.0, 20.0, 21.0],
        }
    )
    plugin = GaussianMixtureAnalysis()
    results = plugin.execute(dataset)

    assert isinstance(results["samples_used"], int)
    assert isinstance(results["component_count"], int)
    assert isinstance(results["component_sizes"], dict)
    assert isinstance(results["weights"], list)
    assert isinstance(results["means"], list)
    assert isinstance(results["converged"], bool)
    assert isinstance(results["iterations"], int)

    assert all(
        isinstance(size, int) and not isinstance(size, np.integer)
        for size in results["component_sizes"].values()
    )
    assert all(
        isinstance(weight, float) and not isinstance(weight, np.floating)
        for weight in results["weights"]
    )
    assert all(
        isinstance(mean_value, float) and not isinstance(mean_value, np.floating)
        for row in results["means"]
        for mean_value in row
    )


def test_explain_returns_required_keys():
    plugin = GaussianMixtureAnalysis()
    explanation = plugin.explain({})

    assert set(explanation.keys()) == {
        "samples_used",
        "features_used",
        "component_count",
        "component_sizes",
        "weights",
        "means",
        "converged",
        "iterations",
    }


def test_observations_returns_expected_structure():
    dataset = pd.DataFrame(
        {
            "x": [0.0, 0.0, 0.0, 10.0, 10.0, 10.0, 20.0, 20.0, 20.0],
            "y": [0.0, 0.5, 1.0, 10.0, 10.5, 11.0, 20.0, 20.5, 21.0],
            "z": [0.0, 1.0, 2.0, 10.0, 11.0, 12.0, 20.0, 21.0, 22.0],
        }
    )
    plugin = GaussianMixtureAnalysis()
    results = plugin.execute(dataset)
    observations = plugin.observations(results)

    assert isinstance(observations, dict)
    assert "gaussian_mixture" in observations
    assert isinstance(observations["gaussian_mixture"], list)
    assert len(observations["gaussian_mixture"]) >= 1


def test_observations_handles_empty_results():
    plugin = GaussianMixtureAnalysis()
    observations = plugin.observations({})

    assert isinstance(observations, dict)
    assert observations == {"": ["Very small dataset used."]}


def test_observations_produces_objective_observations_only():
    dataset = pd.DataFrame(
        {
            "x": [0.0, 0.0, 0.0, 10.0, 10.0, 10.0, 20.0, 20.0, 20.0],
            "y": [0.0, 0.5, 1.0, 10.0, 10.5, 11.0, 20.0, 20.5, 21.0],
            "z": [0.0, 1.0, 2.0, 10.0, 11.0, 12.0, 20.0, 21.0, 22.0],
        }
    )
    plugin = GaussianMixtureAnalysis()
    observations = plugin.observations(plugin.execute(dataset))

    allowed_observations = {
        "Model converged successfully.",
        "Model required multiple iterations.",
        "Components are relatively balanced.",
        "One component dominates the dataset.",
        "Very small dataset used.",
    }

    assert all(
        item in allowed_observations
        for item in observations["gaussian_mixture"]
    )


def test_selected_by_analysis_registry_for_numeric_dataset():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0],
            "y": [4.0, 5.0, 6.0],
        }
    )
    engine = AnalysisEngine()
    profile = engine.profiler.profile(dataset)
    applicable_names = {plugin.name for plugin in engine.registry.applicable(profile)}

    assert "Gaussian Mixture Model" in applicable_names
