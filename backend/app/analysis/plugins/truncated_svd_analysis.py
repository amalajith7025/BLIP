"""Truncated SVD dimensionality reduction plugin.

Performs Truncated SVD on numeric variables.
"""
from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import StandardScaler

from ..interfaces import AnalysisPlugin
from ..schemas import DatasetProfile


class TruncatedSVDAnalysis(AnalysisPlugin):
    """Plugin that performs Truncated SVD."""

    name = "Truncated SVD"
    description = "Performs Truncated SVD for dimensionality reduction." 

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
        model = TruncatedSVD(n_components=n_components, random_state=42)
        model.fit(scaled)

        explained_variance_ratio = [float(x) for x in getattr(model, "explained_variance_ratio_", [])]
        singular_values = [float(x) for x in getattr(model, "singular_values_", [])]

        results = {
            "samples_used": int(numeric_frame.shape[0]),
            "features": numeric_columns,
            "components": int(n_components),
            "explained_variance_ratio": explained_variance_ratio,
            "singular_values": singular_values,
        }

        return results

    def explain(self, results: Dict[str, Any]) -> Dict[str, str]:
        return {
            "samples_used": "The number of observations used after dropping missing values.",
            "features": "Numeric features included in the analysis.",
            "components": "Number of singular vectors computed.",
            "explained_variance_ratio": "Proportion of variance explained by each component.",
            "singular_values": "Singular values corresponding to each computed component.",
        }

    def observations(self, results: Dict[str, Any]) -> Dict[str, List[str]]:
        if not results:
            return {"": ["Very small dataset used."]}

        observations: List[str] = []
        samples_used = results.get("samples_used", 0)
        evr = results.get("explained_variance_ratio", [])

        if samples_used < 5:
            observations.append("Very small dataset used.")

        if evr:
            if evr[0] >= 0.7:
                observations.append("The first component explains most of the variance.")
            elif evr[0] < 0.4:
                observations.append("No dominant component is present.")
            else:
                observations.append("Variance is distributed across components.")

        return {"truncated_svd": observations}
