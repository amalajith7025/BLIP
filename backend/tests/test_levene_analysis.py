import numpy as np
import pandas as pd

from app.analysis.profiler import DataProfiler
from app.analysis.plugins.levene_analysis import LeveneAnalysis


def test_validate_returns_true_for_mixed_datasets():
    dataset = pd.DataFrame(
        {
            "group": ["a", "a", "b", "b"],
            "value": [1.0, 2.0, 3.0, 4.0],
        }
    )
    profile = DataProfiler().profile(dataset)

    plugin = LeveneAnalysis()

    assert plugin.validate(profile) is True


def test_validate_returns_false_without_categorical_columns():
    dataset = pd.DataFrame(
        {
            "value": [1.0, 2.0, 3.0],
            "score": [4.0, 5.0, 6.0],
        }
    )
    profile = DataProfiler().profile(dataset)

    plugin = LeveneAnalysis()

    assert plugin.validate(profile) is False


def test_validate_returns_false_without_numeric_columns():
    dataset = pd.DataFrame(
        {
            "group": ["a", "b", "a"],
            "label": ["x", "y", "z"],
        }
    )
    profile = DataProfiler().profile(dataset)

    plugin = LeveneAnalysis()

    assert plugin.validate(profile) is False


def test_execute_returns_expected_structure():
    dataset = pd.DataFrame(
        {
            "group": ["a", "a", "b", "b"],
            "value": [10.0, 11.0, 12.0, 13.0],
        }
    )
    plugin = LeveneAnalysis()
    results = plugin.execute(dataset)

    assert "group" in results
    assert "value" in results["group"]

    metric_keys = set(results["group"]["value"].keys())
    expected_keys = {
        "statistic",
        "p_value",
        "group_count",
        "group_sizes",
        "alpha",
        "equal_variance",
    }

    assert expected_keys.issubset(metric_keys)


def test_execute_detects_equal_variances():
    dataset = pd.DataFrame(
        {
            "group": ["a"] * 5 + ["b"] * 5,
            "value": [10.0, 11.0, 12.0, 11.0, 10.0, 9.0, 10.0, 11.0, 10.5, 9.5],
        }
    )
    plugin = LeveneAnalysis()
    results = plugin.execute(dataset)

    metrics = results["group"]["value"]

    assert metrics["p_value"] is not None
    assert metrics["p_value"] >= 0.05
    assert metrics["equal_variance"] is True


def test_execute_detects_unequal_variances():
    dataset = pd.DataFrame(
        {
            "group": ["a"] * 5 + ["b"] * 5,
            "value": [10.0, 10.0, 10.0, 10.0, 10.0, 1.0, 100.0, 1.0, 100.0, 1.0],
        }
    )
    plugin = LeveneAnalysis()
    results = plugin.execute(dataset)

    metrics = results["group"]["value"]

    assert metrics["equal_variance"] is False
    assert metrics["p_value"] is not None
    assert 0.0 <= metrics["p_value"] <= 1.0


def test_execute_handles_missing_values():
    dataset = pd.DataFrame(
        {
            "group": ["a", "a", "b", "b", "b"],
            "value": [10.0, np.nan, 12.0, 14.0, np.nan],
        }
    )
    plugin = LeveneAnalysis()
    results = plugin.execute(dataset)

    assert "group" in results
    metrics = results["group"]["value"]

    assert metrics["group_count"] == 2
    assert metrics["group_sizes"] == {"a": 1, "b": 2}
    assert metrics["p_value"] is None or 0.0 <= metrics["p_value"] <= 1.0


def test_execute_handles_multiple_groups():
    dataset = pd.DataFrame(
        {
            "group": ["a"] * 3 + ["b"] * 3 + ["c"] * 3,
            "value": [10.0, 11.0, 9.0, 20.0, 19.0, 21.0, 30.0, 31.0, 29.0],
        }
    )
    plugin = LeveneAnalysis()
    results = plugin.execute(dataset)

    assert "group" in results
    metrics = results["group"]["value"]

    assert metrics["group_count"] == 3
    assert set(metrics["group_sizes"].keys()) == {"a", "b", "c"}


def test_execute_handles_empty_dataset():
    dataset = pd.DataFrame(
        {
            "group": [],
            "value": [],
        }
    )
    plugin = LeveneAnalysis()

    results = plugin.execute(dataset)

    assert results == {}


def test_explain_returns_required_keys():
    plugin = LeveneAnalysis()
    explanation = plugin.explain({})

    expected = {
        "statistic",
        "p_value",
        "alpha",
        "group_count",
        "group_sizes",
        "equal_variance",
    }

    assert set(explanation.keys()) == expected


def test_observations_returns_expected_structure():
    dataset = pd.DataFrame(
        {
            "group": ["a"] * 3 + ["b"] * 3,
            "value": [10.0, 11.0, 9.0, 20.0, 21.0, 19.0],
        }
    )
    plugin = LeveneAnalysis()
    results = plugin.execute(dataset)
    observations = plugin.observations(results)

    assert isinstance(observations, dict)
    assert "group" in observations
    assert isinstance(observations["group"], list)


def test_observations_handles_empty_results():
    plugin = LeveneAnalysis()
    observations = plugin.observations({})

    assert observations == {}


def test_execute_returns_python_native_types():
    dataset = pd.DataFrame(
        {
            "group": ["a", "a", "b", "b"],
            "value": [10.0, 11.0, 10.5, 11.5],
        }
    )
    plugin = LeveneAnalysis()
    results = plugin.execute(dataset)

    metrics = results["group"]["value"]

    assert isinstance(metrics["statistic"], float)
    assert isinstance(metrics["p_value"], float)
    assert isinstance(metrics["group_count"], int)
    assert isinstance(metrics["group_sizes"], dict)
    assert isinstance(metrics["alpha"], float)
    assert isinstance(metrics["equal_variance"], bool)


def test_execute_supports_multiple_numeric_columns():
    dataset = pd.DataFrame(
        {
            "group": ["a", "a", "b", "b"],
            "value_1": [10.0, 11.0, 12.0, 13.0],
            "value_2": [20.0, 21.0, 22.0, 23.0],
        }
    )
    plugin = LeveneAnalysis()
    results = plugin.execute(dataset)

    assert "group" in results
    assert "value_1" in results["group"]
    assert "value_2" in results["group"]
