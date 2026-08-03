import pandas as pd
import pytest

from app.analysis.profiler import DataProfiler
from app.analysis.plugins.frequency_distribution import FrequencyDistribution


def test_validate_returns_true_for_categorical_datasets():
    dataset = pd.DataFrame({"category": ["a", "b", "a"]})
    profile = DataProfiler().profile(dataset)

    plugin = FrequencyDistribution()

    assert plugin.validate(profile) is True


def test_execute_computes_frequencies_and_percentages():
    dataset = pd.DataFrame({"category": ["a", "a", "b", "c"]})
    plugin = FrequencyDistribution()
    results = plugin.execute(dataset)
    metrics = results["category"]

    assert metrics["total_records"] == 4
    assert metrics["non_missing"] == 4
    assert metrics["missing_values"] == 0
    assert metrics["unique_values"] == 3

    distribution = metrics["distribution"]
    values = {item["value"] for item in distribution}
    assert values == {"a", "b", "c"}

    frequency_by_value = {item["value"]: item for item in distribution}
    assert frequency_by_value["a"]["count"] == 2
    assert frequency_by_value["a"]["percentage"] == 50.0
    assert frequency_by_value["b"]["count"] == 1
    assert frequency_by_value["b"]["percentage"] == 25.0
    assert frequency_by_value["c"]["count"] == 1
    assert frequency_by_value["c"]["percentage"] == 25.0


def test_execute_handles_missing_values():
    dataset = pd.DataFrame({"category": ["a", None, "a", "b"]})
    plugin = FrequencyDistribution()
    results = plugin.execute(dataset)
    metrics = results["category"]

    assert metrics["total_records"] == 4
    assert metrics["non_missing"] == 3
    assert metrics["missing_values"] == 1
    assert metrics["unique_values"] == 2

    distribution = metrics["distribution"]
    assert distribution[0]["count"] == 2
    assert distribution[0]["percentage"] == pytest.approx(66.66666666666666)
    assert distribution[1]["count"] == 1
    assert distribution[1]["percentage"] == pytest.approx(33.33333333333333)


def test_explain_returns_required_keys():
    plugin = FrequencyDistribution()
    explanation = plugin.explain({})

    expected = {"frequency", "percentage", "unique_values"}
    assert expected.issubset(explanation.keys())


def test_observations_returns_mapping_for_varied_distribution():
    dataset = pd.DataFrame({"category": ["a", "a", "a", "b", "c"]})
    plugin = FrequencyDistribution()
    results = plugin.execute(dataset)
    observations = plugin.observations(results)

    assert isinstance(observations, dict)
    assert "category" in observations
    assert isinstance(observations["category"], list)
    assert "One category dominates the distribution." in observations["category"]
    assert "High category diversity." in observations["category"]


def test_observations_handles_empty_categorical_column():
    dataset = pd.DataFrame({"category": [None, None]})
    plugin = FrequencyDistribution()
    results = plugin.execute(dataset)
    observations = plugin.observations(results)

    assert observations == {"category": ["No non-missing values available for analysis."]}
