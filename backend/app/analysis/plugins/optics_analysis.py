"""OPTICS clustering analysis plugin.

Performs OPTICS clustering and reports ordering and reachability availability.
"""
from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
import pandas as pd
from sklearn.cluster import OPTICS

from ..interfaces import AnalysisPlugin
from ..schemas import DatasetProfile


class OPTICSAnalysis(AnalysisPlugin):
    """Plugin that performs OPTICS clustering."""

    name = "OPTICS Clustering"
    description = "Performs OPTICS clustering and reports ordering and reachability." 

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

        model = OPTICS(min_samples=5)
        model.fit(numeric_frame.values)

        labels = model.labels_

        # identify non-noise clusters and remap to contiguous 0..k-1
        unique_labels = np.unique(labels)
        non_noise = [int(l) for l in unique_labels if int(l) >= 0]
        non_noise.sort()
        remap = {orig: idx for idx, orig in enumerate(non_noise)}

        cluster_sizes = {
            int(remap[lab]): int(np.sum(labels == lab))
            for lab in non_noise
        }

        ordering = [int(i) for i in getattr(model, "ordering_")] if hasattr(model, "ordering_") else []
        reachability = getattr(model, "reachability_", None)
        reachability_available = False
        if reachability is not None:
            reachability_available = bool(np.any(np.isfinite(reachability)))

        results = {
            "samples_used": int(numeric_frame.shape[0]),
            "features": numeric_columns,
            "clusters": int(len(non_noise)),
            "cluster_sizes": cluster_sizes,
            "ordering": ordering,
            "reachability_available": bool(reachability_available),
        }

        return results

    def explain(self, results: Dict[str, Any]) -> Dict[str, str]:
        return {
            "samples_used": "The number of complete observations used for clustering.",
            "features": "The numeric features included in the clustering analysis.",
            "clusters": "The number of clusters identified by OPTICS (excluding noise).",
            "cluster_sizes": "The number of observations assigned to each cluster.",
            "ordering": "The ordering of samples produced by OPTICS.",
            "reachability_available": "Whether reachability distances were computed and are available.",
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

        return {"optics": observations}
