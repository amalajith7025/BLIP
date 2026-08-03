import numpy as np
import pandas as pd
import pytest

from app.analysis.profiler import DataProfiler
from app.analysis.plugins.pca_analysis import PCAAnalysis


def test_validate_returns_true_for_numeric_dataset():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0],
            "y": [4.0, 5.0, 6.0],
        }
    )
    profile = DataProfiler().profile(dataset)

    plugin = PCAAnalysis()

    assert plugin.validate(profile) is True


def test_validate_returns_false_for_fewer_than_two_numeric_columns():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0],
            "group": ["a", "b", "a"],
        }
    )
    profile = DataProfiler().profile(dataset)

    plugin = PCAAnalysis()

    assert plugin.validate(profile) is False


def test_execute_returns_expected_top_level_structure():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0, 4.0],
            "y": [2.0, 3.0, 4.0, 5.0],
            "z": [3.0, 4.0, 5.0, 6.0],
        }
    )
    plugin = PCAAnalysis()
    results = plugin.execute(dataset)

    assert set(results.keys()) == {
        "explained_variance_ratio",
        "cumulative_variance",
        "eigenvalues",
        "components",
        "number_of_components",
        "samples_used",
        "features_used",
    }


def test_execute_computes_pca_for_multiple_numeric_columns():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0, 4.0],
            "y": [1.0, 4.0, 9.0, 16.0],
            "z": [2.0, 3.0, 5.0, 7.0],
        }
    )
    plugin = PCAAnalysis()
    results = plugin.execute(dataset)

    assert results["number_of_components"] == 3
    assert results["samples_used"] == 4
    assert results["features_used"] == 3


def test_explained_variance_ratio_is_valid():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0, 4.0],
            "y": [2.0, 4.0, 6.0, 8.0],
            "z": [1.0, 3.0, 5.0, 7.0],
        }
    )
    plugin = PCAAnalysis()
    results = plugin.execute(dataset)

    ratio = results["explained_variance_ratio"]

    assert all(isinstance(value, float) for value in ratio)
    assert sum(ratio) == pytest.approx(1.0, rel=1e-6)
    assert all(0.0 <= value <= 1.0 for value in ratio)


def test_cumulative_variance_is_increasing_and_ends_at_one():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0, 4.0],
            "y": [2.0, 4.0, 6.0, 8.0],
            "z": [1.0, 3.0, 5.0, 7.0],
        }
    )
    plugin = PCAAnalysis()
    results = plugin.execute(dataset)

    cumulative = results["cumulative_variance"]

    assert cumulative == sorted(cumulative)
    assert cumulative[-1] == pytest.approx(1.0, rel=1e-6)


def test_components_contain_expected_structure():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0, 4.0],
            "y": [4.0, 5.0, 6.0, 7.0],
            "z": [7.0, 8.0, 9.0, 10.0],
        }
    )
    plugin = PCAAnalysis()
    results = plugin.execute(dataset)

    assert isinstance(results["components"], list)
    assert len(results["components"]) == results["number_of_components"]

    for component in results["components"]:
        assert set(component.keys()) == {"component", "loadings"}
        assert isinstance(component["component"], str)
        assert isinstance(component["loadings"], dict)
        assert set(component["loadings"].keys()) == {"x", "y", "z"}
        assert all(isinstance(value, float) for value in component["loadings"].values())


def test_execute_ignores_rows_with_nan_values():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0, 4.0],
            "y": [2.0, np.nan, 6.0, 8.0],
            "z": [3.0, 4.0, 5.0, np.nan],
        }
    )
    plugin = PCAAnalysis()
    results = plugin.execute(dataset)

    assert "samples_used" in results
    assert results["samples_used"] == 2
    assert results["features_used"] == 3


def test_execute_returns_empty_dict_when_too_few_rows_remain():
    dataset = pd.DataFrame(
        {
            "x": [1.0, np.nan],
            "y": [2.0, np.nan],
            "z": [3.0, np.nan],
        }
    )
    plugin = PCAAnalysis()
    results = plugin.execute(dataset)

    assert results == {}


def test_explain_returns_required_keys():
    plugin = PCAAnalysis()
    explanation = plugin.explain({})

    assert set(explanation.keys()) == {
        "explained_variance_ratio",
        "cumulative_variance",
        "eigenvalues",
        "components",
        "number_of_components",
        "samples_used",
        "features_used",
    }


def test_observations_returns_expected_structure():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0, 4.0],
            "y": [4.0, 5.0, 6.0, 7.0],
            "z": [7.0, 8.0, 9.0, 10.0],
        }
    )
    plugin = PCAAnalysis()
    results = plugin.execute(dataset)
    observations = plugin.observations(results)

    assert isinstance(observations, dict)
    assert "pca" in observations
    assert isinstance(observations["pca"], list)
    assert len(observations["pca"]) >= 1


def test_observations_handles_empty_results():
    plugin = PCAAnalysis()
    observations = plugin.observations({})

    assert isinstance(observations, dict)
    assert observations == {"": ["PCA could not be performed."]}


def test_execute_returns_native_python_types_only():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0, 4.0],
            "y": [2.0, 4.0, 6.0, 8.0],
            "z": [1.0, 3.0, 5.0, 7.0],
        }
    )
    plugin = PCAAnalysis()
    results = plugin.execute(dataset)

    assert isinstance(results["explained_variance_ratio"], list)
    assert isinstance(results["cumulative_variance"], list)
    assert isinstance(results["eigenvalues"], list)
    assert isinstance(results["components"], list)
    assert isinstance(results["number_of_components"], int)
    assert isinstance(results["samples_used"], int)
    assert isinstance(results["features_used"], int)

    for value in results["explained_variance_ratio"]:
        assert isinstance(value, float)
        assert not isinstance(value, np.floating)
    for value in results["cumulative_variance"]:
        assert isinstance(value, float)
        assert not isinstance(value, np.floating)
    for value in results["eigenvalues"]:
        assert isinstance(value, float)
        assert not isinstance(value, np.floating)

    for component in results["components"]:
        assert isinstance(component["component"], str)
        assert isinstance(component["loadings"], dict)
        for loading_value in component["loadings"].values():
            assert isinstance(loading_value, float)
            assert not isinstance(loading_value, np.floating)


def test_execute_supports_more_than_two_numeric_columns():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0, 4.0],
            "y": [1.0, 2.0, 3.0, 4.0],
            "z": [2.0, 4.0, 6.0, 8.0],
            "w": [1.0, 3.0, 5.0, 7.0],
        }
    )
    plugin = PCAAnalysis()
    results = plugin.execute(dataset)

    assert results["features_used"] == 4
    assert results["number_of_components"] == 4


def test_execute_is_deterministic_for_same_dataset():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0, 4.0, 5.0],
            "y": [5.0, 4.0, 3.0, 2.0, 1.0],
            "z": [2.0, 3.0, 4.0, 5.0, 6.0],
        }
    )
    plugin = PCAAnalysis()
    results_one = plugin.execute(dataset)
    results_two = plugin.execute(dataset)

    assert results_one == results_two
