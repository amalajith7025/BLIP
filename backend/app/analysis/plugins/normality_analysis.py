"""Statistical normality analysis plugin.

Performs Shapiro-Wilk normality tests for numeric columns.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from scipy.stats import shapiro

from ..interfaces import AnalysisPlugin
from ..schemas import DatasetProfile


class NormalityAnalysis(AnalysisPlugin):
    """Plugin that performs Shapiro-Wilk normality tests."""

    name = "Normality Analysis"
    description = (
        "Performs Shapiro-Wilk normality tests for numeric columns."
    )

    def validate(self, profile: DatasetProfile) -> bool:
        """Return True when at least one numeric column exists."""
        return any(cp.can_average for cp in profile.column_profiles)

    def execute(self, dataset: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Execute Shapiro-Wilk tests for every numeric column."""
        results: Dict[str, Dict[str, Any]] = {}

        if dataset is None or dataset.empty:
            return results

        numeric_columns = dataset.select_dtypes(include=[np.number]).columns.tolist()

        for column in numeric_columns:
            series = dataset[column].dropna().astype(float)
            sample_size = int(series.shape[0])

            if sample_size < 3:
                continue

            try:
                statistic, p_value = shapiro(series)
                results[column] = {
                    "statistic": float(statistic) if np.isfinite(statistic) else None,
                    "p_value": float(p_value) if np.isfinite(p_value) else None,
                    "sample_size": sample_size,
                }
            except Exception:
                continue

        return results

    def explain(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
        """Return standardized explanations for normality output keys."""
        return {
            "statistic": "The Shapiro-Wilk test statistic measuring normality.",
            "p_value": "The probability of observing the sample under the null hypothesis of normality.",
            "sample_size": "The number of observations used for the test.",
        }

    def observations(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
        """Generate objective observations from normality test results."""
        observations: Dict[str, List[str]] = {}

        for column, metrics in results.items():
            column_observations: List[str] = []
            p_value = metrics.get("p_value")

            if p_value is None:
                column_observations.append("Test could not be performed.")
            else:
                column_observations.append("Normality test completed successfully.")
                if p_value < 0.05:
                    column_observations.append(
                        "Data significantly deviates from normality."
                    )
                else:
                    column_observations.append(
                        "Data does not significantly deviate from normality."
                    )

            observations[column] = column_observations

        if not observations:
            observations[""] = ["Test could not be performed."]

        return observations
