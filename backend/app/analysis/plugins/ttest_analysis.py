"""Independent Samples t-Test analysis plugin.

Performs Welch's t-test for numeric columns across binary categorical groups.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from scipy.stats import ttest_ind

from ..interfaces import AnalysisPlugin
from ..schemas import DatasetProfile


class TTestAnalysis(AnalysisPlugin):
    """Plugin that performs independent samples t-tests."""

    name = "T-Test Analysis"
    description = (
        "Performs independent samples t-tests for numeric columns across "
        "binary categorical groups."
    )

    def validate(self, profile: DatasetProfile) -> bool:
        """Return True when the dataset contains numeric data and a binary categorical column."""
        has_numeric = any(cp.can_average for cp in profile.column_profiles)
        has_binary_categorical = any(
            cp.can_group and cp.unique_values == 2
            for cp in profile.column_profiles
        )

        return has_numeric and has_binary_categorical

    def execute(self, dataset: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Execute Welch's t-test for every valid categorical-numeric pair."""
        results: Dict[str, Dict[str, Any]] = {}

        if dataset is None or dataset.empty:
            return results

        numeric_columns = dataset.select_dtypes(include=[np.number]).columns.tolist()
        categorical_columns = dataset.select_dtypes(exclude=[np.number]).columns.tolist()

        if not numeric_columns or not categorical_columns:
            return results

        for categorical in categorical_columns:
            category_series = dataset[categorical]
            non_missing_groups = category_series.dropna().unique().tolist()

            if len(non_missing_groups) != 2:
                continue

            group_1_name, group_2_name = non_missing_groups
            comparison_results: Dict[str, Any] = {}

            for numeric_column in numeric_columns:
                numeric_frame = dataset[[categorical, numeric_column]].copy()
                numeric_frame = numeric_frame[numeric_frame[numeric_column].notna()]

                group_1_values = numeric_frame.loc[
                    numeric_frame[categorical] == group_1_name, numeric_column
                ].astype(float)
                group_2_values = numeric_frame.loc[
                    numeric_frame[categorical] == group_2_name, numeric_column
                ].astype(float)

                group_1_size = int(group_1_values.shape[0])
                group_2_size = int(group_2_values.shape[0])
                t_statistic: Optional[float] = None
                p_value: Optional[float] = None
                degrees_of_freedom: Optional[float] = None

                if group_1_size > 0 and group_2_size > 0:
                    try:
                        test_result = ttest_ind(
                            group_1_values,
                            group_2_values,
                            equal_var=False,
                            nan_policy="omit",
                        )

                        if np.isfinite(test_result.statistic):
                            t_statistic = float(test_result.statistic)
                        if np.isfinite(test_result.pvalue):
                            p_value = float(test_result.pvalue)

                        degrees_of_freedom = self._compute_welch_df(
                            group_1_values, group_2_values
                        )
                    except Exception:
                        t_statistic = None
                        p_value = None
                        degrees_of_freedom = None

                comparison_results[numeric_column] = {
                    "group_1": str(group_1_name),
                    "group_2": str(group_2_name),
                    "group_1_size": group_1_size,
                    "group_2_size": group_2_size,
                    "t_statistic": t_statistic,
                    "p_value": p_value,
                    "degrees_of_freedom": degrees_of_freedom,
                }

            if comparison_results:
                results[categorical] = comparison_results

        return results

    def explain(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
        """Return standardized explanations for t-test output keys."""
        return {
            "t_statistic": "The t statistic comparing the difference between group means.",
            "p_value": "The probability of observing the data under the null hypothesis.",
            "group_1": "The first binary group label used for the comparison.",
            "group_2": "The second binary group label used for the comparison.",
            "group_1_size": "The number of non-missing observations in the first group.",
            "group_2_size": "The number of non-missing observations in the second group.",
        }

    def observations(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
        """Generate objective observations from t-test results."""
        observations: Dict[str, List[str]] = {}

        for categorical, comparisons in results.items():
            group_observations: List[str] = []
            valid_test_found = False
            insufficient_found = False
            difference_detected = False
            no_difference_detected = False

            for metrics in comparisons.values():
                group_1_size = metrics.get("group_1_size", 0)
                group_2_size = metrics.get("group_2_size", 0)
                t_statistic = metrics.get("t_statistic")
                p_value = metrics.get("p_value")

                if (
                    group_1_size < 2
                    or group_2_size < 2
                    or t_statistic is None
                    or p_value is None
                ):
                    insufficient_found = True
                    continue

                valid_test_found = True
                if p_value < 0.05:
                    difference_detected = True
                else:
                    no_difference_detected = True

            if not comparisons:
                group_observations.append("No valid two-group comparison available.")
            else:
                if insufficient_found and not valid_test_found:
                    group_observations.append("Insufficient observations for testing.")
                if valid_test_found:
                    group_observations.append("Test completed successfully.")
                    if difference_detected:
                        group_observations.append(
                            "Difference detected at the selected significance level."
                        )
                    if no_difference_detected:
                        group_observations.append(
                            "No statistically significant difference detected."
                        )

                if not valid_test_found and not insufficient_found:
                    group_observations.append(
                        "No valid two-group comparison available."
                    )

            observations[categorical] = group_observations

        return observations

    @staticmethod
    def _compute_welch_df(
        group_1_values: pd.Series, group_2_values: pd.Series
    ) -> Optional[float]:
        """Compute Welch's degrees of freedom for two independent samples."""
        if group_1_values.size < 2 or group_2_values.size < 2:
            return None

        var_1 = float(np.var(group_1_values, ddof=1))
        var_2 = float(np.var(group_2_values, ddof=1))
        n1 = float(group_1_values.size)
        n2 = float(group_2_values.size)

        numerator = (var_1 / n1 + var_2 / n2) ** 2
        denominator = 0.0

        if var_1 > 0:
            denominator += (var_1 / n1) ** 2 / (n1 - 1)
        if var_2 > 0:
            denominator += (var_2 / n2) ** 2 / (n2 - 1)

        if denominator <= 0:
            return None

        return float(numerator / denominator)
