"""Regression analysis plugin.

Calculates pairwise simple linear regression models for numeric columns.
"""
from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
import pandas as pd

from ..interfaces import AnalysisPlugin
from ..schemas import DatasetProfile


class RegressionAnalysis(AnalysisPlugin):
    """Plugin that computes simple linear regression for numeric columns.

    Validation: applicable only when the dataset contains at least two numeric
    columns.
    """

    name = "Regression Analysis"
    description = "Calculate pairwise simple linear regression models for numeric columns."

    def validate(self, profile: DatasetProfile) -> bool:
        """Return True when at least two numeric columns exist.

        Args:
            profile: DatasetProfile produced by the profiler.

        Returns:
            bool: True when at least two numeric columns can be averaged.
        """
        return sum(cp.can_average for cp in profile.column_profiles) >= 2

    def execute(self, dataset: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Compute pairwise simple linear regression models.

        Uses pairwise complete observations and returns raw regression metrics.
        """
        results: Dict[str, Dict[str, Any]] = {}

        numeric_columns = dataset.select_dtypes(include=[np.number]).columns.tolist()

        for index_a in range(len(numeric_columns) - 1):
            column_a = numeric_columns[index_a]
            for column_b in numeric_columns[index_a + 1 :]:
                pairwise = dataset[[column_a, column_b]].dropna()
                slope: Any = None
                intercept: Any = None
                r_squared: Any = None
                mse: Any = None
                rss: Any = None

                if len(pairwise) >= 2:
                    x = pairwise[column_a].to_numpy(dtype=float)
                    y = pairwise[column_b].to_numpy(dtype=float)
                    if np.unique(x).size > 1:
                        try:
                            slope, intercept = np.polyfit(x, y, 1)
                            y_pred = slope * x + intercept
                            residuals = y - y_pred
                            rss_value = float(np.sum(residuals**2))
                            mean_y = float(np.mean(y))
                            ss_total = float(np.sum((y - mean_y) ** 2))
                            r_squared = (
                                1.0 - rss_value / ss_total
                                if ss_total > 0
                                else (1.0 if np.isclose(rss_value, 0.0) else 0.0)
                            )
                            mse = float(rss_value / len(y))
                            rss = rss_value
                        except Exception:
                            slope = None
                            intercept = None
                            r_squared = None
                            mse = None
                            rss = None

                results.setdefault(column_a, {})[column_b] = {
                    "slope": slope,
                    "intercept": intercept,
                    "r_squared": r_squared,
                    "mse": mse,
                    "rss": rss,
                }

        return results

    def explain(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
        """Return universal explanations for regression metrics."""
        return {
            "regression": "A model that describes the relationship between a predictor and a response variable.",
            "slope": "The change in the response variable for a unit change in the predictor.",
            "intercept": "The expected response value when the predictor is zero.",
            "r_squared": "The proportion of variance in the response explained by the predictor.",
            "mse": "The average squared difference between observed and predicted values.",
            "rss": "The total squared difference between observed and predicted values.",
        }

    def observations(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
        """Generate objective observations for each pairwise regression model."""
        grouped: Dict[str, List[str]] = {}

        for column_a, pairs in results.items():
            for column_b, metrics in pairs.items():
                r_squared = metrics.get("r_squared")
                key = f"{column_a} ↔ {column_b}"
                observations: List[str] = []

                if r_squared is None:
                    observations.append("Regression model could not be calculated.")
                elif r_squared >= 0.8:
                    observations.append("Strong linear model fit detected.")
                elif r_squared >= 0.4:
                    observations.append("Moderate linear model fit detected.")
                else:
                    observations.append("Weak linear model fit detected.")

                grouped[key] = observations

        return grouped
