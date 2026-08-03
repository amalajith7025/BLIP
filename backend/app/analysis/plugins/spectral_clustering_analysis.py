"""Spectral Clustering analysis plugin.

Performs spectral clustering using nearest-neighbors affinity.
"""
from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
import pandas as pd
from sklearn.cluster import SpectralClustering

from ..interfaces import AnalysisPlugin
from ..schemas import DatasetProfile


class SpectralClusteringAnalysis(AnalysisPlugin):
    """Plugin that performs Spectral Clustering."""

    name = "Spectral Clustering"
    description = "Performs spectral clustering with nearest-neighbors affinity." 

    def validate(self, profile: DatasetProfile) -> bool:
        numeric_columns = [cp for cp in profile.column_profiles if cp.can_average]
        return len(numeric_columns) >= 2

    def execute(self, dataset: pd.DataFrame) -> Dict[str, Any]:
        results: Dict[str, Any] = {}

        if dataset is None or dataset.empty:
            return results

        numeric_columns = dataset.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_columns) < 2:
            return results

        numeric_frame = dataset[numeric_columns].dropna()
        if numeric_frame.shape[0] < 5:
            return results

        # choose n_neighbors safely based on available samples to avoid
        # kneighbors_graph errors when the default neighbor count is too large
        n_neighbors = max(1, min(10, int(numeric_frame.shape[0]) - 1))
        model = SpectralClustering(n_clusters=3, affinity="nearest_neighbors", n_neighbors=n_neighbors, random_state=42)
        labels = model.fit_predict(numeric_frame.values)

        unique_labels = np.unique(labels)
        cluster_sizes = {int(int_label): int(int(np.sum(labels == int_label))) for int_label in unique_labels}

        results = {
            "samples_used": int(numeric_frame.shape[0]),
            "features": numeric_columns,
            "clusters": int(len(unique_labels)),
            "cluster_sizes": cluster_sizes,
            "affinity": "nearest_neighbors",
        }

        return results

    def explain(self, results: Dict[str, Any]) -> Dict[str, str]:
        return {
            "samples_used": "The number of complete observations used for clustering.",
            "features": "The numeric features included in the clustering analysis.",
            "clusters": "The number of clusters identified by the spectral clustering algorithm.",
            "cluster_sizes": "The number of observations assigned to each cluster.",
            "affinity": "The affinity metric used to build the similarity graph for spectral clustering.",
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

        return {"spectral_clustering": observations}
