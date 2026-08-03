"""One-Way ANOVA analysis plugin.

Performs one-way analysis of variance for numeric columns across categorical groups.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from scipy.stats import f_oneway

from ..interfaces import AnalysisPlugin
from ..schemas import DatasetProfile


class AnovaAnalysis(AnalysisPlugin):
    """Plugin that performs one-way ANOVA across categorical groups."""

    name = "ANOVA Analysis"
    description = (
        "Performs one-way ANOVA for numeric columns across categorical groups."
    )

    def validate(self, profile: DatasetProfile) -> bool:
        """Return True when at least one numeric and one categorical column exist, with a categorical column having three or more unique groups."""
        has_numeric = any(cp.can_average for cp in profile.column_profiles)
        has_valid_categorical = any(
            cp.can_group and cp.unique_values >= 3
            for cp in profile.column_profiles
        )
        return has_numeric and has_valid_categorical

    def execute(self, dataset: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Execute one-way ANOVA for every valid categorical-numeric combination."""
        results: Dict[str, Dict[str, Any]] = {}

        if dataset is None or dataset.empty:
            return results

        categorical_columns = dataset.select_dtypes(exclude=[np.number]).columns.tolist()
        numeric_columns = dataset.select_dtypes(include=[np.number]).columns.tolist()

        if not categorical_columns or not numeric_columns:
            return results

        for categorical in categorical_columns:
            comparison_results: Dict[str, Any] = {}
            category_series = dataset[categorical]
            non_missing_category = category_series.dropna()
            unique_groups = non_missing_category.unique().tolist()

            if len(unique_groups) < 3:
                continue

            for numeric_column in numeric_columns:
                numeric_frame = dataset[[categorical, numeric_column]].dropna()

                if numeric_frame.empty:
                    continue

                groups = []
                group_sizes: Dict[str, int] = {}
                skip_comparison = False

                for group_label in unique_groups:
                    group_values = numeric_frame.loc[
                        numeric_frame[categorical] == group_label, numeric_column
                    ].astype(float)
                    size = int(group_values.shape[0])

                    if size > 0:
                        groups.append(group_values.to_numpy())
                        group_sizes[str(group_label)] = size

                if len(groups) < 3:
                    continue

                if any(size < 2 for size in group_sizes.values()):
                    continue

                try:
                    f_statistic, p_value = f_oneway(*groups)

                    comparison_results[numeric_column] = {
                        "f_statistic": float(f_statistic) if np.isfinite(f_statistic) else None,
                        "p_value": float(p_value) if np.isfinite(p_value) else None,
                        "group_count": len(group_sizes),
                        "group_sizes": group_sizes,
                    }
                except Exception:
                    continue

            if comparison_results:
                results[categorical] = comparison_results

        return results

    def explain(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
        """Return standardized explanations for ANOVA output keys."""
        return {
            "f_statistic": "The F statistic comparing variance between groups to variance within groups.",
            "p_value": "The probability of observing the group differences under the null hypothesis.",
            "group_count": "The number of groups included in the ANOVA comparison.",
            "group_sizes": "The number of non-missing observations in each group.",
        }

    def observations(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
        """Generate objective observations from ANOVA results."""
        observations: Dict[str, List[str]] = {}

        for categorical, comparisons in results.items():
            categorical_observations: List[str] = []
            valid_test_found = False
            significant_found = False
            non_significant_found = False

            if not comparisons:
                observations[categorical] = ["No valid comparison available."]
                continue

            for metrics in comparisons.values():
                p_value = metrics.get("p_value")

                if p_value is None:
                    continue

                valid_test_found = True
                if p_value < 0.05:
                    significant_found = True
                else:
                    non_significant_found = True

            if not valid_test_found:
                categorical_observations.append("Insufficient observations for testing.")
            else:
                categorical_observations.append("Analysis completed successfully.")
                if significant_found:
                    categorical_observations.append(
                        "Statistically significant difference detected."
                    )
                if non_significant_found:
                    categorical_observations.append(
                        "No statistically significant difference detected."
                    )

            observations[categorical] = categorical_observations

        if not observations:
            observations[""] = ["No valid comparison available."]

        return observations
