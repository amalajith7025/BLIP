import numpy as np
import pandas as pd

from app.analysis.profiler import DataProfiler
from app.analysis.plugins.anova_analysis import AnovaAnalysis


def test_validate_returns_true_for_valid_dataset():
    dataset = pd.DataFrame(
        {
            "group": ["a", "a", "b", "b", "c", "c"],
            "value": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
        }
    )
    profile = DataProfiler().profile(dataset)

    plugin = AnovaAnalysis()

    assert plugin.validate(profile) is True


def test_validate_returns_false_for_numeric_only_dataset():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0],
            "y": [4.0, 5.0, 6.0],
        }
    )
    profile = DataProfiler().profile(dataset)

    plugin = AnovaAnalysis()

    assert plugin.validate(profile) is False


def test_validate_returns_false_for_categorical_only_dataset():
    dataset = pd.DataFrame(
        {
            "a": ["x", "y", "z"],
            "b": ["u", "v", "w"],
        }
    )
    profile = DataProfiler().profile(dataset)

    plugin = AnovaAnalysis()

    assert plugin.validate(profile) is False


def test_validate_returns_false_when_less_than_three_groups():
    dataset = pd.DataFrame(
        {
            "group": ["a", "a", "b", "b"],
            "value": [1.0, 2.0, 3.0, 4.0],
        }
    )
    profile = DataProfiler().profile(dataset)

    plugin = AnovaAnalysis()

    assert plugin.validate(profile) is False


def test_execute_returns_expected_structure():
    dataset = pd.DataFrame(
        {
            "group": ["a", "a", "b", "b", "c", "c"],
            "value": [10.0, 12.0, 20.0, 22.0, 30.0, 32.0],
        }
    )
    plugin = AnovaAnalysis()
    results = plugin.execute(dataset)

    assert "group" in results
    assert "value" in results["group"]

    metric_keys = set(results["group"]["value"].keys())
    expected_keys = {"f_statistic", "p_value", "group_count", "group_sizes"}

    assert metric_keys == expected_keys


def test_execute_computes_anova_statistics():
    dataset = pd.DataFrame(
        {
            "group": ["a"] * 4 + ["b"] * 4 + ["c"] * 4,
            "value": [10.0, 11.0, 12.0, 13.0, 20.0, 21.0, 22.0, 23.0, 30.0, 31.0, 32.0, 33.0],
        }
    )
    plugin = AnovaAnalysis()
    results = plugin.execute(dataset)

    metrics = results["group"]["value"]

    assert isinstance(metrics["f_statistic"], float)
    assert isinstance(metrics["p_value"], float)
    assert metrics["group_count"] == 3
    assert isinstance(metrics["group_sizes"], dict)
    assert set(metrics["group_sizes"].keys()) == {"a", "b", "c"}
    assert 0.0 <= metrics["p_value"] <= 1.0


def test_execute_handles_missing_values():
    dataset = pd.DataFrame(
        {
            "group": ["a", "a", "a", "b", "b", "b", "c", "c", "c"],
            "value": [10.0, 11.0, np.nan, 20.0, 21.0, np.nan, 30.0, 31.0, np.nan],
        }
    )
    plugin = AnovaAnalysis()
    results = plugin.execute(dataset)

    assert isinstance(results, dict)
    assert "group" in results
    assert "value" in results["group"]


def test_execute_handles_empty_dataset():
    dataset = pd.DataFrame(
        {
            "group": [None, None, None],
            "value": [np.nan, np.nan, np.nan],
        }
    )
    plugin = AnovaAnalysis()
    results = plugin.execute(dataset)

    assert results == {}


def test_execute_skips_groups_with_single_observation():
    dataset = pd.DataFrame(
        {
            "group": ["a", "a", "b", "b", "c"],
            "value": [10.0, 11.0, 20.0, 21.0, 30.0],
        }
    )
    plugin = AnovaAnalysis()
    results = plugin.execute(dataset)

    assert results == {}


def test_execute_returns_unique_category_numeric_pairs():
    dataset = pd.DataFrame(
        {
            "group_a": ["x", "x", "y", "y", "z", "z"],
            "group_b": ["u", "u", "v", "v", "w", "w"],
            "value_1": [10.0, 11.0, 20.0, 21.0, 30.0, 31.0],
            "value_2": [40.0, 41.0, 50.0, 51.0, 60.0, 61.0],
        }
    )
    plugin = AnovaAnalysis()
    results = plugin.execute(dataset)

    assert "group_a" in results
    assert "group_b" in results
    assert "value_1" in results["group_a"]
    assert "value_2" in results["group_a"]
    assert "value_1" in results["group_b"]
    assert "value_2" in results["group_b"]
    assert "group_a" not in results.get("group_b", {})
    assert "group_b" not in results.get("group_a", {})


def test_explain_returns_required_keys():
    plugin = AnovaAnalysis()
    explanation = plugin.explain({})

    expected = {"f_statistic", "p_value", "group_count", "group_sizes"}
    assert set(explanation.keys()) == expected


def test_observations_returns_expected_structure():
    dataset = pd.DataFrame(
        {
            "group": ["a"] * 4 + ["b"] * 4 + ["c"] * 4,
            "value": [10.0, 11.0, 12.0, 13.0, 20.0, 21.0, 22.0, 23.0, 30.0, 31.0, 32.0, 33.0],
        }
    )
    plugin = AnovaAnalysis()
    results = plugin.execute(dataset)
    observations = plugin.observations(results)

    assert isinstance(observations, dict)
    assert all(isinstance(value, list) for value in observations.values())


def test_observations_handles_empty_results():
    plugin = AnovaAnalysis()
    observations = plugin.observations({})

    assert isinstance(observations, dict)
    assert "" in observations
    assert observations[""] == ["No valid comparison available."]
