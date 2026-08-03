"""Mann-Whitney U test analysis plugin.

Performs the Mann-Whitney U test for numeric columns across two independent categorical groups.
"""
from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu

from ..interfaces import AnalysisPlugin
from ..schemas import DatasetProfile


class MannWhitneyAnalysis(AnalysisPlugin):
    """Plugin that performs Mann-Whitney U tests."""

    name = "Mann-Whitney U Analysis"
    description = (
        "Perform the Mann-Whitney U test for two independent groups."
    )

    def validate(self, profile: DatasetProfile) -> bool:
        """Return True when the dataset contains at least one numeric and categorical column."""
        has_numeric = any(cp.can_average for cp in profile.column_profiles)
        has_categorical = any(cp.can_group for cp in profile.column_profiles)
        return has_numeric and has_categorical

    def execute(self, dataset: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Execute Mann-Whitney U tests for every valid categorical-numeric pair."""
        results: Dict[str, Dict[str, Any]] = {}

        if dataset is None or dataset.empty:
            return results

        categorical_columns = dataset.select_dtypes(exclude=[np.number]).columns.tolist()
        numeric_columns = dataset.select_dtypes(include=[np.number]).columns.tolist()

        if not categorical_columns or not numeric_columns:
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

                u_statistic: Any = None
                p_value: Any = None

                if group_1_size > 0 and group_2_size > 0:
                    try:
                        test_result = mannwhitneyu(
                            group_1_values,
                            group_2_values,
                            alternative="two-sided",
                            nan_policy="omit",
                        )

                        if np.isfinite(test_result.statistic):
                            u_statistic = float(test_result.statistic)
                        if np.isfinite(test_result.pvalue):
                            p_value = float(test_result.pvalue)
                    except Exception:
                        u_statistic = None
                        p_value = None

                comparison_results[numeric_column] = {
                    "u_statistic": u_statistic,
                    "p_value": p_value,
                    "group_1_size": group_1_size,
                    "group_2_size": group_2_size,
                    "alpha": 0.05,
                    "significant_difference": bool(
                        p_value is not None and p_value < 0.05
                    ),
                }

            if comparison_results:
                results[categorical] = comparison_results

        return results

    def explain(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
        """Return standardized explanations for Mann-Whitney output keys."""
        return {
            "u_statistic": "The Mann-Whitney U statistic comparing the two group distributions.",
            "p_value": "The probability of observing the data under the null hypothesis of equal distributions.",
            "alpha": "The significance level used to determine statistical differences.",
            "group_1_size": "The number of non-missing observations in the first group.",
            "group_2_size": "The number of non-missing observations in the second group.",
            "significant_difference": "Indicates whether the two groups differ at the selected alpha level.",
        }

    def observations(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
        """Generate objective observations from Mann-Whitney results."""
        if not results:
            return {}

        observations: Dict[str, List[str]] = {}

        for categorical, comparisons in results.items():
            categorical_observations: List[str] = []
            valid_test_found = False
            significant_found = False
            no_difference_found = False
            insufficient_found = False

            if not comparisons:
                observations[categorical] = ["Very small sample sizes detected."]
                continue

            for metrics in comparisons.values():
                group_1_size = metrics.get("group_1_size", 0)
                group_2_size = metrics.get("group_2_size", 0)
                p_value = metrics.get("p_value")

                if group_1_size < 1 or group_2_size < 1 or p_value is None:
                    insufficient_found = True
                    continue

                valid_test_found = True
                if p_value < 0.05:
                    significant_found = True
                else:
                    no_difference_found = True

            if not valid_test_found:
                if insufficient_found:
                    categorical_observations.append("Very small sample sizes detected.")
                else:
                    categorical_observations.append("No valid two-group comparison available.")
            else:
                categorical_observations.append("Analysis completed successfully.")
                if significant_found:
                    categorical_observations.append(
                        "Statistically significant difference detected."
                    )
                if no_difference_found:
                    categorical_observations.append(
                        "No statistically significant difference detected."
                    )

            observations[categorical] = categorical_observations

        return observations
