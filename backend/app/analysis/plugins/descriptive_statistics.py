"""Descriptive Statistics analysis plugin.

Calculates descriptive statistics for numeric columns and
provides universal explanations and objective observations.
"""
from __future__ import annotations

from typing import Any, Dict, List, Union

import numpy as np
import pandas as pd

from ..interfaces import AnalysisPlugin
from ..schemas import DatasetProfile


class DescriptiveStatistics(AnalysisPlugin):
    """Plugin that computes descriptive statistics for numeric columns.

    Validation: The plugin is applicable when the dataset profile
    contains at least one column with `can_average == True`.
    """

    name = "Descriptive Statistics"
    description = "Calculate standard descriptive statistics for numeric columns."

    def validate(self, profile: DatasetProfile) -> bool:
        """Return True if any column in the profile is numeric.

        Args:
            profile: DatasetProfile produced by the profiler.

        Returns:
            bool: True when at least one numeric column exists.
        """
        return any(cp.can_average for cp in profile.column_profiles)

    def execute(self, dataset: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Compute descriptive statistics for every numeric column.

        Handles missing values gracefully and does not crash on empty columns.

        Args:
            dataset: pandas DataFrame with the data to analyse.

        Returns:
            dict: Mapping of column name -> metrics mapping.
        """
        results: Dict[str, Dict[str, Any]] = {}

        numeric_columns = dataset.select_dtypes(include=[np.number]).columns.tolist()

        for col in numeric_columns:
            series = dataset[col]
            non_null = series.dropna()
            count = int(non_null.count())
            missing = int(series.isnull().sum())

            if count == 0:
                metrics = {
                    "count": 0,
                    "missing_values": missing,
                    "mean": None,
                    "median": None,
                    "mode": None,
                    "minimum": None,
                    "maximum": None,
                    "range": None,
                    "variance": None,
                    "std_dev": None,
                    "quartile_1": None,
                    "quartile_3": None,
                    "interquartile_range": None,
                }

                results[col] = metrics
                continue

            mean = float(non_null.mean())
            median = float(non_null.median())

            modes = non_null.mode().dropna().tolist()
            if len(modes) == 0:
                mode_value: Union[None, float, List[float]] = None
            elif len(modes) == 1:
                mode_value = self._to_scalar(modes[0])
            else:
                mode_value = [self._to_scalar(m) for m in modes]

            minimum = float(non_null.min())
            maximum = float(non_null.max())
            value_range = maximum - minimum

            # Use population variance/std (ddof=0) for descriptive measures
            variance = float(non_null.var(ddof=0))
            std_dev = float(non_null.std(ddof=0))

            q1 = float(non_null.quantile(0.25))
            q3 = float(non_null.quantile(0.75))
            iqr = q3 - q1

            metrics = {
                "count": count,
                "missing_values": missing,
                "mean": mean,
                "median": median,
                "mode": mode_value,
                "minimum": minimum,
                "maximum": maximum,
                "range": value_range,
                "variance": variance,
                "std_dev": std_dev,
                "quartile_1": q1,
                "quartile_3": q3,
                "interquartile_range": iqr,
            }

            results[col] = metrics

        return results

    def explain(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
        """Return universal statistical explanations for metrics.

        The explanations are metric-focused and do not reference business logic.
        """
        return {
            "mean": "Represents the arithmetic average of the observations.",
            "median": "Represents the middle value after sorting.",
            "mode": "Represents the most frequently occurring value(s).",
            "variance": "Measures overall variability of the values.",
            "std_dev": "Represents the dispersion of values around the average.",
            "minimum": "The smallest observed value.",
            "maximum": "The largest observed value.",
            "range": "Difference between maximum and minimum values.",
            "quartile_1": "The 25th percentile; lower quartile of the distribution.",
            "quartile_3": "The 75th percentile; upper quartile of the distribution.",
            "interquartile_range": "The difference between the third and first quartiles, representing the spread of the middle 50% of observations.",
            "count": "Number of non-missing observations used for calculations.",
            "missing_values": "Number of missing observations in the column.",
        }

    def observations(self, results: Dict[str, Dict[str, Any]]) -> List[str]:
        """Generate objective observations from statistical results.

        Observations are concise, avoid business interpretation and recommendations.
        """
        obs: List[str] = []

        for col, metrics in results.items():
            count = metrics.get("count")
            missing = metrics.get("missing_values", 0)

            # Missing values observations
            if count == 0:
                obs.append(f"{col}: No non-missing values available for analysis.")
                continue

            if missing == 0:
                obs.append(f"{col}: No missing values detected.")
            else:
                total = count + missing
                if total > 0 and (missing / total) > 0.2:
                    obs.append(f"{col}: Large number of missing values detected.")
                else:
                    obs.append(f"{col}: Some missing values detected.")

            mean = metrics.get("mean")
            median = metrics.get("median")
            std_dev = metrics.get("std_dev")

            # Variability observations (use coefficient of variation when mean is non-zero)
            if mean not in (None, 0) and std_dev is not None:
                cov = abs(std_dev / (abs(mean) + 1e-12))
                if cov < 0.1:
                    obs.append(f"{col}: Values are tightly clustered around the average.")
                elif cov > 1:
                    obs.append(f"{col}: Values show high variability.")

            if mean is not None and median is not None:
                if abs(mean - median) / (abs(mean) + 1e-12) < 0.05:
                    obs.append(f"{col}: Distribution appears symmetric.")
                else:
                    obs.append(f"{col}: Mean differs substantially from median.")

            grouped[col] = obs

        return grouped

