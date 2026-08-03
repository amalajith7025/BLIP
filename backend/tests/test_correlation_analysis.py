import numpy as np
import pandas as pd
import pytest

from app.analysis.profiler import DataProfiler
from app.analysis.plugins.correlation_analysis import CorrelationAnalysis


def test_validate_returns_true_for_multiple_numeric_columns():
    dataset = pd.DataFrame(
        {
            "a": [1.0, 2.0, 3.0],
            "b": [2.0, 4.0, 6.0],
        }
    )
    profile = DataProfiler().profile(dataset)

    plugin = CorrelationAnalysis()

    assert plugin.validate(profile) is True


def test_validate_returns_false_for_single_numeric_column():
    dataset = pd.DataFrame({"a": [1.0, 2.0, 3.0]})
    profile = DataProfiler().profile(dataset)

    plugin = CorrelationAnalysis()

    assert plugin.validate(profile) is False


def test_execute_computes_positive_correlation():
    dataset = pd.DataFrame(
        {
            "a": [1.0, 2.0, 3.0, 4.0],
            "b": [2.0, 4.0, 6.0, 8.0],
        }
    )
    plugin = CorrelationAnalysis()
    results = plugin.execute(dataset)

    assert "a" in results
    assert "b" in results["a"]

    metrics = results["a"]["b"]
    assert metrics["coefficient"] == pytest.approx(1.0)
    assert metrics["strength"] == "Very Strong"
    assert metrics["direction"] == "Positive"


def test_execute_computes_negative_correlation():
    dataset = pd.DataFrame(
        {
            "a": [1.0, 2.0, 3.0, 4.0],
            "b": [-1.0, -2.0, -3.0, -4.0],
        }
    )
    plugin = CorrelationAnalysis()
    results = plugin.execute(dataset)

    assert "a" in results
    assert "b" in results["a"]

    metrics = results["a"]["b"]
    assert metrics["coefficient"] == pytest.approx(-1.0)
    assert metrics["strength"] == "Very Strong"
    assert metrics["direction"] == "Negative"


def test_execute_handles_missing_values():
    dataset = pd.DataFrame(
        {
            "a": [1.0, 2.0, np.nan, 4.0],
            "b": [2.0, 4.0, 6.0, np.nan],
        }
    )
    plugin = CorrelationAnalysis()
    results = plugin.execute(dataset)

    assert "a" in results
    assert "b" in results["a"]

    metrics = results["a"]["b"]
    assert metrics["coefficient"] == pytest.approx(1.0)
    assert metrics["strength"] == "Very Strong"
    assert metrics["direction"] == "Positive"


def test_execute_handles_constant_column():
    dataset = pd.DataFrame(
        {
            "a": [1.0, 1.0, 1.0, 1.0],
            "b": [1.0, 2.0, 3.0, 4.0],
        }
    )
    plugin = CorrelationAnalysis()
    results = plugin.execute(dataset)

    assert "a" in results
    assert "b" in results["a"]

    metrics = results["a"]["b"]
    assert metrics["coefficient"] is None
    assert metrics["strength"] == "Undefined"
    assert metrics["direction"] == "Undefined"


def test_explain_returns_required_keys():
    plugin = CorrelationAnalysis()
    explanation = plugin.explain({})

    expected = {"correlation", "coefficient", "strength", "direction"}
    assert set(explanation.keys()) == expected


def test_observations_returns_expected_structure():
    dataset = pd.DataFrame(
        {
            "a": [1.0, 2.0, 3.0, 4.0],
            "b": [2.0, 4.0, 6.0, 8.0],
        }
    )
    plugin = CorrelationAnalysis()
    results = plugin.execute(dataset)
    observations = plugin.observations(results)

    assert isinstance(observations, dict)
    assert all(isinstance(value, list) for value in observations.values())
    assert any(
        item in {
            "Very Strong positive relationship detected.",
            "Very Strong negative relationship detected.",
            "Moderate linear relationship detected.",
            "Weak linear relationship detected.",
            "No linear relationship detected.",
            "Correlation could not be calculated.",
        }
        for values in observations.values()
        for item in values
    )


def test_execute_returns_unique_column_pairs():
    dataset = pd.DataFrame(
        {
            "a": [1.0, 2.0, 3.0],
            "b": [2.0, 4.0, 6.0],
            "c": [3.0, 6.0, 9.0],
        }
    )
    plugin = CorrelationAnalysis()
    results = plugin.execute(dataset)

    assert "b" in results["a"]
    assert "c" in results["a"]
    assert "c" in results["b"]

    assert "a" not in results["b"]
    assert "a" not in results.get("c", {})
    assert "b" not in results.get("c", {})
