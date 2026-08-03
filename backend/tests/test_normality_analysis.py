import numpy as np
import pandas as pd
import pytest

from app.analysis.profiler import DataProfiler
from app.analysis.plugins.normality_analysis import NormalityAnalysis


def test_validate_returns_true_for_numeric_dataset():
    dataset = pd.DataFrame({"value": [1.0, 2.0, 3.0]})
    profile = DataProfiler().profile(dataset)

    plugin = NormalityAnalysis()

    assert plugin.validate(profile) is True


def test_validate_returns_false_for_categorical_dataset():
    dataset = pd.DataFrame({"category": ["a", "b", "c"]})
    profile = DataProfiler().profile(dataset)

    plugin = NormalityAnalysis()

    assert plugin.validate(profile) is False


def test_execute_returns_expected_structure():
    dataset = pd.DataFrame({"value": [10, 11, 12, 13, 14, 15]})
    plugin = NormalityAnalysis()
    results = plugin.execute(dataset)

    assert "value" in results

    metric_keys = set(results["value"].keys())
    expected_keys = {"statistic", "p_value", "sample_size"}

    assert metric_keys == expected_keys


def test_execute_computes_shapiro_statistics():
    dataset = pd.DataFrame(
        {"value": [10, 11, 12, 13, 14, 15, 16, 17]}
    )
    plugin = NormalityAnalysis()
    results = plugin.execute(dataset)

    metrics = results["value"]

    assert isinstance(metrics["statistic"], float)
    assert isinstance(metrics["p_value"], float)
    assert metrics["sample_size"] == 8
    assert 0.0 <= metrics["p_value"] <= 1.0


def test_execute_handles_missing_values():
    dataset = pd.DataFrame(
        {"value": [10.0, 11.0, np.nan, 13.0, 14.0, 15.0]}
    )
    plugin = NormalityAnalysis()
    results = plugin.execute(dataset)

    assert "value" in results
    assert results["value"]["sample_size"] == 5


def test_execute_handles_empty_numeric_column():
    dataset = pd.DataFrame({"value": [np.nan, np.nan]})
    plugin = NormalityAnalysis()
    results = plugin.execute(dataset)

    assert results == {}


def test_execute_handles_less_than_three_observations():
    dataset = pd.DataFrame({"value": [1.0, 2.0]})
    plugin = NormalityAnalysis()
    results = plugin.execute(dataset)

    assert results == {}


def test_execute_handles_constant_values():
    dataset = pd.DataFrame({"value": [5, 5, 5, 5, 5]})
    plugin = NormalityAnalysis()
    results = plugin.execute(dataset)

    assert "value" in results
    metrics = results["value"]

    assert metrics["sample_size"] == 5
    assert metrics["statistic"] is None or isinstance(metrics["statistic"], float)
    assert metrics["p_value"] is None or isinstance(metrics["p_value"], float)


def test_execute_handles_multiple_numeric_columns():
    dataset = pd.DataFrame(
        {
            "a": [10.0, 11.0, 12.0, 13.0, 14.0, 15.0],
            "b": [20.0, 21.0, 22.0, 23.0, 24.0, 25.0],
        }
    )
    plugin = NormalityAnalysis()
    results = plugin.execute(dataset)

    assert "a" in results
    assert "b" in results
    assert results["a"]["sample_size"] == 6
    assert results["b"]["sample_size"] == 6


def test_explain_returns_required_keys():
    plugin = NormalityAnalysis()
    explanation = plugin.explain({})

    expected = {"statistic", "p_value", "sample_size"}
    assert set(explanation.keys()) == expected


def test_observations_returns_expected_structure():
    dataset = pd.DataFrame({"value": [10, 11, 12, 13, 14, 15, 16]})
    plugin = NormalityAnalysis()
    results = plugin.execute(dataset)
    observations = plugin.observations(results)

    assert isinstance(observations, dict)
    assert "value" in observations
    assert isinstance(observations["value"], list)


def test_observations_handles_empty_results():
    plugin = NormalityAnalysis()
    observations = plugin.observations({})

    assert isinstance(observations, dict)
    assert "" in observations
    assert observations[""] == ["Test could not be performed."]
