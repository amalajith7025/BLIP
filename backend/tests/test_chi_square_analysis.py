import numpy as np
import pandas as pd
import pytest

from app.analysis.profiler import DataProfiler
from app.analysis.plugins.chi_square_analysis import ChiSquareAnalysis


def test_validate_returns_true_for_two_categorical_columns():
    dataset = pd.DataFrame(
        {
            "a": ["x", "x", "y", "y"],
            "b": ["u", "u", "v", "v"],
        }
    )
    profile = DataProfiler().profile(dataset)

    plugin = ChiSquareAnalysis()

    assert plugin.validate(profile) is True


def test_validate_returns_false_for_single_categorical_column():
    dataset = pd.DataFrame(
        {
            "a": ["x", "y", "x", "y"],
            "value": [1, 2, 3, 4],
        }
    )
    profile = DataProfiler().profile(dataset)

    plugin = ChiSquareAnalysis()

    assert plugin.validate(profile) is False


def test_validate_returns_false_for_numeric_dataset():
    dataset = pd.DataFrame(
        {
            "x": [1, 2, 3],
            "y": [4, 5, 6],
        }
    )
    profile = DataProfiler().profile(dataset)

    plugin = ChiSquareAnalysis()

    assert plugin.validate(profile) is False


def test_execute_returns_expected_structure():
    dataset = pd.DataFrame(
        {
            "a": ["x", "x", "y", "y"],
            "b": ["u", "v", "u", "v"],
        }
    )
    plugin = ChiSquareAnalysis()
    results = plugin.execute(dataset)

    assert "a" in results
    assert "b" in results["a"]

    metric_keys = set(results["a"]["b"].keys())
    expected_keys = {
        "chi_square_statistic",
        "p_value",
        "degrees_of_freedom",
        "observed_frequencies",
        "expected_frequencies",
    }

    assert metric_keys == expected_keys


def test_execute_computes_chi_square_statistics():
    dataset = pd.DataFrame(
        {
            "a": ["x", "x", "y", "y", "x", "y"],
            "b": ["u", "u", "u", "v", "v", "v"],
        }
    )
    plugin = ChiSquareAnalysis()
    results = plugin.execute(dataset)

    metrics = results["a"]["b"]

    assert isinstance(metrics["chi_square_statistic"], float)
    assert isinstance(metrics["p_value"], float)
    assert isinstance(metrics["degrees_of_freedom"], int)
    assert isinstance(metrics["observed_frequencies"], list)
    assert isinstance(metrics["expected_frequencies"], list)
    assert metrics["degrees_of_freedom"] >= 1
    assert 0.0 <= metrics["p_value"] <= 1.0


def test_execute_handles_missing_values():
    dataset = pd.DataFrame(
        {
            "a": ["x", None, "y", "y", "x"],
            "b": ["u", "u", "v", None, "v"],
        }
    )
    plugin = ChiSquareAnalysis()
    results = plugin.execute(dataset)

    assert isinstance(results, dict)
    assert "a" in results
    assert "b" in results["a"]


def test_execute_handles_single_category_columns():
    dataset = pd.DataFrame(
        {
            "a": ["x", "x", "x", "x"],
            "b": ["u", "v", "u", "v"],
        }
    )
    plugin = ChiSquareAnalysis()
    results = plugin.execute(dataset)

    assert results == {}


def test_execute_handles_empty_dataset():
    dataset = pd.DataFrame(
        {
            "a": [None, None],
            "b": [None, None],
        }
    )
    plugin = ChiSquareAnalysis()
    results = plugin.execute(dataset)

    assert results == {}


def test_execute_returns_unique_column_pairs():
    dataset = pd.DataFrame(
        {
            "a": ["x", "x", "y", "y"],
            "b": ["u", "v", "u", "v"],
            "c": ["m", "m", "n", "n"],
        }
    )
    plugin = ChiSquareAnalysis()
    results = plugin.execute(dataset)

    assert "a" in results
    assert "b" in results["a"]
    assert "c" in results["a"]
    assert "a" not in results.get("b", {})
    assert "a" not in results.get("c", {})


def test_explain_returns_required_keys():
    plugin = ChiSquareAnalysis()
    explanation = plugin.explain({})

    expected = {
        "chi_square_statistic",
        "p_value",
        "degrees_of_freedom",
        "observed_frequencies",
        "expected_frequencies",
    }

    assert set(explanation.keys()) == expected


def test_observations_returns_expected_structure():
    dataset = pd.DataFrame(
        {
            "a": ["x", "x", "y", "y"],
            "b": ["u", "v", "u", "v"],
        }
    )
    plugin = ChiSquareAnalysis()
    results = plugin.execute(dataset)
    observations = plugin.observations(results)

    assert isinstance(observations, dict)
    assert all(isinstance(value, list) for value in observations.values())


def test_observations_handles_empty_results():
    plugin = ChiSquareAnalysis()
    observations = plugin.observations({})

    assert isinstance(observations, dict)
    assert "" in observations
    assert observations[""] == ["No valid categorical comparison available."]
