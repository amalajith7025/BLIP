"""Chi-Square Test of Independence analysis plugin.

Performs chi-square tests for pairs of categorical columns.
"""
from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency

from ..interfaces import AnalysisPlugin
from ..schemas import DatasetProfile


class ChiSquareAnalysis(AnalysisPlugin):
    """Plugin that performs Chi-Square tests of independence."""

    name = "Chi-Square Analysis"
    description = (
        "Performs Chi-Square tests of independence for pairs of categorical columns."
    )

    def validate(self, profile: DatasetProfile) -> bool:
        """Return True when at least two categorical columns exist."""
        categorical_columns = sum(1 for cp in profile.column_profiles if cp.can_group)
        return categorical_columns >= 2

    def execute(self, dataset: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Execute Chi-Square tests for every unique categorical column pair."""
        results: Dict[str, Dict[str, Any]] = {}

        if dataset is None or dataset.empty:
            return results

        categorical_columns = dataset.select_dtypes(exclude=[np.number]).columns.tolist()

        if len(categorical_columns) < 2:
            return results

        for index_a, column_a in enumerate(categorical_columns):
            comparison_results: Dict[str, Any] = {}

            for column_b in categorical_columns[index_a + 1 :]:
                contingency_frame = dataset[[column_a, column_b]].dropna()

                if contingency_frame.empty:
                    continue

                observed = pd.crosstab(
                    contingency_frame[column_a], contingency_frame[column_b]
                )

                if observed.shape[0] < 2 or observed.shape[1] < 2:
                    continue

                try:
                    chi2, p_value, dof, expected = chi2_contingency(observed)

                    comparison_results[column_b] = {
                        "chi_square_statistic": float(chi2),
                        "p_value": float(p_value),
                        "degrees_of_freedom": int(dof),
                        "observed_frequencies": observed.values.tolist(),
                        "expected_frequencies": expected.tolist(),
                    }
                except Exception:
                    continue

            if comparison_results:
                results[column_a] = comparison_results

        return results

    def explain(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
        """Return standardized explanations for chi-square output keys."""
        return {
            "chi_square_statistic": "The chi-square statistic comparing observed and expected counts.",
            "p_value": "The probability of observing the contingency table under the null hypothesis.",
            "degrees_of_freedom": "The number of degrees of freedom for the chi-square test.",
            "observed_frequencies": "The contingency table of observed category counts.",
            "expected_frequencies": "The contingency table of expected counts under independence.",
        }

    def observations(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
        """Generate objective observations from chi-square test results."""
        observations: Dict[str, List[str]] = {}

        for column_a, comparisons in results.items():
            column_observations: List[str] = []
            valid_test_found = False
            difference_detected = False
            no_difference_detected = False

            if not comparisons:
                observations[column_a] = ["No valid categorical comparison available."]
                continue

            for metrics in comparisons.values():
                p_value = metrics.get("p_value")

                if p_value is None:
                    continue

                valid_test_found = True
                if p_value < 0.05:
                    difference_detected = True
                else:
                    no_difference_detected = True

            if not valid_test_found:
                column_observations.append("Insufficient observations for testing.")
            else:
                column_observations.append("Test completed successfully.")
                if difference_detected:
                    column_observations.append(
                        "Association detected at the selected significance level."
                    )
                if no_difference_detected:
                    column_observations.append(
                        "No statistically significant association detected."
                    )

            observations[column_a] = column_observations

        if not observations:
            observations[""] = ["No valid categorical comparison available."]

        return observations
