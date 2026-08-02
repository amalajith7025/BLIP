"""Pareto analysis plugin.

Calculates Pareto distributions for categorical columns.
"""
from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
import pandas as pd

from ..interfaces import AnalysisPlugin
from ..schemas import DatasetProfile

PARETO_CONCENTRATION_THRESHOLD = 0.2


class ParetoAnalysis(AnalysisPlugin):
    """Plugin that computes Pareto analysis for categorical columns.

    Validation: applicable when the dataset profile contains at least one
    column with `categorical == True`.
    """

    name = "Pareto Analysis"
    description = "Calculate Pareto distributions for categorical columns."

    def validate(self, profile: DatasetProfile) -> bool:
        """Return True when at least one categorical column exists.

        Args:
            profile: DatasetProfile produced by the profiler.

        Returns:
            bool: True when at least one categorical column exists.
        """
        return any(cp.categorical for cp in profile.column_profiles)

    def execute(self, dataset: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Compute Pareto statistics for every categorical column.

        Returns raw statistical results only. The AnalysisEngine builds the
        response envelope.

        Args:
            dataset: pandas DataFrame to analyse.

        Returns:
            Dict[str, Dict[str, Any]]: raw results per categorical column.
        """
        results: Dict[str, Dict[str, Any]] = {}

        categorical_columns = dataset.select_dtypes(include=["category", "object"]).columns.tolist()

        for col in categorical_columns:
            series = dataset[col]
            total_records = int(len(series))
            non_null = series.dropna()
            non_missing = int(non_null.shape[0])
            missing_values = total_records - non_missing
            unique_values = int(non_null.nunique())
            threshold_percentage = 80

            if non_missing == 0:
                results[col] = {
                    "total_records": total_records,
                    "non_missing": non_missing,
                    "missing_values": missing_values,
                    "unique_values": unique_values,
                    "threshold_percentage": threshold_percentage,
                    "categories_to_threshold": 0,
                    "distribution": [],
                }
                continue

            counts = non_null.value_counts(dropna=True)
            distribution: List[Dict[str, Any]] = []
            cumulative_count = 0
            categories_to_threshold = 0

            for value, count in counts.items():
                scalar_value = self._to_scalar(value)
                percentage = float(count / non_missing * 100.0)
                cumulative_count += int(count)
                cumulative_percentage = float(cumulative_count / non_missing * 100.0)

                distribution.append({
                    "value": scalar_value,
                    "count": int(count),
                    "percentage": percentage,
                    "cumulative_count": cumulative_count,
                    "cumulative_percentage": cumulative_percentage,
                })

                if categories_to_threshold == 0 and cumulative_percentage >= threshold_percentage:
                    categories_to_threshold = len(distribution)

            results[col] = {
                "total_records": total_records,
                "non_missing": non_missing,
                "missing_values": missing_values,
                "unique_values": unique_values,
                "threshold_percentage": threshold_percentage,
                "categories_to_threshold": categories_to_threshold,
                "distribution": distribution,
            }

        return results

    def explain(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
        """Return universal explanations for Pareto analysis metrics.

        Explanations are returned once and not duplicated per column.
        """
        return {
            "pareto_analysis": "A technique for examining category counts ordered by frequency, showing cumulative counts and cumulative percentages.",
            "rank": "The position of a category when categories are ordered by descending frequency.",
            "cumulative_count": "The running total of category counts when categories are ordered by frequency.",
            "cumulative_percentage": "The running total of category percentages when categories are ordered by frequency.",
            "threshold_percentage": "The target cumulative percentage used to identify the point where the most frequent categories account for most observations.",
        }

    def observations(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
        """Generate objective observations grouped per column.

        Observations are concise and avoid business interpretation.
        """
        grouped: Dict[str, List[str]] = {}

        for col, metrics in results.items():
            col_obs: List[str] = []
            non_missing = metrics.get("non_missing", 0)
            distribution = metrics.get("distribution", [])
            categories_to_threshold = metrics.get("categories_to_threshold", 0)

            if non_missing == 0:
                col_obs.append("No non-missing values available for analysis.")
                grouped[col] = col_obs
                continue

            if distribution:
                threshold_ratio = categories_to_threshold / len(distribution) if distribution else 0.0

                if categories_to_threshold == 1:
                    col_obs.append("A single category accounts for most observations.")
                elif threshold_ratio <= PARETO_CONCENTRATION_THRESHOLD:
                    col_obs.append("The cumulative distribution reaches the threshold after relatively few categories.")
                else:
                    col_obs.append("The cumulative distribution increases gradually.")

                diversity_ratio = len(distribution) / non_missing if non_missing > 0 else 0.0
                if diversity_ratio > 0.5:
                    col_obs.append("Categories are broadly distributed.")
            else:
                col_obs.append("No categorical distribution data available.")

            grouped[col] = col_obs

        return grouped

    @staticmethod
    def _to_scalar(value: Any) -> Any:
        """Convert numpy scalar to native Python scalar when possible."""
        if isinstance(value, np.generic):
            return value.item()
        return value
