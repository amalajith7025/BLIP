import numpy as np
import pandas as pd

from app.analysis.engine import AnalysisEngine
from app.analysis.profiler import DataProfiler
from app.analysis.plugins.kmeans_analysis import KMeansAnalysis


def test_plugin_metadata():
    plugin = KMeansAnalysis()

    assert plugin.name == "K-Means Clustering"
    assert plugin.description == (
        "Groups similar observations into clusters using the K-Means clustering algorithm."
    )


def test_validate_returns_true_with_two_numeric_columns():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0],
            "y": [4.0, 5.0, 6.0],
        }
    )
    profile = DataProfiler().profile(dataset)

    plugin = KMeansAnalysis()

    assert plugin.validate(profile) is True


def test_validate_returns_false_with_one_numeric_column():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0],
            "group": ["a", "b", "a"],
        }
    )
    profile = DataProfiler().profile(dataset)

    plugin = KMeansAnalysis()

    assert plugin.validate(profile) is False


def test_validate_returns_false_for_categorical_only_dataset():
    dataset = pd.DataFrame(
        {
            "a": ["x", "y", "x"],
            "b": ["u", "v", "u"],
        }
    )
    profile = DataProfiler().profile(dataset)

    plugin = KMeansAnalysis()

    assert plugin.validate(profile) is False


def test_execute_returns_expected_structure():
    dataset = pd.DataFrame(
        {
            "x": [0.0, 0.5, 10.0, 10.5, 20.0, 20.5],
            "y": [0.0, 0.5, 10.0, 10.5, 0.0, 0.5],
        }
    )
    plugin = KMeansAnalysis()
    results = plugin.execute(dataset)

    assert set(results.keys()) == {
        "samples_used",
        "features_used",
        "cluster_count",
        "cluster_sizes",
        "inertia",
        "cluster_centers",
    }


def test_execute_returns_empty_dict_when_fewer_than_two_complete_rows_remain():
    dataset = pd.DataFrame(
        {
            "x": [1.0, np.nan],
            "y": [2.0, np.nan],
        }
    )
    plugin = KMeansAnalysis()
    results = plugin.execute(dataset)

    assert results == {}


def test_execute_ignores_rows_containing_missing_values():
    dataset = pd.DataFrame(
        {
            "x": [0.0, 0.5, 10.0, np.nan, 20.0, 20.5],
            "y": [0.0, 0.5, 10.0, 10.5, np.nan, 0.5],
            "z": [1.0, 1.0, 11.0, 11.0, 1.0, np.nan],
        }
    )
    plugin = KMeansAnalysis()
    results = plugin.execute(dataset)

    assert results["samples_used"] == 3
    assert results["features_used"] == ["x", "y", "z"]
    assert results["cluster_count"] == 3


def test_execute_supports_multiple_numeric_columns():
    dataset = pd.DataFrame(
        {
            "x": [0.0, 0.5, 10.0, 10.5, 20.0, 20.5],
            "y": [0.0, 0.5, 10.0, 10.5, 0.0, 0.5],
            "z": [1.0, 1.0, 11.0, 11.0, 1.0, 1.0],
        }
    )
    plugin = KMeansAnalysis()
    results = plugin.execute(dataset)

    assert results["samples_used"] == 6
    assert results["features_used"] == ["x", "y", "z"]
    assert results["cluster_count"] == 3
    assert set(results["cluster_sizes"].keys()) == {
        "Cluster 0",
        "Cluster 1",
        "Cluster 2",
    }
    assert isinstance(results["inertia"], float)
    assert isinstance(results["cluster_centers"], list)
    assert len(results["cluster_centers"]) == 3
    assert all(isinstance(center, list) for center in results["cluster_centers"])


def test_execute_returns_python_native_types_only():
    dataset = pd.DataFrame(
        {
            "x": [0.0, 0.5, 10.0, 10.5, 20.0, 20.5],
            "y": [0.0, 0.5, 10.0, 10.5, 0.0, 0.5],
        }
    )
    plugin = KMeansAnalysis()
    results = plugin.execute(dataset)

    assert isinstance(results["samples_used"], int)
    assert isinstance(results["cluster_count"], int)
    assert isinstance(results["cluster_sizes"], dict)
    assert isinstance(results["inertia"], float)
    assert isinstance(results["cluster_centers"], list)
    assert not any(
        isinstance(value, np.integer) or isinstance(value, np.floating)
        for value in [results["samples_used"], results["cluster_count"], results["inertia"]]
    )

    for center in results["cluster_centers"]:
        assert isinstance(center, list)
        for value in center:
            assert isinstance(value, float)
            assert not isinstance(value, np.floating)

    for size in results["cluster_sizes"].values():
        assert isinstance(size, int)
        assert not isinstance(size, np.integer)


def test_explain_returns_required_keys():
    plugin = KMeansAnalysis()
    explanation = plugin.explain({})

    assert set(explanation.keys()) == {
        "cluster_count",
        "cluster_sizes",
        "inertia",
        "cluster_centers",
        "samples_used",
        "features_used",
    }


def test_observations_returns_expected_structure():
    dataset = pd.DataFrame(
        {
            "x": [0.0, 0.5, 10.0, 10.5, 20.0, 20.5],
            "y": [0.0, 0.5, 10.0, 10.5, 0.0, 0.5],
            "z": [1.0, 1.0, 11.0, 11.0, 1.0, 1.0],
        }
    )
    plugin = KMeansAnalysis()
    results = plugin.execute(dataset)
    observations = plugin.observations(results)

    assert isinstance(observations, dict)
    assert all(isinstance(value, list) for value in observations.values())
    assert len(observations["kmeans"]) >= 1


def test_observations_handles_empty_results():
    plugin = KMeansAnalysis()
    observations = plugin.observations({})

    assert isinstance(observations, dict)
    assert observations == {"": ["Very small dataset used."]}


def test_observations_produces_objective_observations_only():
    dataset = pd.DataFrame(
        {
            "x": [0.0, 0.5, 10.0, 10.5, 20.0, 20.5],
            "y": [0.0, 0.5, 10.0, 10.5, 0.0, 0.5],
            "z": [1.0, 1.0, 11.0, 11.0, 1.0, 1.0],
        }
    )
    plugin = KMeansAnalysis()
    observations = plugin.observations(plugin.execute(dataset))

    assert all(
        item in {
            "Very small dataset used.",
            "Multiple clusters identified.",
            "Cluster sizes are relatively balanced.",
            "One cluster dominates the dataset.",
            "Low within-cluster variation observed.",
            "High within-cluster variation observed.",
        }
        for item in observations["kmeans"]
    )


def test_registered_in_analysis_engine():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0],
            "y": [4.0, 5.0, 6.0],
        }
    )
    engine = AnalysisEngine()
    profile = engine.profiler.profile(dataset)
    applicable_names = {plugin.name for plugin in engine.registry.applicable(profile)}

    assert "K-Means Clustering" in applicable_names


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

    assert "K-Means Clustering" in applicable_names
