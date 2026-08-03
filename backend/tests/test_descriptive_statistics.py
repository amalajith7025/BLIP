import numpy as np
import pandas as pd
import pytest

from app.analysis.profiler import DataProfiler
from app.analysis.plugins.descriptive_statistics import DescriptiveStatistics


def test_validate_returns_true_for_numeric_datasets():
    dataset = pd.DataFrame({"value": [1, 2, 3]})
    profile = DataProfiler().profile(dataset)

    plugin = DescriptiveStatistics()

    assert plugin.validate(profile) is True


def test_validate_returns_false_for_non_numeric_datasets():
    dataset = pd.DataFrame({"label": ["a", "b", "c"]})
    profile = DataProfiler().profile(dataset)

    plugin = DescriptiveStatistics()

    assert plugin.validate(profile) is False


def test_execute_computes_statistics_correctly():
    dataset = pd.DataFrame({"value": [1, 2, 3, 3]})
    plugin = DescriptiveStatistics()
    results = plugin.execute(dataset)

    assert "value" in results
    metrics = results["value"]

    assert metrics["count"] == 4
    assert metrics["missing_values"] == 0
    assert metrics["mean"] == 2.25
    assert metrics["median"] == 2.5
    assert metrics["mode"] == 3
    assert metrics["minimum"] == 1.0
    assert metrics["maximum"] == 3.0
    assert metrics["range"] == 2.0
    assert metrics["variance"] == pytest.approx(0.6875)
    assert metrics["std_dev"] == pytest.approx(np.sqrt(0.6875))
    assert metrics["quartile_1"] == pytest.approx(1.75)
    assert metrics["quartile_3"] == pytest.approx(3.0)
    assert metrics["interquartile_range"] == pytest.approx(1.25)


def test_execute_handles_missing_values():
    dataset = pd.DataFrame({"value": [1.0, np.nan, 3.0]})
    plugin = DescriptiveStatistics()
    results = plugin.execute(dataset)
    metrics = results["value"]

    assert metrics["count"] == 2
    assert metrics["missing_values"] == 1
    assert metrics["mean"] == 2.0
    assert metrics["median"] == 2.0
    assert metrics["minimum"] == 1.0
    assert metrics["maximum"] == 3.0


def test_execute_handles_empty_numeric_columns():
    dataset = pd.DataFrame({"value": [np.nan, np.nan]})
    plugin = DescriptiveStatistics()
    results = plugin.execute(dataset)
    metrics = results["value"]

    assert metrics["count"] == 0
    assert metrics["missing_values"] == 2
    assert metrics["mean"] is None
    assert metrics["median"] is None
    assert metrics["mode"] is None
    assert metrics["minimum"] is None
    assert metrics["maximum"] is None
    assert metrics["variance"] is None
    assert metrics["std_dev"] is None


def test_explain_returns_required_keys():
    plugin = DescriptiveStatistics()
    explanation = plugin.explain({})

    expected = {
        "mean",
        "median",
        "mode",
        "variance",
        "std_dev",
        "minimum",
        "maximum",
        "range",
        "quartile_1",
        "quartile_3",
        "interquartile_range",
        "count",
        "missing_values",
    }

    assert expected.issubset(explanation.keys())


def test_observations_returns_expected_structure():
    dataset = pd.DataFrame({"value": [1.0, 1.0, np.nan, 4.0]})
    plugin = DescriptiveStatistics()
    results = plugin.execute(dataset)

    observations = plugin.observations(results)

    assert isinstance(observations, dict)
    assert "value" in observations
    assert isinstance(observations["value"], list)
    assert any(
        "No missing values detected." in item
        or "Some missing values detected." in item
        or "Large number of missing values detected." in item
        for item in observations["value"]
    )
