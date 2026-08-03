"""Independent Component Analysis plugin.

Performs FastICA decomposition.
"""
from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
import pandas as pd
from sklearn.decomposition import FastICA
from sklearn.preprocessing import StandardScaler

from ..interfaces import AnalysisPlugin
from ..schemas import DatasetProfile


class IndependentComponentAnalysis(AnalysisPlugin):
    """Plugin that performs Independent Component Analysis (FastICA)."""

    name = "Independent Component Analysis"
    description = "Performs Independent Component Analysis using FastICA." 

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

        scaler = StandardScaler()
        scaled = scaler.fit_transform(numeric_frame.values)

        n_components = min(2, len(numeric_columns))
        model = FastICA(n_components=n_components, random_state=42, max_iter=200)
        transformed = model.fit_transform(scaled)

        # mixing_ shape: (n_features, n_components)
        mixing = getattr(model, "mixing_")
        mixing_matrix = {}
        for idx, feature in enumerate(numeric_columns):
            mixing_matrix[feature] = [float(x) for x in mixing[idx].tolist()]

        iterations = int(getattr(model, "n_iter_", 0))
        max_iter = int(getattr(model, "max_iter", 200))
        converged = iterations < max_iter

        results = {
            "samples_used": int(numeric_frame.shape[0]),
            "features": numeric_columns,
            "components": int(n_components),
            "mixing_matrix": mixing_matrix,
            "iterations": iterations,
            "converged": bool(converged),
        }

        return results

    def explain(self, results: Dict[str, Any]) -> Dict[str, str]:
        return {
            "samples_used": "The number of observations used after dropping missing values.",
            "features": "Numeric features included in the analysis.",
            "components": "The number of independent components extracted.",
            "mixing_matrix": "The estimated mixing matrix mapping components to observed features.",
            "iterations": "The number of iterations taken during fitting.",
            "converged": "Whether the FastICA algorithm converged within the maximum iterations.",
        }

    def observations(self, results: Dict[str, Any]) -> Dict[str, List[str]]:
        if not results:
            return {"": ["Very small dataset used."]}

        observations: List[str] = []
        samples_used = results.get("samples_used", 0)
        components = results.get("components", 0)

        if samples_used < 5:
            observations.append("Very small dataset used.")

        if components > 1:
            observations.append("Multiple independent components identified.")

        if not results.get("converged", True):
            observations.append("Model did not converge within the iteration limit.")

        return {"ica": observations}
