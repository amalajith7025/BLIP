"""Kruskal-Wallis analysis plugin.

Compares distributions of three or more independent groups using the Kruskal-Wallis H test.
"""
from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
import pandas as pd
from scipy.stats import kruskal

from ..interfaces import AnalysisPlugin
from ..schemas import DatasetProfile


class KruskalWallisAnalysis(AnalysisPlugin):
    """Plugin that performs Kruskal-Wallis H tests."""

    name = "Kruskal-Wallis Analysis"
    description = (
        "Compares the distributions of three or more independent groups using the "
        "Kruskal-Wallis H test."
    )

    def validate(self, profile: DatasetProfile) -> bool:
        """Return True when at least one categorical and one numeric column exist."""
        has_numeric = any(cp.can_average for cp in profile.column_profiles)
        has_categorical = any(cp.can_group for cp in profile.column_profiles)
        return has_numeric and has_categorical

    def execute(self, dataset: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Execute Kruskal-Wallis tests for every categorical-numeric combination."""
        results: Dict[str, Dict[str, Any]] = {}

        if dataset is None or dataset.empty:
            return results

        categorical_columns = dataset.select_dtypes(exclude=[np.number]).columns.tolist()
        numeric_columns = dataset.select_dtypes(include=[np.number]).columns.tolist()

        if not categorical_columns or not numeric_columns:
            return results

        for categorical in categorical_columns:
            comparison_results: Dict[str, Any] = {}

            for numeric_column in numeric_columns:
                numeric_frame = dataset[[categorical, numeric_column]].dropna()

                if numeric_frame.empty:
                    continue

                groups: Dict[str, np.ndarray] = {}
                for group_label in numeric_frame[categorical].unique().tolist():
                    group_values = numeric_frame.loc[
                        numeric_frame[categorical] == group_label, numeric_column
                    ].astype(float)
                    if group_values.shape[0] > 0:
                        groups[str(group_label)] = group_values.to_numpy()

                if len(groups) < 3:
                    continue

                group_sizes = {label: int(values.shape[0]) for label, values in groups.items()}

                try:
                    statistic, p_value = kruskal(*groups.values())
                    comparison_results[numeric_column] = {
                        "statistic": float(statistic) if np.isfinite(statistic) else None,
                        "p_value": float(p_value) if np.isfinite(p_value) else None,
                        "group_count": len(groups),
                        "group_sizes": group_sizes,
                        "alpha": 0.05,
                        "significant_difference": (
                            float(p_value) < 0.05 if np.isfinite(p_value) else False
                        ),
                    }
                except Exception:
                    continue

            if comparison_results:
                results[categorical] = comparison_results

        return results

    def explain(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
        """Return standardized explanations for Kruskal-Wallis output keys."""
        return {
            "statistic": "The Kruskal-Wallis H statistic comparing group ranks.",
            "p_value": "The probability of observing the rank differences under the null hypothesis.",
            "alpha": "The significance level used to determine statistical differences.",
            "significant_difference": "Indicates whether group distributions differ at the selected alpha level.",
            "group_count": "The number of groups included in the test.",
            "group_sizes": "The number of observations in each group.",
        }

    def observations(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
        """Generate objective observations from Kruskal-Wallis results."""
        if not results:
            return {}

        observations: Dict[str, List[str]] = {}

        for categorical, comparisons in results.items():
            categorical_observations: List[str] = []
            test_completed = False
            significant_found = False
            non_significant_found = False
            uneven_sizes = False

            if not comparisons:
                observations[categorical] = ["Very small sample sizes detected."]
                continue

            for metrics in comparisons.values():
                p_value = metrics.get("p_value")
                group_sizes = metrics.get("group_sizes", {})

                if p_value is None:
                    continue

                test_completed = True
                if metrics.get("significant_difference"):
                    significant_found = True
                else:
                    non_significant_found = True

                if group_sizes and len(set(group_sizes.values())) > 1:
                    uneven_sizes = True

            if not test_completed:
                categorical_observations.append("Very small sample sizes detected.")
            else:
                categorical_observations.append("Analysis completed successfully.")
                if significant_found:
                    categorical_observations.append(
                        "Significant differences detected between groups."
                    )
                if non_significant_found:
                    categorical_observations.append(
                        "No statistically significant differences detected."
                    )
                if uneven_sizes:
                    categorical_observations.append("Uneven group sizes detected.")

            observations[categorical] = categorical_observations

        if not observations:
            observations[""] = ["Very small sample sizes detected."]

        return observations
