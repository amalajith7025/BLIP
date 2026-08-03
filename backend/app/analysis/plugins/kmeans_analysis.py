"""K-Means clustering analysis plugin.

Groups similar observations into clusters using the K-Means clustering algorithm.
"""
from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

from ..interfaces import AnalysisPlugin
from ..schemas import DatasetProfile


class KMeansAnalysis(AnalysisPlugin):
    """Plugin that performs K-Means clustering."""

    name = "K-Means Clustering"
    description = (
        "Groups similar observations into clusters using the K-Means clustering algorithm."
    )

    def validate(self, profile: DatasetProfile) -> bool:
        """Return True when the dataset contains at least two numeric columns."""
        numeric_columns = [cp for cp in profile.column_profiles if cp.can_average]
        return len(numeric_columns) >= 2

    def execute(self, dataset: pd.DataFrame) -> Dict[str, Any]:
        """Execute K-Means clustering on numeric columns."""
        results: Dict[str, Any] = {}

        if dataset is None or dataset.empty:
            return results

        numeric_columns = dataset.select_dtypes(include=[np.number]).columns.tolist()

        if len(numeric_columns) < 2:
            return results

        numeric_frame = dataset[numeric_columns].dropna()

        if numeric_frame.shape[0] < 2:
            return results

        model = KMeans(
            n_clusters=3,
            random_state=42,
            n_init="auto",
        )
        model.fit(numeric_frame.values)

        labels = model.labels_
        cluster_sizes = {
            f"Cluster {i}": int(np.sum(labels == i))
            for i in range(model.n_clusters)
        }

        results = {
            "samples_used": int(numeric_frame.shape[0]),
            "features_used": numeric_columns,
            "cluster_count": int(model.n_clusters),
            "cluster_sizes": cluster_sizes,
            "inertia": float(model.inertia_),
            "cluster_centers": [
                [float(value) for value in center]
                for center in model.cluster_centers_
            ],
        }

        return results

    def explain(self, results: Dict[str, Any]) -> Dict[str, str]:
        """Return standardized explanations for K-Means output keys."""
        return {
            "cluster_count": "The number of clusters used by the K-Means algorithm.",
            "cluster_sizes": "The number of observations assigned to each cluster.",
            "inertia": "The sum of squared distances of samples to their nearest cluster center.",
            "cluster_centers": "The coordinates of each cluster center in feature space.",
            "samples_used": "The number of complete observations used for clustering.",
            "features_used": "The numeric features included in the clustering analysis.",
        }

    def observations(self, results: Dict[str, Any]) -> Dict[str, List[str]]:
        """Generate objective observations from K-Means results."""
        if not results:
            return {"": ["Very small dataset used."]}

        observations: Dict[str, List[str]] = {}
        cluster_sizes = results.get("cluster_sizes", {})
        samples_used = results.get("samples_used", 0)
        inertia = results.get("inertia", 0.0)

        cluster_observations: List[str] = []

        if samples_used < 5:
            cluster_observations.append("Very small dataset used.")

        if results.get("cluster_count", 0) > 1:
            cluster_observations.append("Multiple clusters identified.")

        size_values = list(cluster_sizes.values())
        if size_values:
            max_size = max(size_values)
            min_size = min(size_values)
            if min_size > 0 and max_size <= 2 * min_size:
                cluster_observations.append("Cluster sizes are relatively balanced.")
            if max_size >= 0.6 * samples_used:
                cluster_observations.append("One cluster dominates the dataset.")

        if inertia <= samples_used:
            cluster_observations.append("Low within-cluster variation observed.")
        else:
            cluster_observations.append("High within-cluster variation observed.")

        observations["kmeans"] = cluster_observations
        return observations
