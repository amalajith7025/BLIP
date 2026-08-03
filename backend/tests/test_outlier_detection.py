import numpy as np
import pandas as pd
import pytest

from app.analysis.profiler import DataProfiler
from app.analysis.plugins.outlier_detection import OutlierDetection


def test_validate_returns_true_for_numeric_dataset():
    dataset = pd.DataFrame({"value": [1.0, 2.0, 3.0]})
    profile = DataProfiler().profile(dataset)

    plugin = OutlierDetection()

    assert plugin.validate(profile) is True


def test_validate_returns_false_for_non_numeric_dataset():
    dataset = pd.DataFrame({"label": ["a", "b", "c"]})
    profile = DataProfiler().profile(dataset)

    plugin = OutlierDetection()

    assert plugin.validate(profile) is False


def test_execute_detects_iqr_outliers():
    dataset = pd.DataFrame({"value": [10, 11, 12, 13, 14, 100]})
    plugin = OutlierDetection()
    results = plugin.execute(dataset)

    assert "value" in results
    iqr_result = results["value"]["iqr"]

    assert iqr_result["outlier_count"] == 1
    assert iqr_result["outlier_indices"] == [5]
    assert iqr_result["lower_bound"] is not None
    assert iqr_result["upper_bound"] is not None


def test_execute_detects_zscore_outliers():
    dataset = pd.DataFrame({"value": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 100]})
    plugin = OutlierDetection()
    results = plugin.execute(dataset)

    assert "value" in results
    z_score_result = results["value"]["z_score"]

    assert z_score_result["threshold"] == 3
    assert z_score_result["outlier_count"] == 1
    assert z_score_result["outlier_indices"] == [10]


def test_execute_handles_missing_values():
    dataset = pd.DataFrame({"value": [1.0, np.nan, 3.0, 100.0]})
    plugin = OutlierDetection()
    results = plugin.execute(dataset)

    assert "value" in results
    iqr_result = results["value"]["iqr"]
    z_score_result = results["value"]["z_score"]

    assert iqr_result["q1"] is not None
    assert iqr_result["q3"] is not None
    assert isinstance(iqr_result["outlier_indices"], list)
    assert isinstance(z_score_result["outlier_indices"], list)


def test_execute_handles_constant_column():
    dataset = pd.DataFrame({"value": [5.0, 5.0, 5.0, 5.0]})
    plugin = OutlierDetection()
    results = plugin.execute(dataset)

    assert "value" in results
    iqr_result = results["value"]["iqr"]
    z_score_result = results["value"]["z_score"]

    assert iqr_result["outlier_count"] == 0
    assert iqr_result["outlier_indices"] == []
    assert z_score_result["outlier_count"] == 0
    assert z_score_result["outlier_indices"] == []


def test_execute_handles_empty_numeric_column():
    dataset = pd.DataFrame({"value": [np.nan, np.nan]})
    plugin = OutlierDetection()
    results = plugin.execute(dataset)

    assert "value" in results
    iqr_result = results["value"]["iqr"]
    z_score_result = results["value"]["z_score"]

    assert iqr_result["q1"] is None
    assert iqr_result["q3"] is None
    assert iqr_result["outlier_count"] == 0
    assert iqr_result["outlier_indices"] == []
    assert z_score_result["threshold"] == 3
    assert z_score_result["outlier_count"] == 0
    assert z_score_result["outlier_indices"] == []


def test_explain_returns_required_keys():
    plugin = OutlierDetection()
    explanation = plugin.explain({})

    expected = {
        "iqr",
        "q1",
        "q3",
        "lower_bound",
        "upper_bound",
        "z_score",
        "threshold",
        "outlier_count",
        "outlier_indices",
    }

    assert set(explanation.keys()) == expected


def test_observations_returns_expected_structure():
    dataset = pd.DataFrame({"value": [10.0, 11.0, 12.0, 13.0, 14.0, 100.0]})
    plugin = OutlierDetection()
    results = plugin.execute(dataset)
    observations = plugin.observations(results)

    assert isinstance(observations, dict)
    assert "value" in observations
    assert isinstance(observations["value"], list)
    assert len(observations["value"]) >= 1
    assert any(
        item in {
            "No outliers detected.",
            "Outliers detected using the IQR method.",
            "Outliers detected using the Z-score method.",
            "Multiple outlier detection methods identified extreme observations.",
            "Insufficient observations for outlier detection.",
        }
        for item in observations["value"]
    )


def test_execute_returns_expected_result_structure():
    dataset = pd.DataFrame(
        {
            "a": [1.0, 2.0, 3.0, 100.0],
            "b": [2.0, 4.0, 6.0, 8.0],
        }
    )
    plugin = OutlierDetection()
    results = plugin.execute(dataset)

    for column, metrics in results.items():
        assert set(metrics.keys()) == {"iqr", "z_score"}

        iqr_result = metrics["iqr"]
        assert set(iqr_result.keys()) == {
            "q1",
            "q3",
            "iqr",
            "lower_bound",
            "upper_bound",
            "outlier_count",
            "outlier_indices",
        }

        z_score_result = metrics["z_score"]
        assert set(z_score_result.keys()) == {
            "threshold",
            "outlier_count",
            "outlier_indices",
        }
