"""Factor Analysis plugin.

Performs Factor Analysis dimensionality reduction.
"""
from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
import pandas as pd
from sklearn.decomposition import FactorAnalysis
from sklearn.preprocessing import StandardScaler

from ..interfaces import AnalysisPlugin
from ..schemas import DatasetProfile


class FactorAnalysisPlugin(AnalysisPlugin):
    """Plugin that performs Factor Analysis."""

    name = "Factor Analysis"
    description = "Performs Factor Analysis for dimensionality reduction." 

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
        model = FactorAnalysis(n_components=n_components, random_state=42)
        model.fit(scaled)

        # loadings: components_ shape (n_components, n_features)
        loadings = {}
        for idx, feature in enumerate(numeric_columns):
            vals = [float(x) for x in model.components_[:, idx].tolist()]
            loadings[feature] = vals

        noise_variance = [float(x) for x in getattr(model, "noise_variance_")]

        results = {
            "samples_used": int(numeric_frame.shape[0]),
            "features": numeric_columns,
            "components": int(model.n_components),
            "loadings": loadings,
            "noise_variance": noise_variance,
        }

        return results

    def explain(self, results: Dict[str, Any]) -> Dict[str, str]:
        return {
            "samples_used": "The number of observations used after dropping missing values.",
            "features": "Numeric features included in the analysis.",
            "components": "Number of latent factors fitted by Factor Analysis.",
            "loadings": "The factor loadings for each feature across components.",
            "noise_variance": "Estimated noise variance for each feature.",
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
            observations.append("Multiple latent factors identified.")

        return {"factor_analysis": observations}
