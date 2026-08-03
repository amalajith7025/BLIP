"""Hierarchical Clustering analysis plugin.

Groups similar observations using agglomerative hierarchical clustering.
"""
from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
import pandas as pd
from sklearn.cluster import AgglomerativeClustering

from ..interfaces import AnalysisPlugin
from ..schemas import DatasetProfile


class HierarchicalClusteringAnalysis(AnalysisPlugin):
    """Plugin that performs hierarchical clustering analysis."""

    name = "Hierarchical Clustering"
    description = (
        "Groups similar observations using agglomerative hierarchical clustering."
    )

    def validate(self, profile: DatasetProfile) -> bool:
        """Return True when the dataset contains at least two numeric columns."""
        numeric_columns = [cp for cp in profile.column_profiles if cp.can_average]
        return len(numeric_columns) >= 2

    def execute(self, dataset: pd.DataFrame) -> Dict[str, Any]:
        """Execute hierarchical clustering on numeric columns."""
        results: Dict[str, Any] = {}

        if dataset is None or dataset.empty:
            return results

        numeric_columns = dataset.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_columns) < 2:
            return results

        numeric_frame = dataset[numeric_columns].dropna()
        if numeric_frame.shape[0] < 2:
            return results

        model = AgglomerativeClustering(n_clusters=3)
        labels = model.fit_predict(numeric_frame.values)

        cluster_sizes = {
            f"Cluster {i}": int(np.sum(labels == i))
            for i in range(model.n_clusters)
        }

        results = {
            "samples_used": int(numeric_frame.shape[0]),
            "features_used": numeric_columns,
            "cluster_count": int(model.n_clusters),
            "cluster_sizes": cluster_sizes,
        }

        return results

    def explain(self, results: Dict[str, Any]) -> Dict[str, str]:
        """Return standardized explanations for hierarchical clustering output keys."""
        return {
            "samples_used": "The number of complete observations used for clustering.",
            "features_used": "The numeric features included in the hierarchical clustering analysis.",
            "cluster_count": "The number of clusters identified by the hierarchical clustering algorithm.",
            "cluster_sizes": "The number of observations assigned to each cluster.",
        }

    def observations(self, results: Dict[str, Any]) -> Dict[str, List[str]]:
        """Generate objective observations from hierarchical clustering results."""
        if not results:
            return {"": ["Very small dataset used."]}

        samples_used = results.get("samples_used", 0)
        cluster_sizes = results.get("cluster_sizes", {})
        cluster_count = results.get("cluster_count", 0)

        cluster_observations: List[str] = []

        if samples_used < 5:
            cluster_observations.append("Very small dataset used.")

        if cluster_count > 1:
            cluster_observations.append("Multiple clusters identified.")

        size_values = list(cluster_sizes.values())
        if size_values:
            max_size = max(size_values)
            min_size = min(size_values)
            if min_size > 0 and max_size <= 2 * min_size:
                cluster_observations.append("Cluster sizes are relatively balanced.")
            if max_size >= 0.6 * samples_used:
                cluster_observations.append("One cluster dominates the dataset.")

        return {"hierarchical_clustering": cluster_observations}
