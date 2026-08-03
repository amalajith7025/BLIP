"""DBSCAN clustering analysis plugin.

Groups observations into density-based clusters and identifies noise points.
"""
from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN

from ..interfaces import AnalysisPlugin
from ..schemas import DatasetProfile


class DBSCANAnalysis(AnalysisPlugin):
    """Plugin that performs DBSCAN clustering analysis."""

    name = "DBSCAN Clustering"
    description = (
        "Groups observations into density-based clusters and identifies noise points."
    )

    def validate(self, profile: DatasetProfile) -> bool:
        """Return True when the dataset contains at least two numeric columns."""
        numeric_columns = [cp for cp in profile.column_profiles if cp.can_average]
        return len(numeric_columns) >= 2

    def execute(self, dataset: pd.DataFrame) -> Dict[str, Any]:
        """Execute DBSCAN clustering on numeric columns."""
        results: Dict[str, Any] = {}

        if dataset is None or dataset.empty:
            return results

        numeric_columns = dataset.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_columns) < 2:
            return results

        numeric_frame = dataset[numeric_columns].dropna()
        if numeric_frame.shape[0] < 2:
            return results

        model = DBSCAN(eps=0.5, min_samples=5)
        labels = model.fit_predict(numeric_frame.values)

        noise_points = int(np.sum(labels == -1))
        cluster_labels = sorted({int(label) for label in labels if label >= 0})

        cluster_sizes = {
            f"Cluster {label}": int(np.sum(labels == label))
            for label in cluster_labels
        }

        results = {
            "samples_used": int(numeric_frame.shape[0]),
            "features_used": numeric_columns,
            "cluster_count": int(len(cluster_labels)),
            "noise_points": noise_points,
            "cluster_sizes": cluster_sizes,
        }

        return results

    def explain(self, results: Dict[str, Any]) -> Dict[str, str]:
        """Return standardized explanations for DBSCAN output keys."""
        return {
            "samples_used": "The number of complete observations used for DBSCAN clustering.",
            "features_used": "The numeric features included in the DBSCAN analysis.",
            "cluster_count": "The number of density-based clusters identified by DBSCAN.",
            "noise_points": "The number of observations classified as noise by DBSCAN.",
            "cluster_sizes": "The number of observations assigned to each identified cluster.",
        }

    def observations(self, results: Dict[str, Any]) -> Dict[str, List[str]]:
        """Generate objective observations from DBSCAN results."""
        if not results:
            return {"": ["No clusters detected."]}

        samples_used = results.get("samples_used", 0)
        cluster_count = results.get("cluster_count", 0)
        noise_points = results.get("noise_points", 0)
        cluster_sizes = results.get("cluster_sizes", {})

        dbscan_observations: List[str] = []

        if cluster_count == 0:
            dbscan_observations.append("No clusters detected.")
        if cluster_count > 1:
            dbscan_observations.append("Multiple clusters identified.")
        if noise_points > 0:
            dbscan_observations.append("Noise points detected.")
        if samples_used > 0 and noise_points >= 0.3 * samples_used:
            dbscan_observations.append("Large proportion of observations classified as noise.")

        size_values = list(cluster_sizes.values())
        if size_values:
            max_size = max(size_values)
            min_size = min(size_values)
            if min_size > 0 and max_size <= 2 * min_size:
                dbscan_observations.append("Cluster sizes are relatively balanced.")
            if max_size >= 0.6 * samples_used:
                dbscan_observations.append("One cluster dominates the dataset.")

        return {"dbscan": dbscan_observations}
