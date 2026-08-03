import numpy as np
import pandas as pd

from app.analysis.engine import AnalysisEngine
from app.analysis.profiler import DataProfiler
from app.analysis.plugins.hierarchical_clustering_analysis import HierarchicalClusteringAnalysis


def test_plugin_metadata():
    plugin = HierarchicalClusteringAnalysis()

    assert plugin.name == "Hierarchical Clustering"
    assert plugin.description == (
        "Groups similar observations using agglomerative hierarchical clustering."
    )


def test_validate_returns_true_with_two_numeric_columns():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0],
            "y": [4.0, 5.0, 6.0],
        }
    )
    profile = DataProfiler().profile(dataset)

    plugin = HierarchicalClusteringAnalysis()

    assert plugin.validate(profile) is True


def test_validate_returns_false_with_one_numeric_column():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0],
            "group": ["a", "b", "a"],
        }
    )
    profile = DataProfiler().profile(dataset)

    plugin = HierarchicalClusteringAnalysis()

    assert plugin.validate(profile) is False


def test_validate_returns_false_for_categorical_only_dataset():
    dataset = pd.DataFrame(
        {
            "a": ["x", "y", "x"],
            "b": ["u", "v", "u"],
        }
    )
    profile = DataProfiler().profile(dataset)

    plugin = HierarchicalClusteringAnalysis()

    assert plugin.validate(profile) is False


def test_execute_returns_expected_structure():
    dataset = pd.DataFrame(
        {
            "x": [0.0, 0.0, 10.0, 10.0, 20.0, 20.0],
            "y": [0.0, 0.5, 10.0, 10.5, 20.0, 20.5],
            "z": [0.0, 1.0, 10.0, 11.0, 20.0, 21.0],
        }
    )
    plugin = HierarchicalClusteringAnalysis()
    results = plugin.execute(dataset)

    assert set(results.keys()) == {
        "samples_used",
        "features_used",
        "cluster_count",
        "cluster_sizes",
    }


def test_execute_returns_empty_dict_when_fewer_than_two_complete_rows_remain():
    dataset = pd.DataFrame(
        {
            "x": [1.0, np.nan],
            "y": [2.0, np.nan],
            "z": [3.0, np.nan],
        }
    )
    plugin = HierarchicalClusteringAnalysis()
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
    plugin = HierarchicalClusteringAnalysis()
    results = plugin.execute(dataset)

    assert results["samples_used"] == 4
    assert results["features_used"] == ["x", "y", "z"]
    assert results["cluster_count"] == 3


def test_execute_supports_multiple_numeric_columns():
    dataset = pd.DataFrame(
        {
            "x": [0.0, 0.0, 10.0, 10.0, 20.0, 20.0],
            "y": [0.0, 0.5, 10.0, 10.5, 20.0, 20.5],
            "z": [0.0, 1.0, 10.0, 11.0, 20.0, 21.0],
        }
    )
    plugin = HierarchicalClusteringAnalysis()
    results = plugin.execute(dataset)

    assert results["samples_used"] == 6
    assert results["features_used"] == ["x", "y", "z"]
    assert results["cluster_count"] == 3
    assert isinstance(results["cluster_sizes"], dict)
    assert set(results["cluster_sizes"].keys()) == {
        "Cluster 0",
        "Cluster 1",
        "Cluster 2",
    }
    assert sum(results["cluster_sizes"].values()) == results["samples_used"]


def test_execute_returns_python_native_types_only():
    dataset = pd.DataFrame(
        {
            "x": [0.0, 0.0, 10.0, 10.0, 20.0, 20.0],
            "y": [0.0, 0.5, 10.0, 10.5, 20.0, 20.5],
            "z": [0.0, 1.0, 10.0, 11.0, 20.0, 21.0],
        }
    )
    plugin = HierarchicalClusteringAnalysis()
    results = plugin.execute(dataset)

    assert isinstance(results["samples_used"], int)
    assert isinstance(results["cluster_count"], int)
    assert isinstance(results["cluster_sizes"], dict)
    assert isinstance(results["features_used"], list)
    assert all(isinstance(key, str) for key in results["features_used"])
    assert all(
        isinstance(size, int) and not isinstance(size, np.integer)
        for size in results["cluster_sizes"].values()
    )
    assert sum(results["cluster_sizes"].values()) == results["samples_used"]


def test_explain_returns_required_keys():
    plugin = HierarchicalClusteringAnalysis()
    explanation = plugin.explain({})

    assert set(explanation.keys()) == {
        "samples_used",
        "features_used",
        "cluster_count",
        "cluster_sizes",
    }


def test_observations_returns_expected_structure():
    dataset = pd.DataFrame(
        {
            "x": [0.0, 0.0, 10.0, 10.0, 20.0, 20.0],
            "y": [0.0, 0.5, 10.0, 10.5, 20.0, 20.5],
            "z": [0.0, 1.0, 10.0, 11.0, 20.0, 21.0],
        }
    )
    plugin = HierarchicalClusteringAnalysis()
    results = plugin.execute(dataset)
    observations = plugin.observations(results)

    assert isinstance(observations, dict)
    assert "hierarchical_clustering" in observations
    assert isinstance(observations["hierarchical_clustering"], list)
    assert len(observations["hierarchical_clustering"]) >= 1


def test_observations_handles_empty_results():
    plugin = HierarchicalClusteringAnalysis()
    observations = plugin.observations({})

    assert isinstance(observations, dict)
    assert observations == {"": ["Very small dataset used."]}


def test_observations_produces_objective_observations_only():
    dataset = pd.DataFrame(
        {
            "x": [0.0, 0.0, 10.0, 10.0, 20.0, 20.0],
            "y": [0.0, 0.5, 10.0, 10.5, 20.0, 20.5],
            "z": [0.0, 1.0, 10.0, 11.0, 20.0, 21.0],
        }
    )
    plugin = HierarchicalClusteringAnalysis()
    observations = plugin.observations(plugin.execute(dataset))

    allowed_observations = {
        "Very small dataset used.",
        "Multiple clusters identified.",
        "Cluster sizes are relatively balanced.",
        "One cluster dominates the dataset.",
    }

    assert all(
        item in allowed_observations
        for item in observations["hierarchical_clustering"]
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

    assert "Hierarchical Clustering" in applicable_names
