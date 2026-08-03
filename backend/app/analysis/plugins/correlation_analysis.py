"""Correlation analysis plugin.

Calculates pairwise Pearson correlations for numeric columns.
"""
from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
import pandas as pd

from ..interfaces import AnalysisPlugin
from ..schemas import DatasetProfile


class CorrelationAnalysis(AnalysisPlugin):
    """Plugin that computes pairwise correlations for numeric columns.

    Validation: applicable only when the dataset contains at least two numeric
    columns.
    """

    name = "Correlation Analysis"
    description = "Calculate pairwise Pearson correlations for numeric columns."

    def validate(self, profile: DatasetProfile) -> bool:
        """Return True when at least two numeric columns exist.

        Args:
            profile: DatasetProfile produced by the profiler.

        Returns:
            bool: True when at least two numeric columns can be averaged.
        """
        return sum(cp.can_average for cp in profile.column_profiles) >= 2

    def execute(self, dataset: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Compute pairwise Pearson correlations for numeric column pairs.

        Uses pairwise complete observations and handles constant columns
        without raising exceptions.
        """
        results: Dict[str, Dict[str, Any]] = {}

        numeric_columns = dataset.select_dtypes(include=[np.number]).columns.tolist()

        for index_a in range(len(numeric_columns) - 1):
            column_a = numeric_columns[index_a]
            for column_b in numeric_columns[index_a + 1 :]:
                pairwise = dataset[[column_a, column_b]].dropna()
                coefficient: Any = None
                strength = "Undefined"
                direction = "Undefined"

                if len(pairwise) >= 2:
                    unique_a = int(pairwise[column_a].nunique(dropna=True))
                    unique_b = int(pairwise[column_b].nunique(dropna=True))

                    if unique_a > 1 and unique_b > 1:
                        correlation = pairwise[column_a].corr(pairwise[column_b], method="pearson")
                        if not pd.isna(correlation):
                            coefficient = float(correlation)

                if coefficient is not None:
                    abs_coefficient = abs(coefficient)

                    if abs_coefficient <= 0.19:
                        strength = "Very Weak"
                    elif abs_coefficient <= 0.39:
                        strength = "Weak"
                    elif abs_coefficient <= 0.59:
                        strength = "Moderate"
                    elif abs_coefficient <= 0.79:
                        strength = "Strong"
                    else:
                        strength = "Very Strong"

                    if coefficient > 0:
                        direction = "Positive"
                    elif coefficient < 0:
                        direction = "Negative"
                    else:
                        direction = "No Linear Relationship"

                results.setdefault(column_a, {})[column_b] = {
                    "coefficient": coefficient,
                    "strength": strength,
                    "direction": direction,
                }

        return results

    def explain(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
        """Return universal explanations for correlation metrics."""
        return {
            "correlation": "A measure of how two numeric variables vary together.",
            "coefficient": "Pearson correlation coefficient showing the linear relationship strength and direction.",
            "strength": "Describes the magnitude of the linear relationship.",
            "direction": "Describes whether the linear relationship is positive, negative, or absent.",
        }

    def observations(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
        """Generate objective observations for each pairwise correlation."""
        grouped: Dict[str, List[str]] = {}

        for column_a, pairs in results.items():
            for column_b, metrics in pairs.items():
                coefficient = metrics.get("coefficient")
                strength = metrics.get("strength")
                direction = metrics.get("direction")
                key = f"{column_a} ↔ {column_b}"
                observations: List[str] = []

                if coefficient is None or direction == "Undefined":
                    observations.append("Correlation could not be calculated.")
                elif strength in {"Strong", "Very Strong"}:
                    observations.append(f"{strength} {direction.lower()} relationship detected.")
                elif strength == "Moderate":
                    observations.append("Moderate linear relationship detected.")
                elif strength == "Weak":
                    observations.append("Weak linear relationship detected.")
                else:
                    observations.append("No linear relationship detected.")

                grouped[key] = observations

        return grouped
