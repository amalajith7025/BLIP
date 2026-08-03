import numpy as np
import pandas as pd

from app.analysis.profiler import DataProfiler
from app.analysis.plugins.kruskal_wallis_analysis import KruskalWallisAnalysis


def test_validate_returns_true_for_mixed_datasets():
    dataset = pd.DataFrame(
        {
            "group": ["a", "a", "b", "b", "c", "c"],
            "value": [1, 2, 3, 4, 5, 6],
        }
    )

    profile = DataProfiler().profile(dataset)

    plugin = KruskalWallisAnalysis()

    assert plugin.validate(profile) is True


def test_validate_returns_false_without_categorical_columns():
    dataset = pd.DataFrame(
        {
            "x": [1, 2, 3],
            "y": [4, 5, 6],
        }
    )

    profile = DataProfiler().profile(dataset)

    plugin = KruskalWallisAnalysis()

    assert plugin.validate(profile) is False


def test_validate_returns_false_without_numeric_columns():
    dataset = pd.DataFrame(
        {
            "group": ["a", "b", "c"],
            "label": ["x", "y", "z"],
        }
    )

    profile = DataProfiler().profile(dataset)

    plugin = KruskalWallisAnalysis()

    assert plugin.validate(profile) is False


def test_execute_returns_expected_structure():
    dataset = pd.DataFrame(
        {
            "group": ["a"] * 5 + ["b"] * 5 + ["c"] * 5,
            "value": [1, 2, 3, 4, 5, 10, 11, 12, 13, 14, 20, 21, 22, 23, 24],
        }
    )

    plugin = KruskalWallisAnalysis()
    results = plugin.execute(dataset)

    assert "group" in results
    assert "value" in results["group"]

    metrics = results["group"]["value"]

    assert "statistic" in metrics
    assert "p_value" in metrics
    assert "group_count" in metrics
    assert "group_sizes" in metrics
    assert "alpha" in metrics
    assert "significant_difference" in metrics

    assert metrics["group_count"] == 3
    assert isinstance(metrics["group_sizes"], dict)
    assert set(metrics["group_sizes"].keys()) == {"a", "b", "c"}
    assert metrics["group_sizes"] == {"a": 5, "b": 5, "c": 5}
    assert metrics["alpha"] == 0.05


def test_execute_handles_missing_values():
    dataset = pd.DataFrame(
        {
            "group": [
                "a",
                "a",
                "b",
                "b",
                "c",
                "c",
                "c",
            ],
            "value": [
                10,
                np.nan,
                20,
                21,
                30,
                np.nan,
                31,
            ],
        }
    )

    plugin = KruskalWallisAnalysis()
    results = plugin.execute(dataset)

    assert "group" in results

    metrics = results["group"]["value"]

    assert metrics["group_count"] == 3
    assert isinstance(metrics["group_sizes"], dict)
    assert metrics["group_sizes"] == {"a": 1, "b": 2, "c": 2}


def test_execute_skips_when_less_than_three_groups_exist():
    dataset = pd.DataFrame(
        {
            "group": ["a", "a", "b", "b"],
            "value": [1, 2, 3, 4],
        }
    )

    plugin = KruskalWallisAnalysis()

    results = plugin.execute(dataset)

    assert results == {}


def test_execute_handles_empty_dataset():
    dataset = pd.DataFrame(
        {
            "group": [],
            "value": [],
        }
    )

    plugin = KruskalWallisAnalysis()

    results = plugin.execute(dataset)

    assert results == {}


def test_explain_returns_required_keys():
    plugin = KruskalWallisAnalysis()

    explanation = plugin.explain({})

    assert set(explanation.keys()) == {
        "statistic",
        "p_value",
        "alpha",
        "significant_difference",
        "group_count",
        "group_sizes",
    }


def test_observations_returns_expected_structure():
    dataset = pd.DataFrame(
        {
            "group": ["a"] * 5 + ["b"] * 5 + ["c"] * 5,
            "value": [1, 2, 3, 4, 5, 10, 11, 12, 13, 14, 20, 21, 22, 23, 24],
        }
    )

    plugin = KruskalWallisAnalysis()

    results = plugin.execute(dataset)

    observations = plugin.observations(results)

    assert isinstance(observations, dict)
    assert "group" in observations
    assert isinstance(observations["group"], list)


def test_observations_handles_empty_results():
    plugin = KruskalWallisAnalysis()

    observations = plugin.observations({})

    assert observations == {}


def test_execute_returns_python_numeric_types():
    dataset = pd.DataFrame(
        {
            "group": ["a"] * 5 + ["b"] * 5 + ["c"] * 5,
            "value": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        }
    )

    plugin = KruskalWallisAnalysis()

    results = plugin.execute(dataset)

    metrics = results["group"]["value"]

    assert isinstance(metrics["statistic"], float)
    assert isinstance(metrics["p_value"], float)
    assert isinstance(metrics["group_count"], int)
    assert isinstance(metrics["group_sizes"], dict)
    assert isinstance(metrics["alpha"], float)
    assert isinstance(metrics["significant_difference"], bool)


def test_execute_supports_multiple_numeric_columns():
    dataset = pd.DataFrame(
        {
            "group": ["a"] * 5 + ["b"] * 5 + ["c"] * 5,
            "x": [1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17],
            "y": [5, 6, 7, 8, 9, 20, 21, 22, 23, 24, 40, 41, 42, 43, 44],
        }
    )

    plugin = KruskalWallisAnalysis()

    results = plugin.execute(dataset)

    assert "group" in results
    assert "x" in results["group"]
    assert "y" in results["group"]