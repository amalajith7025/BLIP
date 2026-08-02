"""Frequency distribution analysis plugin.

Calculates frequency distributions for categorical columns.

The plugin performs only scientific analysis and returns raw results.
"""
from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
import pandas as pd

from ..interfaces import AnalysisPlugin
from ..schemas import DatasetProfile


class FrequencyDistribution(AnalysisPlugin):
    """Plugin that computes frequency distributions for categorical columns.

    Validation: applicable when the dataset profile contains at least one
    column with `categorical == True`.
    """

    name = "Frequency Distribution"
    description = "Calculate category frequencies and percentages for categorical columns."

    def validate(self, profile: DatasetProfile) -> bool:
        """Return True when at least one categorical column exists.

        Args:
            profile: DatasetProfile produced by the profiler.

        Returns:
            bool: True when at least one categorical column exists.
        """
        return any(cp.categorical for cp in profile.column_profiles)

    def execute(self, dataset: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Compute frequency statistics for every categorical column.

        Returns a mapping of column name to its raw statistics. The plugin
        returns only raw statistical results; response envelopes are built
        by the AnalysisEngine.

        Args:
            dataset: pandas DataFrame to analyse.

        Returns:
            Dict[str, Dict[str, Any]]: raw results per column.
        """
        results: Dict[str, Dict[str, Any]] = {}

        # Select object and categorical dtypes
        cat_columns = dataset.select_dtypes(include=["category", "object"]).columns.tolist()

        for col in cat_columns:
            series = dataset[col]
            total_records = int(len(series))
            non_null = series.dropna()
            non_missing = int(non_null.shape[0])

            missing_values = total_records - non_missing

            if non_missing == 0:
                results[col] = {
                    "total_records": total_records,
                    "non_missing": non_missing,
                    "missing_values": missing_values,
                    "unique_values": 0,
                    "distribution": [],
                }
                continue

            # value_counts for frequencies (counts of each category)
            counts = non_null.value_counts(dropna=True)
            distribution: List[Dict[str, Any]] = []

            for value, cnt in counts.items():
                key = value if not (isinstance(value, np.generic)) else value.item()
                pct = float(cnt / non_missing * 100.0)
                distribution.append({
                    "value": key,
                    "count": int(cnt),
                    "percentage": pct,
                })

            results[col] = {
                "total_records": total_records,
                "non_missing": non_missing,
                "missing_values": missing_values,
                "unique_values": int(non_null.nunique()),
                "distribution": distribution,
            }

        return results

    def explain(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
        """Return universal explanations for frequency metrics.

        Explanations are returned once and not duplicated per column.
        """
        return {
            "frequency": "The count of occurrences for each category.",
            "percentage": "The relative frequency of each category expressed as a percentage of non-missing observations.",
            "unique_values": "The number of distinct non-missing categories observed.",
        }

    def observations(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
        """Generate objective observations grouped per column.

        Observations are concise and avoid business interpretation.
        """
        grouped: Dict[str, List[str]] = {}

        for col, metrics in results.items():
            col_obs: List[str] = []
            non_missing = metrics.get("non_missing", 0)
            unique = metrics.get("unique_values", 0)
            distribution = metrics.get("distribution", [])

            if non_missing == 0:
                col_obs.append("No non-missing values available for analysis.")
                grouped[col] = col_obs
                continue

            if unique <= 1:
                col_obs.append("Single category present.")
                grouped[col] = col_obs
                continue

            # Distribution is already sorted by descending frequency because it is generated
            # from pandas value_counts().
            top_prop = (
                distribution[0]["percentage"] / 100.0
                if distribution
                else 0.0
            )

            if top_prop > 0.5:
                col_obs.append("One category dominates the distribution.")
            elif top_prop < 0.25 and unique >= 3:
                col_obs.append("Distribution appears relatively balanced.")

            # Diversity observations (ratio-based)
            diversity_ratio = unique / non_missing if non_missing > 0 else 0.0
            if diversity_ratio > 0.5:
                col_obs.append("High category diversity.")
            elif diversity_ratio < 0.05:
                col_obs.append("Low category diversity.")

            grouped[col] = col_obs

        return grouped
