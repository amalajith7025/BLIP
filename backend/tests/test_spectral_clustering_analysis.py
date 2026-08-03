import numpy as np
import pandas as pd

from app.analysis.engine import AnalysisEngine
from app.analysis.profiler import DataProfiler
from app.analysis.plugins.spectral_clustering_analysis import SpectralClusteringAnalysis


def test_plugin_metadata():
    plugin = SpectralClusteringAnalysis()

    assert plugin.name == "Spectral Clustering"


def test_validate_returns_true_with_two_numeric_columns():
    dataset = pd.DataFrame({"x": [1.0, 2.0, 3.0], "y": [4.0, 5.0, 6.0]})
    profile = DataProfiler().profile(dataset)

    plugin = SpectralClusteringAnalysis()
    assert plugin.validate(profile) is True


def test_validate_returns_false_with_one_numeric_column():
    dataset = pd.DataFrame({"x": [1.0, 2.0, 3.0], "group": ["a", "b", "a"]})
    profile = DataProfiler().profile(dataset)

    plugin = SpectralClusteringAnalysis()
    assert plugin.validate(profile) is False


def test_execute_returns_expected_structure():
    dataset = pd.DataFrame({
        "x": [0.0, 0.5, 10.0, 10.5, 20.0],
        "y": [0.0, 0.5, 10.0, 10.5, 0.0],
    })
    plugin = SpectralClusteringAnalysis()
    results = plugin.execute(dataset)

    assert set(results.keys()) == {"samples_used", "features", "clusters", "cluster_sizes", "affinity"}


def test_execute_returns_empty_dict_when_fewer_than_five_complete_rows_remain():
    dataset = pd.DataFrame({"x": [1.0, np.nan, np.nan], "y": [2.0, np.nan, np.nan]})
    plugin = SpectralClusteringAnalysis()
    results = plugin.execute(dataset)

    assert results == {}


def test_execute_ignores_rows_containing_missing_values():
    dataset = pd.DataFrame({
        "x": [0.0, 0.5, 10.0, np.nan, 20.0],
        "y": [0.0, 0.5, 10.0, 10.5, np.nan],
        "z": [1.0, 1.0, 11.0, 11.0, 1.0],
    })
    plugin = SpectralClusteringAnalysis()
    results = plugin.execute(dataset)

    # fewer than five complete observations remain -> should return {}
    assert results == {}


def test_execute_supports_multiple_numeric_columns():
    dataset = pd.DataFrame({
        "x": [0.0, 0.5, 10.0, 10.5, 20.0, 20.5],
        "y": [0.0, 0.5, 10.0, 10.5, 0.0, 0.5],
        "z": [1.0, 1.0, 11.0, 11.0, 1.0, 1.0],
    })
    plugin = SpectralClusteringAnalysis()
    results = plugin.execute(dataset)

    assert results["samples_used"] == 6
    assert set(results["cluster_sizes"].keys()) == set(range(results["clusters"]))
    assert results["affinity"] == "nearest_neighbors"


def test_execute_returns_python_native_types_only():
    dataset = pd.DataFrame({
        "x": [0.0, 0.5, 10.0, 10.5, 20.0, 20.5],
        "y": [0.0, 0.5, 10.0, 10.5, 0.0, 0.5],
    })
    plugin = SpectralClusteringAnalysis()
    results = plugin.execute(dataset)

    assert isinstance(results["samples_used"], int)
    assert isinstance(results["clusters"], int)
    assert isinstance(results["cluster_sizes"], dict)
    assert isinstance(results["affinity"], str)


def test_explain_returns_required_keys():
    plugin = SpectralClusteringAnalysis()
    explanation = plugin.explain({})

    assert set(explanation.keys()) == {"samples_used", "features", "clusters", "cluster_sizes", "affinity"}


def test_observations_returns_expected_structure():
    dataset = pd.DataFrame({
        "x": [0.0, 0.5, 10.0, 10.5, 20.0, 20.5],
        "y": [0.0, 0.5, 10.0, 10.5, 0.0, 0.5],
        "z": [1.0, 1.0, 11.0, 11.0, 1.0, 1.0],
    })
    plugin = SpectralClusteringAnalysis()
    observations = plugin.observations(plugin.execute(dataset))

    assert isinstance(observations, dict)
    assert "spectral_clustering" in observations


def test_observations_handles_empty_results():
    plugin = SpectralClusteringAnalysis()
    observations = plugin.observations({})

    assert observations == {"": ["Very small dataset used."]}


def test_registered_in_analysis_engine():
    dataset = pd.DataFrame({"x": [1.0, 2.0, 3.0], "y": [4.0, 5.0, 6.0]})
    engine = AnalysisEngine()
    profile = engine.profiler.profile(dataset)
    applicable_names = {plugin.name for plugin in engine.registry.applicable(profile)}

    assert "Spectral Clustering" in applicable_names


def test_selected_by_analysis_registry_for_numeric_dataset():
    dataset = pd.DataFrame({"x": [1.0, 2.0, 3.0], "y": [4.0, 5.0, 6.0]})
    engine = AnalysisEngine()
    profile = engine.profiler.profile(dataset)
    applicable_names = {plugin.name for plugin in engine.registry.applicable(profile)}

    assert "Spectral Clustering" in applicable_names
