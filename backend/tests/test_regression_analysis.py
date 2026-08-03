import numpy as np
import pandas as pd
import pytest

from app.analysis.profiler import DataProfiler
from app.analysis.plugins.regression_analysis import RegressionAnalysis


def test_validate_returns_true_for_multiple_numeric_columns():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0],
            "y": [2.0, 4.0, 6.0],
        }
    )
    profile = DataProfiler().profile(dataset)

    plugin = RegressionAnalysis()

    assert plugin.validate(profile) is True


def test_validate_returns_false_for_single_numeric_column():
    dataset = pd.DataFrame({"x": [1.0, 2.0, 3.0]})
    profile = DataProfiler().profile(dataset)

    plugin = RegressionAnalysis()

    assert plugin.validate(profile) is False


def test_execute_computes_linear_regression():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0, 4.0, 5.0],
            "y": [2.0, 4.0, 6.0, 8.0, 10.0],
        }
    )
    plugin = RegressionAnalysis()
    results = plugin.execute(dataset)

    assert "x" in results
    assert "y" in results["x"]

    metrics = results["x"]["y"]
    assert metrics["slope"] == pytest.approx(2.0)
    assert metrics["intercept"] == pytest.approx(0.0)
    assert metrics["r_squared"] == pytest.approx(1.0)
    assert metrics["mse"] == pytest.approx(0.0)
    assert metrics["rss"] == pytest.approx(0.0)


def test_execute_handles_missing_values():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, np.nan, 4.0],
            "y": [2.0, 4.0, 6.0, 8.0],
        }
    )
    plugin = RegressionAnalysis()
    results = plugin.execute(dataset)

    assert "x" in results
    assert "y" in results["x"]

    metrics = results["x"]["y"]
    assert metrics["slope"] == pytest.approx(2.0)
    assert metrics["intercept"] == pytest.approx(0.0)
    assert metrics["r_squared"] == pytest.approx(1.0)
    assert metrics["mse"] == pytest.approx(0.0)
    assert metrics["rss"] == pytest.approx(0.0)


def test_execute_handles_constant_column():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 1.0, 1.0, 1.0],
            "y": [2.0, 4.0, 6.0, 8.0],
        }
    )
    plugin = RegressionAnalysis()
    results = plugin.execute(dataset)

    assert "x" in results
    assert "y" in results["x"]

    metrics = results["x"]["y"]
    assert metrics["slope"] is None
    assert metrics["intercept"] is None
    assert metrics["r_squared"] is None
    assert metrics["mse"] is None
    assert metrics["rss"] is None


def test_execute_handles_insufficient_observations():
    dataset = pd.DataFrame(
        {
            "x": [1.0, np.nan, np.nan],
            "y": [2.0, np.nan, np.nan],
        }
    )
    plugin = RegressionAnalysis()
    results = plugin.execute(dataset)

    assert "x" in results
    assert "y" in results["x"]

    metrics = results["x"]["y"]
    assert metrics["slope"] is None
    assert metrics["intercept"] is None
    assert metrics["r_squared"] is None
    assert metrics["mse"] is None
    assert metrics["rss"] is None


def test_explain_returns_required_keys():
    plugin = RegressionAnalysis()
    explanation = plugin.explain({})

    expected = {"regression", "slope", "intercept", "r_squared", "mse", "rss"}
    assert set(explanation.keys()) == expected


def test_observations_returns_expected_structure():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0, 4.0],
            "y": [2.0, 4.0, 6.0, 8.0],
        }
    )
    plugin = RegressionAnalysis()
    results = plugin.execute(dataset)
    observations = plugin.observations(results)

    assert isinstance(observations, dict)
    assert all(isinstance(value, list) for value in observations.values())
    assert any(
        item in {
            "Strong linear model fit detected.",
            "Moderate linear model fit detected.",
            "Weak linear model fit detected.",
            "Regression model could not be calculated.",
        }
        for values in observations.values()
        for item in values
    )


def test_execute_returns_unique_column_pairs():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0],
            "y": [2.0, 4.0, 6.0],
            "z": [3.0, 6.0, 9.0],
        }
    )
    plugin = RegressionAnalysis()
    results = plugin.execute(dataset)

    assert "y" in results["x"]
    assert "z" in results["x"]
    assert "z" in results["y"]

    assert "x" not in results["y"]
    assert "x" not in results.get("z", {})
    assert "y" not in results.get("z", {})


def test_execute_returns_expected_result_structure():
    dataset = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0],
            "y": [2.0, 4.0, 6.0],
        }
    )
    plugin = RegressionAnalysis()
    results = plugin.execute(dataset)

    for pairs in results.values():
        for metrics in pairs.values():
            assert set(metrics.keys()) == {"slope", "intercept", "r_squared", "mse", "rss"}
