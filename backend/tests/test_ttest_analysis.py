import numpy as np
import pandas as pd
import pytest

from app.analysis.profiler import DataProfiler
from app.analysis.plugins.ttest_analysis import TTestAnalysis


def test_validate_returns_true_for_valid_dataset():
    dataset = pd.DataFrame(
        {
            "group": ["a", "a", "b", "b"],
            "value": [1.0, 2.0, 3.0, 4.0],
        }
    )
    profile = DataProfiler().profile(dataset)

    plugin = TTestAnalysis()

    assert plugin.validate(profile) is True


def test_validate_returns_false_without_numeric_columns():
    dataset = pd.DataFrame(
        {
            "group": ["a", "a", "b", "b"],
            "category": ["x", "x", "y", "y"],
        }
    )
    profile = DataProfiler().profile(dataset)

    plugin = TTestAnalysis()

    assert plugin.validate(profile) is False


def test_validate_returns_false_without_binary_category():
    dataset = pd.DataFrame(
        {
            "group": ["a", "b", "c", "a"],
            "value": [1.0, 2.0, 3.0, 4.0],
        }
    )
    profile = DataProfiler().profile(dataset)

    plugin = TTestAnalysis()

    assert plugin.validate(profile) is False


def test_execute_returns_expected_structure():
    dataset = pd.DataFrame(
        {
            "group": ["a", "a", "b", "b"],
            "value": [10.0, 11.0, 12.0, 13.0],
        }
    )
    plugin = TTestAnalysis()
    results = plugin.execute(dataset)

    assert "group" in results
    assert "value" in results["group"]

    metric_keys = set(results["group"]["value"].keys())
    expected_keys = {
        "group_1",
        "group_2",
        "group_1_size",
        "group_2_size",
        "t_statistic",
        "p_value",
    }

    assert expected_keys.issubset(metric_keys)


def test_execute_runs_independent_ttest():
    dataset = pd.DataFrame(
        {
            "group": ["a"] * 5 + ["b"] * 5,
            "value": [10.0, 11.0, 12.0, 13.0, 14.0, 50.0, 51.0, 52.0, 53.0, 54.0],
        }
    )
    plugin = TTestAnalysis()
    results = plugin.execute(dataset)

    metrics = results["group"]["value"]

    assert metrics["group_1_size"] == 5
    assert metrics["group_2_size"] == 5
    assert metrics["t_statistic"] is not None
    assert metrics["p_value"] is not None
    assert 0.0 <= metrics["p_value"] <= 1.0


def test_execute_handles_missing_values():
    dataset = pd.DataFrame(
        {
            "group": ["a", "a", "b", "b", "b"],
            "value": [10.0, np.nan, 12.0, 52.0, np.nan],
        }
    )
    plugin = TTestAnalysis()
    results = plugin.execute(dataset)

    assert "group" in results
    metrics = results["group"]["value"]

    assert metrics["group_1_size"] == 1
    assert metrics["group_2_size"] == 2
    assert metrics["p_value"] is None or 0.0 <= metrics["p_value"] <= 1.0


def test_execute_handles_empty_dataset():
    dataset = pd.DataFrame(
        {
            "group": ["a", "b"],
            "value": [np.nan, np.nan],
        }
    )
    plugin = TTestAnalysis()
    results = plugin.execute(dataset)

    assert isinstance(results, dict)
    assert "group" in results
    metrics = results["group"]["value"]

    assert metrics["group_1_size"] == 0
    assert metrics["group_2_size"] == 0
    assert metrics["t_statistic"] is None
    assert metrics["p_value"] is None


def test_execute_handles_insufficient_observations():
    dataset = pd.DataFrame(
        {
            "group": ["a", "b"],
            "value": [10.0, 50.0],
        }
    )
    plugin = TTestAnalysis()
    results = plugin.execute(dataset)

    assert "group" in results
    metrics = results["group"]["value"]

    assert metrics["group_1_size"] == 1
    assert metrics["group_2_size"] == 1
    assert metrics["t_statistic"] is None
    assert metrics["p_value"] is None


def test_explain_returns_required_keys():
    plugin = TTestAnalysis()
    explanation = plugin.explain({})

    expected = {
        "t_statistic",
        "p_value",
        "group_1",
        "group_2",
        "group_1_size",
        "group_2_size",
    }

    assert set(explanation.keys()) == expected


def test_observations_returns_expected_structure():
    dataset = pd.DataFrame(
        {
            "group": ["a", "a", "b", "b"],
            "value": [10.0, 11.0, 12.0, 13.0],
        }
    )
    plugin = TTestAnalysis()
    results = plugin.execute(dataset)
    observations = plugin.observations(results)

    assert isinstance(observations, dict)
    assert "group" in observations
    assert isinstance(observations["group"], list)
    assert len(observations["group"]) >= 1
    assert any(
        item in {
            "Test completed successfully.",
            "No statistically significant difference detected.",
            "Difference detected at the selected significance level.",
            "Insufficient observations for testing.",
            "No valid two-group comparison available.",
        }
        for item in observations["group"]
    )


def test_execute_multiple_numeric_columns():
    dataset = pd.DataFrame(
        {
            "group": ["a", "a", "b", "b"],
            "value_1": [10.0, 11.0, 12.0, 13.0],
            "value_2": [20.0, 21.0, 22.0, 23.0],
            "value_3": [30.0, 31.0, 32.0, 33.0],
        }
    )
    plugin = TTestAnalysis()
    results = plugin.execute(dataset)

    assert "group" in results
    assert set(results["group"].keys()) == {"value_1", "value_2", "value_3"}


def test_execute_multiple_binary_columns():
    dataset = pd.DataFrame(
        {
            "group_a": ["a", "a", "b", "b"],
            "group_b": ["x", "x", "y", "y"],
            "value": [10.0, 11.0, 12.0, 13.0],
        }
    )
    plugin = TTestAnalysis()
    results = plugin.execute(dataset)

    assert "group_a" in results
    assert "group_b" in results
    assert "value" in results["group_a"]
    assert "value" in results["group_b"]
