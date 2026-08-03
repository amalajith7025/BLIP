import numpy as np
import pandas as pd

from app.analysis.engine import AnalysisEngine
from app.analysis.profiler import DataProfiler
from app.analysis.plugins.birch_analysis import BirchAnalysis


def test_plugin_metadata():
    plugin = BirchAnalysis()

    assert plugin.name == "Birch Clustering"


def test_validate_returns_true_with_two_numeric_columns():
    dataset = pd.DataFrame({"x": [1.0, 2.0, 3.0], "y": [4.0, 5.0, 6.0]})
    profile = DataProfiler().profile(dataset)

    plugin = BirchAnalysis()
    assert plugin.validate(profile) is True


def test_validate_returns_false_with_one_numeric_column():
    dataset = pd.DataFrame({"x": [1.0, 2.0, 3.0], "group": ["a", "b", "a"]})
    profile = DataProfiler().profile(dataset)

    plugin = BirchAnalysis()
    assert plugin.validate(profile) is False


def test_execute_returns_expected_structure():
    dataset = pd.DataFrame({
        "x": [0.0, 0.5, 10.0, 10.5, 20.0],
        "y": [0.0, 0.5, 10.0, 10.5, 0.0],
    })
    plugin = BirchAnalysis()
    results = plugin.execute(dataset)

    assert set(results.keys()) == {"samples_used", "features", "clusters", "cluster_sizes", "branching_factor", "threshold"}


def test_execute_returns_empty_dict_when_fewer_than_five_complete_rows_remain():
    dataset = pd.DataFrame({"x": [1.0, np.nan, np.nan], "y": [2.0, np.nan, np.nan]})
    plugin = BirchAnalysis()
    results = plugin.execute(dataset)

    assert results == {}


def test_execute_ignores_rows_containing_missing_values():
    dataset = pd.DataFrame({
        "x": [0.0, 0.5, 10.0, np.nan, 20.0],
        "y": [0.0, 0.5, 10.0, 10.5, np.nan],
        "z": [1.0, 1.0, 11.0, 11.0, 1.0],
    })
    plugin = BirchAnalysis()
    results = plugin.execute(dataset)

    # fewer than five complete observations remain -> empty
    assert results == {}


def test_execute_supports_multiple_numeric_columns():
    dataset = pd.DataFrame({
        "x": [0.0, 0.5, 10.0, 10.5, 20.0, 20.5],
        "y": [0.0, 0.5, 10.0, 10.5, 0.0, 0.5],
        "z": [1.0, 1.0, 11.0, 11.0, 1.0, 1.0],
    })
    plugin = BirchAnalysis()
    results = plugin.execute(dataset)

    assert results["samples_used"] == 6
    assert set(results["cluster_sizes"].keys()) == set(range(results["clusters"]))
    assert isinstance(results["branching_factor"], int)
    assert isinstance(results["threshold"], float)


def test_execute_returns_python_native_types_only():
    dataset = pd.DataFrame({
        "x": [0.0, 0.5, 10.0, 10.5, 20.0, 20.5],
        "y": [0.0, 0.5, 10.0, 10.5, 0.0, 0.5],
    })
    plugin = BirchAnalysis()
    results = plugin.execute(dataset)

    assert isinstance(results["samples_used"], int)
    assert isinstance(results["clusters"], int)
    assert isinstance(results["cluster_sizes"], dict)
    assert isinstance(results["branching_factor"], int)
    assert isinstance(results["threshold"], float)


def test_explain_returns_required_keys():
    plugin = BirchAnalysis()
    explanation = plugin.explain({})

    assert set(explanation.keys()) == {"samples_used", "features", "clusters", "cluster_sizes", "branching_factor", "threshold"}


def test_observations_returns_expected_structure():
    dataset = pd.DataFrame({
        "x": [0.0, 0.5, 10.0, 10.5, 20.0, 20.5],
        "y": [0.0, 0.5, 10.0, 10.5, 0.0, 0.5],
        "z": [1.0, 1.0, 11.0, 11.0, 1.0, 1.0],
    })
    plugin = BirchAnalysis()
    observations = plugin.observations(plugin.execute(dataset))

    assert isinstance(observations, dict)
    assert "birch" in observations


def test_observations_handles_empty_results():
    plugin = BirchAnalysis()
    observations = plugin.observations({})

    assert observations == {"": ["Very small dataset used."]}


def test_registered_in_analysis_engine():
    dataset = pd.DataFrame({"x": [1.0, 2.0, 3.0], "y": [4.0, 5.0, 6.0]})
    engine = AnalysisEngine()
    profile = engine.profiler.profile(dataset)
    applicable_names = {plugin.name for plugin in engine.registry.applicable(profile)}

    assert "Birch Clustering" in applicable_names


def test_selected_by_analysis_registry_for_numeric_dataset():
    dataset = pd.DataFrame({"x": [1.0, 2.0, 3.0], "y": [4.0, 5.0, 6.0]})
    engine = AnalysisEngine()
    profile = engine.profiler.profile(dataset)
    applicable_names = {plugin.name for plugin in engine.registry.applicable(profile)}

    assert "Birch Clustering" in applicable_names
