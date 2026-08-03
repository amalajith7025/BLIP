"""Outlier detection analysis plugin.

Detects statistical outliers for numeric columns using IQR and Z-score methods.
"""
from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
import pandas as pd

from ..interfaces import AnalysisPlugin
from ..schemas import DatasetProfile


class OutlierDetection(AnalysisPlugin):
    """Plugin that detects outliers in numeric columns.

    Validation: applicable when the dataset contains at least one numeric column.
    """

    name = "Outlier Detection"
    description = "Detect outliers using IQR and Z-score methods for numeric columns."

    def validate(self, profile: DatasetProfile) -> bool:
        """Return True when at least one numeric column exists.

        Args:
            profile: DatasetProfile produced by the profiler.

        Returns:
            bool: True when at least one numeric column can be averaged.
        """
        return any(cp.can_average for cp in profile.column_profiles)

    def execute(self, dataset: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Compute outlier detection metrics for numeric columns.

        Returns raw IQR and Z-score results only.
        """
        results: Dict[str, Dict[str, Any]] = {}

        numeric_columns = dataset.select_dtypes(include=[np.number]).columns.tolist()

        for column in numeric_columns:
            series = dataset[column]
            non_null = series.dropna()
            values = non_null.to_numpy(dtype=float)
            iqr_result: Dict[str, Any] = {
                "q1": None,
                "q3": None,
                "iqr": None,
                "lower_bound": None,
                "upper_bound": None,
                "outlier_count": 0,
                "outlier_indices": [],
            }
            z_score_result: Dict[str, Any] = {
                "threshold": 3,
                "outlier_count": 0,
                "outlier_indices": [],
            }

            if values.size > 0:
                q1 = float(np.quantile(values, 0.25))
                q3 = float(np.quantile(values, 0.75))
                iqr_value = float(q3 - q1)
                lower_bound = float(q1 - 1.5 * iqr_value)
                upper_bound = float(q3 + 1.5 * iqr_value)

                iqr_indices: List[int] = []
                for index, value in zip(non_null.index.tolist(), values):
                    if value < lower_bound or value > upper_bound:
                        iqr_indices.append(int(index))

                iqr_result = {
                    "q1": q1,
                    "q3": q3,
                    "iqr": iqr_value,
                    "lower_bound": lower_bound,
                    "upper_bound": upper_bound,
                    "outlier_count": len(iqr_indices),
                    "outlier_indices": iqr_indices,
                }

                mean = float(np.mean(values))
                std_dev = float(np.std(values, ddof=0))
                z_indices: List[int] = []

                if std_dev > 0 and values.size >= 1:
                    z_scores = np.abs((values - mean) / std_dev)
                    for index, z_score in zip(non_null.index.tolist(), z_scores):
                        if z_score > 3:
                            z_indices.append(int(index))

                z_score_result = {
                    "threshold": 3,
                    "outlier_count": len(z_indices),
                    "outlier_indices": z_indices,
                }

            results[column] = {
                "iqr": iqr_result,
                "z_score": z_score_result,
            }

        return results

    def explain(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
        """Return universal explanations for outlier detection metrics."""
        return {
            "iqr": "Interquartile range used to detect values far from the central distribution.",
            "q1": "The 25th percentile of the non-missing values.",
            "q3": "The 75th percentile of the non-missing values.",
            "lower_bound": "The lower threshold for IQR-based outliers.",
            "upper_bound": "The upper threshold for IQR-based outliers.",
            "z_score": "The standardized score measuring distance from the mean in units of standard deviation.",
            "threshold": "The Z-score cutoff used to identify extreme values.",
            "outlier_count": "The number of observations identified as outliers.",
            "outlier_indices": "The row indices of observations identified as outliers.",
        }

    def observations(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
        """Generate objective observations for outlier detection results."""
        grouped: Dict[str, List[str]] = {}

        for column, metrics in results.items():
            col_obs: List[str] = []
            iqr_metrics = metrics.get("iqr", {})
            z_metrics = metrics.get("z_score", {})
            iqr_count = iqr_metrics.get("outlier_count", 0)
            z_count = z_metrics.get("outlier_count", 0)
            q1 = iqr_metrics.get("q1")
            q3 = iqr_metrics.get("q3")

            if q1 is None or q3 is None:
                col_obs.append("Insufficient observations for outlier detection.")
            else:
                if iqr_count > 0:
                    col_obs.append("Outliers detected using the IQR method.")
                if z_count > 0:
                    col_obs.append("Outliers detected using the Z-score method.")
                if iqr_count > 0 and z_count > 0:
                    col_obs.append("Multiple outlier detection methods identified extreme observations.")
                if iqr_count == 0 and z_count == 0:
                    col_obs.append("No outliers detected.")

            grouped[column] = col_obs

        return grouped
