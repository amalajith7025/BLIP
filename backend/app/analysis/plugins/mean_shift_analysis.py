"""Mean Shift clustering analysis plugin.

Groups observations using the Mean Shift clustering algorithm.
"""
from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
import pandas as pd
from sklearn.cluster import MeanShift

from ..interfaces import AnalysisPlugin
from ..schemas import DatasetProfile


class MeanShiftAnalysis(AnalysisPlugin):
    """Plugin that performs Mean Shift clustering."""

    name = "Mean Shift Clustering"
    description = "Groups observations into clusters using Mean Shift." 

    def validate(self, profile: DatasetProfile) -> bool:
        """Return True when the dataset contains at least two numeric columns."""
        numeric_columns = [cp for cp in profile.column_profiles if cp.can_average]
        return len(numeric_columns) >= 2

    def execute(self, dataset: pd.DataFrame) -> Dict[str, Any]:
        """Execute Mean Shift clustering on numeric columns."""
        results: Dict[str, Any] = {}

        if dataset is None or dataset.empty:
            return results

        numeric_columns = dataset.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_columns) < 2:
            return results

        numeric_frame = dataset[numeric_columns].dropna()
        if numeric_frame.shape[0] < 5:
            return results

        model = MeanShift()
        model.fit(numeric_frame.values)

        labels = model.labels_
        unique_labels = np.unique(labels)
        cluster_sizes = {int(int_label): int(int(np.sum(labels == int_label))) for int_label in unique_labels}

        results = {
            "samples_used": int(numeric_frame.shape[0]),
            "features": numeric_columns,
            "clusters": int(len(unique_labels)),
            "cluster_sizes": cluster_sizes,
            "cluster_centers": [[float(v) for v in center] for center in model.cluster_centers_],
        }

        return results

    def explain(self, results: Dict[str, Any]) -> Dict[str, str]:
        return {
            "samples_used": "The number of complete observations used for clustering.",
            "features": "The numeric features included in the clustering analysis.",
            "clusters": "The number of clusters identified by the Mean Shift algorithm.",
            "cluster_sizes": "The number of observations assigned to each cluster.",
            "cluster_centers": "The coordinates of each cluster center in feature space.",
        }

    def observations(self, results: Dict[str, Any]) -> Dict[str, List[str]]:
        if not results:
            return {"": ["Very small dataset used."]}

        observations: List[str] = []
        samples_used = results.get("samples_used", 0)
        clusters = results.get("clusters", 0)
        cluster_sizes = list(results.get("cluster_sizes", {}).values())

        if samples_used < 5:
            observations.append("Very small dataset used.")

        if clusters > 1:
            observations.append("Multiple clusters identified.")

        if cluster_sizes:
            max_size = max(cluster_sizes)
            min_size = min(cluster_sizes)
            if min_size > 0 and max_size <= 2 * min_size:
                observations.append("Cluster sizes are relatively balanced.")
            if max_size >= 0.6 * samples_used:
                observations.append("One cluster dominates the dataset.")

        return {"mean_shift": observations}
