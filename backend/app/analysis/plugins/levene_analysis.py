"""Levene's test analysis plugin.

Performs Levene's test for equality of variances across categorical groups.
"""
from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
import pandas as pd
from scipy.stats import levene

from ..interfaces import AnalysisPlugin
from ..schemas import DatasetProfile


class LeveneAnalysis(AnalysisPlugin):
    """Plugin that performs Levene's test for equal variances."""

    name = "Levene's Test"
    description = (
        "Perform Levene's test for equality of variances across groups."
    )

    def validate(self, profile: DatasetProfile) -> bool:
        """Return True when the dataset contains at least one numeric and one categorical column."""
        has_numeric = any(cp.can_average for cp in profile.column_profiles)
        has_categorical = any(cp.can_group for cp in profile.column_profiles)
        return has_numeric and has_categorical

    def execute(self, dataset: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Execute Levene's test for every valid categorical-numeric combination."""
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

            if len(non_missing_groups) < 2:
                continue

            comparison_results: Dict[str, Any] = {}

            for numeric_column in numeric_columns:
                numeric_frame = dataset[[categorical, numeric_column]].copy()
                numeric_frame = numeric_frame[numeric_frame[numeric_column].notna()]

                groups: Dict[str, np.ndarray] = {}
                for group_label in non_missing_groups:
                    group_values = numeric_frame.loc[
                        numeric_frame[categorical] == group_label, numeric_column
                    ].astype(float)
                    if group_values.shape[0] > 0:
                        groups[str(group_label)] = group_values.to_numpy()

                if len(groups) < 2:
                    continue

                group_sizes = {label: int(values.shape[0]) for label, values in groups.items()}
                statistic: Any = None
                p_value: Any = None

                try:
                    test_result = levene(*groups.values(), center="mean", nan_policy="omit")
                    statistic = test_result.statistic
                    p_value = test_result.pvalue

                    if np.isnan(statistic) or np.isnan(p_value):
                        deviations = [
                            np.abs(values - np.mean(values))
                            for values in groups.values()
                        ]
                        if deviations and all(
                            np.allclose(dev, dev[0]) if dev.size > 0 else True
                            for dev in deviations
                        ):
                            statistic = 0.0
                            p_value = 1.0

                    if np.isfinite(statistic):
                        statistic = float(statistic)
                    else:
                        statistic = None
                    if np.isfinite(p_value):
                        p_value = float(p_value)
                    else:
                        p_value = None
                except Exception:
                    statistic = None
                    p_value = None

                comparison_results[numeric_column] = {
                    "statistic": statistic,
                    "p_value": p_value,
                    "group_count": len(groups),
                    "group_sizes": group_sizes,
                    "alpha": 0.05,
                    "equal_variance": bool(
                        p_value is not None and p_value >= 0.05
                    ),
                }

            if comparison_results:
                results[categorical] = comparison_results

        return results

    def explain(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
        """Return standardized explanations for Levene output keys."""
        return {
            "statistic": "The Levene statistic comparing variance among groups.",
            "p_value": "The probability of observing the group variance differences under the null hypothesis.",
            "alpha": "The significance level used to judge equality of variances.",
            "group_count": "The number of groups included in the variance comparison.",
            "group_sizes": "The number of non-missing observations in each group.",
            "equal_variance": "Indicates whether group variances are considered equal at the selected alpha level.",
        }

    def observations(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
        """Generate objective observations from Levene results."""
        if not results:
            return {}

        observations: Dict[str, List[str]] = {}

        for categorical, comparisons in results.items():
            categorical_observations: List[str] = []
            valid_test_found = False
            equal_variance_found = False
            unequal_variance_found = False
            insufficient_found = False

            if not comparisons:
                observations[categorical] = ["Very small sample sizes detected."]
                continue

            for metrics in comparisons.values():
                p_value = metrics.get("p_value")
                equal_variance = metrics.get("equal_variance")

                if p_value is None:
                    insufficient_found = True
                    continue

                valid_test_found = True
                if equal_variance:
                    equal_variance_found = True
                else:
                    unequal_variance_found = True

            if not valid_test_found:
                categorical_observations.append("Very small sample sizes detected.")
            else:
                categorical_observations.append("Analysis completed successfully.")
                if equal_variance_found:
                    categorical_observations.append("Equal variances detected.")
                if unequal_variance_found:
                    categorical_observations.append("Unequal variances detected.")

            observations[categorical] = categorical_observations

        return observations
