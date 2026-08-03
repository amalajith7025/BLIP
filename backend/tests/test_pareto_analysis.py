import pandas as pd

from app.analysis.profiler import DataProfiler
from app.analysis.plugins.pareto_analysis import ParetoAnalysis


def test_validate_returns_true_for_categorical_datasets():
    dataset = pd.DataFrame({"category": ["x", "y", "x"]})
    profile = DataProfiler().profile(dataset)

    plugin = ParetoAnalysis()

    assert plugin.validate(profile) is True


def test_execute_computes_cumulative_counts_and_percentages():
    dataset = pd.DataFrame({"category": ["x", "x", "x", "y", "y", "z"]})
    plugin = ParetoAnalysis()
    results = plugin.execute(dataset)
    metrics = results["category"]

    assert metrics["total_records"] == 6
    assert metrics["non_missing"] == 6
    assert metrics["missing_values"] == 0
    assert metrics["unique_values"] == 3
    assert metrics["threshold_percentage"] == 80
    assert metrics["categories_to_threshold"] == 2

    distribution = metrics["distribution"]
    assert distribution[0]["value"] == "x"
    assert distribution[0]["count"] == 3
    assert distribution[0]["percentage"] == 50.0
    assert distribution[0]["cumulative_count"] == 3
    assert distribution[0]["cumulative_percentage"] == 50.0
    assert distribution[1]["cumulative_count"] == 5
    assert distribution[1]["cumulative_percentage"] == 83.33333333333334
    assert distribution[2]["cumulative_count"] == 6
    assert distribution[2]["cumulative_percentage"] == 100.0


def test_execute_handles_empty_categorical_column():
    dataset = pd.DataFrame({"category": [None, None]})
    plugin = ParetoAnalysis()
    results = plugin.execute(dataset)
    metrics = results["category"]

    assert metrics["non_missing"] == 0
    assert metrics["missing_values"] == 2
    assert metrics["unique_values"] == 0
    assert metrics["categories_to_threshold"] == 0
    assert metrics["distribution"] == []


def test_explain_returns_required_keys():
    plugin = ParetoAnalysis()
    explanation = plugin.explain({})

    expected = {
        "pareto_analysis",
        "rank",
        "cumulative_count",
        "cumulative_percentage",
        "threshold_percentage",
    }
    assert expected.issubset(explanation.keys())


def test_observations_returns_expected_list_for_threshold_behavior():
    dataset = pd.DataFrame({"category": ["x", "x", "y", "z", "z"]})
    plugin = ParetoAnalysis()
    results = plugin.execute(dataset)
    observations = plugin.observations(results)

    assert isinstance(observations, dict)
    assert "category" in observations
    assert "The cumulative distribution increases gradually." in observations["category"]
    assert "Categories are broadly distributed." in observations["category"]
