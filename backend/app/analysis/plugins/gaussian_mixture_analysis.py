"""Gaussian Mixture Model analysis plugin.

Groups observations into probabilistic clusters using Gaussian Mixture Models.
"""
from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
import pandas as pd
from sklearn.mixture import GaussianMixture

from ..interfaces import AnalysisPlugin
from ..schemas import DatasetProfile


class GaussianMixtureAnalysis(AnalysisPlugin):
    """Plugin that performs Gaussian Mixture clustering analysis."""

    name = "Gaussian Mixture Model"
    description = (
        "Groups observations into probabilistic clusters using Gaussian Mixture Models."
    )

    def validate(self, profile: DatasetProfile) -> bool:
        """Return True when the dataset contains at least two numeric columns."""
        numeric_columns = [cp for cp in profile.column_profiles if cp.can_average]
        return len(numeric_columns) >= 2

    def execute(self, dataset: pd.DataFrame) -> Dict[str, Any]:
        """Execute Gaussian Mixture clustering on numeric columns."""
        results: Dict[str, Any] = {}

        if dataset is None or dataset.empty:
            return results

        numeric_columns = dataset.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_columns) < 2:
            return results

        numeric_frame = dataset[numeric_columns].dropna()
        if numeric_frame.shape[0] < 2:
            return results

        model = GaussianMixture(
            n_components=3,
            random_state=42,
        )
        model.fit(numeric_frame.values)

        labels = model.predict(numeric_frame.values)
        component_sizes = {
            f"Component {i}": int(np.sum(labels == i))
            for i in range(model.n_components)
        }

        results = {
            "samples_used": int(numeric_frame.shape[0]),
            "features_used": numeric_columns,
            "component_count": int(model.n_components),
            "component_sizes": component_sizes,
            "weights": [float(value) for value in model.weights_],
            "means": [
                [float(value) for value in row]
                for row in model.means_
            ],
            "converged": bool(model.converged_),
            "iterations": int(model.n_iter_),
        }

        return results

    def explain(self, results: Dict[str, Any]) -> Dict[str, str]:
        """Return standardized explanations for Gaussian Mixture output keys."""
        return {
            "samples_used": "The number of complete observations used for Gaussian Mixture modeling.",
            "features_used": "The numeric features included in the Gaussian Mixture analysis.",
            "component_count": "The number of Gaussian mixture components modeled.",
            "component_sizes": "The number of observations assigned to each mixture component.",
            "weights": "The mixture weights for each Gaussian component.",
            "means": "The mean coordinates of each Gaussian component in feature space.",
            "converged": "Whether the Gaussian Mixture model converged successfully.",
            "iterations": "The number of iterations the Gaussian Mixture model required.",
        }

    def observations(self, results: Dict[str, Any]) -> Dict[str, List[str]]:
        """Generate objective observations from Gaussian Mixture results."""
        if not results:
            return {"": ["Very small dataset used."]}

        samples_used = results.get("samples_used", 0)
        component_count = results.get("component_count", 0)
        component_sizes = results.get("component_sizes", {})
        iterations = results.get("iterations", 0)

        mixture_observations: List[str] = []

        if samples_used < 5:
            mixture_observations.append("Very small dataset used.")

        if component_count > 1:
            mixture_observations.append("Components are relatively balanced.")

        size_values = list(component_sizes.values())
        if size_values:
            max_size = max(size_values)
            min_size = min(size_values)
            if min_size > 0 and max_size <= 2 * min_size:
                mixture_observations.append("Components are relatively balanced.")
            if max_size >= 0.6 * samples_used:
                mixture_observations.append("One component dominates the dataset.")

        if iterations > 1:
            mixture_observations.append("Model required multiple iterations.")

        if results.get("converged", False):
            mixture_observations.append("Model converged successfully.")

        return {"gaussian_mixture": mixture_observations}
