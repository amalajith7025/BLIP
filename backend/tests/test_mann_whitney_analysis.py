import numpy as np
import pandas as pd

from app.analysis.profiler import DataProfiler
from app.analysis.plugins.mann_whitney_analysis import MannWhitneyAnalysis


def test_validate_returns_true_for_mixed_datasets():
    dataset = pd.DataFrame(
        {
            "group": ["a", "a", "b", "b"],
            "value": [1.0, 2.0, 3.0, 4.0],
        }
    )
    profile = DataProfiler().profile(dataset)

    plugin = MannWhitneyAnalysis()

    assert plugin.validate(profile) is True


def test_validate_returns_false_without_categorical_columns():
    dataset = pd.DataFrame(
        {
            "value": [1.0, 2.0, 3.0],
            "score": [4.0, 5.0, 6.0],
        }
    )
    profile = DataProfiler().profile(dataset)

    plugin = MannWhitneyAnalysis()

    assert plugin.validate(profile) is False


def test_validate_returns_false_without_numeric_columns():
    dataset = pd.DataFrame(
        {
            "group": ["a", "b", "a"],
            "label": ["x", "y", "z"],
        }
    )
    profile = DataProfiler().profile(dataset)

    plugin = MannWhitneyAnalysis()

    assert plugin.validate(profile) is False


def test_execute_returns_expected_structure():
    dataset = pd.DataFrame(
        {
            "group": ["a", "a", "b", "b"],
            "value": [10.0, 11.0, 12.0, 13.0],
        }
    )
    plugin = MannWhitneyAnalysis()
    results = plugin.execute(dataset)

    assert "group" in results
    assert "value" in results["group"]

    metric_keys = set(results["group"]["value"].keys())
    expected_keys = {
        "u_statistic",
        "p_value",
        "group_1_size",
        "group_2_size",
        "alpha",
        "significant_difference",
    }

    assert expected_keys.issubset(metric_keys)


def test_execute_detects_significant_difference():
    dataset = pd.DataFrame(
        {
            "group": ["a"] * 5 + ["b"] * 5,
            "value": [10.0, 11.0, 12.0, 13.0, 14.0, 50.0, 51.0, 52.0, 53.0, 54.0],
        }
    )
    plugin = MannWhitneyAnalysis()
    results = plugin.execute(dataset)

    metrics = results["group"]["value"]

    assert metrics["p_value"] is not None
    assert metrics["p_value"] < 0.05
    assert metrics["significant_difference"] is True


def test_execute_detects_non_significant_difference():
    dataset = pd.DataFrame(
        {
            "group": ["a"] * 4 + ["b"] * 4,
            "value": [10.0, 11.0, 12.0, 13.0, 10.0, 11.0, 12.0, 13.0],
        }
    )
    plugin = MannWhitneyAnalysis()
    results = plugin.execute(dataset)

    metrics = results["group"]["value"]

    assert metrics["significant_difference"] is False
    assert metrics["p_value"] is not None
    assert 0.0 <= metrics["p_value"] <= 1.0


def test_execute_handles_missing_values():
    dataset = pd.DataFrame(
        {
            "group": ["a", "a", "b", "b", "b"],
            "value": [10.0, np.nan, 12.0, 52.0, np.nan],
        }
    )
    plugin = MannWhitneyAnalysis()
    results = plugin.execute(dataset)

    assert "group" in results
    metrics = results["group"]["value"]

    assert metrics["group_1_size"] == 1
    assert metrics["group_2_size"] == 2
    assert metrics["p_value"] is None or 0.0 <= metrics["p_value"] <= 1.0


def test_execute_skips_when_not_exactly_two_groups_exist():
    dataset = pd.DataFrame(
        {
            "group": ["a", "b", "c", "a"],
            "value": [1.0, 2.0, 3.0, 4.0],
        }
    )
    plugin = MannWhitneyAnalysis()

    results = plugin.execute(dataset)

    assert results == {}


def test_execute_handles_empty_dataset():
    dataset = pd.DataFrame(
        {
            "group": [],
            "value": [],
        }
    )
    plugin = MannWhitneyAnalysis()

    results = plugin.execute(dataset)

    assert results == {}


def test_explain_returns_required_keys():
    plugin = MannWhitneyAnalysis()
    explanation = plugin.explain({})

    expected = {
        "u_statistic",
        "p_value",
        "alpha",
        "group_1_size",
        "group_2_size",
        "significant_difference",
    }

    assert set(explanation.keys()) == expected


def test_observations_returns_expected_structure():
    dataset = pd.DataFrame(
        {
            "group": ["a", "a", "b", "b"],
            "value": [10.0, 11.0, 12.0, 13.0],
        }
    )
    plugin = MannWhitneyAnalysis()
    results = plugin.execute(dataset)
    observations = plugin.observations(results)

    assert isinstance(observations, dict)
    assert "group" in observations
    assert isinstance(observations["group"], list)
    assert len(observations["group"]) >= 1


def test_observations_handles_empty_results():
    plugin = MannWhitneyAnalysis()
    observations = plugin.observations({})

    assert observations == {}


def test_execute_returns_python_native_types():
    dataset = pd.DataFrame(
        {
            "group": ["a", "a", "b", "b"],
            "value": [10.0, 11.0, 12.0, 13.0],
        }
    )
    plugin = MannWhitneyAnalysis()
    results = plugin.execute(dataset)

    metrics = results["group"]["value"]

    assert isinstance(metrics["u_statistic"], float)
    assert isinstance(metrics["p_value"], float)
    assert isinstance(metrics["group_1_size"], int)
    assert isinstance(metrics["group_2_size"], int)
    assert isinstance(metrics["alpha"], float)
    assert isinstance(metrics["significant_difference"], bool)


def test_execute_supports_multiple_numeric_columns():
    dataset = pd.DataFrame(
        {
            "group": ["a", "a", "b", "b"],
            "value_1": [10.0, 11.0, 12.0, 13.0],
            "value_2": [20.0, 21.0, 22.0, 23.0],
        }
    )
    plugin = MannWhitneyAnalysis()
    results = plugin.execute(dataset)

    assert "group" in results
    assert "value_1" in results["group"]
    assert "value_2" in results["group"]
